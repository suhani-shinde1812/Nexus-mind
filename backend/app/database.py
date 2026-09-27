"""
SQLAlchemy engine / session setup.
"""
import logging
import socket
from urllib.parse import urlparse, urlunparse

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings

logger = logging.getLogger("nexusmind.database")
settings = get_settings()


def normalize_database_url(url: str) -> str:
    """
    Normalizes PostgreSQL database URLs for cloud deployments (especially Render).
    - Converts 'postgres://' -> 'postgresql://'
    - Detects unresolved Render internal hostnames ('dpg-xxxx-a') and resolves them
      to the active regional endpoint (e.g. 'dpg-xxxx-a.oregon-postgres.render.com')
    - Ensures 'sslmode=require' is present when connecting to Render PostgreSQL
    """
    if not url:
        return url

    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    if url.startswith("sqlite"):
        return url

    try:
        parsed = urlparse(url)
        host = parsed.hostname
        if not host or host in ("localhost", "127.0.0.1"):
            return url

        # 1. Test direct hostname resolution
        try:
            socket.gethostbyname(host)
            # If already resolving and on render, ensure sslmode=require
            if "postgres.render.com" in host or host.startswith("dpg-"):
                query = parsed.query
                if "sslmode" not in query:
                    query = f"{query}&sslmode=require" if query else "sslmode=require"
                    url = urlunparse(parsed._replace(query=query))
            return url
        except socket.gaierror:
            logger.warning(
                f"[Database] Hostname '{host}' could not be resolved directly. "
                "Checking Render regional DNS endpoints..."
            )

        # 2. Host failed to resolve: test known Render regional suffixes
        if host.startswith("dpg-") or "." not in host:
            render_regions = ["oregon", "frankfurt", "ohio", "singapore", "virginia"]
            for region in render_regions:
                candidate_host = f"{host}.{region}-postgres.render.com"
                try:
                    ip = socket.gethostbyname(candidate_host)
                    logger.info(
                        f"[Database] Successfully resolved Render database host '{host}' "
                        f"-> '{candidate_host}' ({ip})"
                    )
                    netloc = parsed.netloc.replace(host, candidate_host)
                    query = parsed.query
                    if "sslmode" not in query:
                        query = f"{query}&sslmode=require" if query else "sslmode=require"
                    return urlunparse(parsed._replace(netloc=netloc, query=query))
                except socket.gaierror:
                    continue

        logger.error(
            f"[Database] Could not resolve database host '{host}'. "
            "Please ensure the Web Service and Database are in the same Render region, "
            "or use the External Database URL with sslmode=require."
        )
    except Exception as e:
        logger.warning(f"[Database] Exception during database URL normalization: {e}")

    return url


db_url = normalize_database_url(settings.database_url)

connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(db_url, connect_args=connect_args, future=True)
else:
    engine = create_engine(db_url, pool_pre_ping=True, pool_recycle=300, future=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)



class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

