"""
RAG Knowledge Documents Router:
- Upload documents (PDF, Markdown, Plain Text)
- Chunking & pgvector/semantic embedding pipeline
- Semantic search & LLM synthesis with exact citations
"""
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user, log_audit_event
from app.services import rag_service

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("", response_model=list[schemas.DocumentOut])
def list_documents(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    query = db.query(models.Document)
    if current_user.org_id:
        query = query.filter(models.Document.org_id == current_user.org_id)
    docs = query.order_by(models.Document.created_at.desc()).all()
    out = []
    for d in docs:
        out.append(
            schemas.DocumentOut(
                id=d.id,
                title=d.title,
                filename=d.filename,
                file_type=d.file_type,
                file_size_bytes=d.file_size_bytes,
                summary=d.summary,
                created_at=d.created_at,
                chunk_count=len(d.chunks),
            )
        )
    return out


@router.post("/upload", response_model=schemas.DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(None),
    summary: str = Form(""),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    content_bytes = await file.read()
    if not content_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")

    doc_title = title or file.filename.rsplit(".", 1)[0].replace("-", " ").title()
    file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else "txt"

    doc = models.Document(
        org_id=current_user.org_id,
        title=doc_title,
        filename=file.filename,
        file_type=file_ext,
        file_size_bytes=len(content_bytes),
        summary=summary or f"Uploaded document {file.filename}",
        uploaded_by_id=current_user.id,
    )
    db.add(doc)
    db.flush()

    # Chunk and embed
    rag_service.chunk_document_and_embed(db, doc, content_bytes)

    log_audit_event(
        db,
        action="document_uploaded",
        resource_type="document",
        resource_id=doc.id,
        actor=current_user,
        details={"title": doc.title, "filename": doc.filename, "size": len(content_bytes)},
    )

    return schemas.DocumentOut(
        id=doc.id,
        title=doc.title,
        filename=doc.filename,
        file_type=doc.file_type,
        file_size_bytes=doc.file_size_bytes,
        summary=doc.summary,
        created_at=doc.created_at,
        chunk_count=len(doc.chunks),
    )


@router.post("/query", response_model=schemas.RagQueryOut)
def query_knowledge_base(
    payload: schemas.RagQueryIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Execute hybrid RAG query with semantic matching, tenant scoping & source citations."""
    return rag_service.query_rag_knowledge_base(db, payload.query, top_k=payload.top_k, current_user=current_user)
