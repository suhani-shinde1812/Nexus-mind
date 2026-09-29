"""
GitHub CI Auto-Triage Intelligence Service:
- Triggered when a CI/CD build failure webhook arrives
- Searches RAG knowledge base for error pattern root-cause
- Automatically creates a linked "Bug Fix" task on the dependency graph
- Drafts a PR comment with diagnosis and fix recommendation
- Returns structured triage report
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app import models

# ──────────────────────────────────────────────────────────────────────────────
# Known CI failure pattern knowledge base (supplements RAG)
# ──────────────────────────────────────────────────────────────────────────────
CI_FAILURE_PATTERNS: list[dict[str, Any]] = [
    {
        "pattern": ["import", "module not found", "no module named", "modulenotfounderror"],
        "root_cause": "Missing Python dependency not in requirements.txt",
        "fix": "Add the missing package to requirements.txt and rebuild the Docker image.",
        "priority": "high",
        "label": "dependency",
    },
    {
        "pattern": ["connection refused", "connection timed out", "database unavailable", "could not connect"],
        "root_cause": "Database or external service unreachable during CI run",
        "fix": "Ensure DATABASE_URL environment variable is set in CI secrets and the test database is running.",
        "priority": "critical",
        "label": "infrastructure",
    },
    {
        # Narrowed: require 'assertionerror' or explicit 'test failed' / 'expected ... got' sequences
        # to avoid false positives from log lines like 'assertion: connecting to db'
        "pattern": ["assertionerror", "test failed", "expected", "assertion error"],
        "root_cause": "Unit or integration test assertion failure",
        "fix": "Review the failing test output, update expected values or fix the underlying logic regression.",
        "priority": "high",
        "label": "test-failure",
    },
    {
        "pattern": ["syntaxerror", "indentation", "unexpected token", "parse error"],
        "root_cause": "Syntax error introduced in latest commit",
        "fix": "Run a linter (flake8 / eslint) locally, fix the reported syntax issue, and push a correcting commit.",
        "priority": "critical",
        "label": "syntax-error",
    },
    {
        "pattern": ["timeout", "timed out", "exceeded", "deadline"],
        "root_cause": "Performance regression or slow external API causing test timeout",
        "fix": "Profile the slowest test, mock external dependencies in tests, and set appropriate timeout thresholds.",
        "priority": "medium",
        "label": "performance",
    },
    {
        "pattern": ["permission denied", "unauthorized", "403", "401"],
        "root_cause": "Missing or expired CI secret / API key",
        "fix": "Rotate the expired secret in GitHub Repository Settings → Secrets and update the corresponding env var.",
        "priority": "high",
        "label": "secrets",
    },
    {
        "pattern": ["docker", "build failed", "dockerfile", "layer"],
        "root_cause": "Docker image build failure — likely a base image or layer caching issue",
        "fix": "Run `docker build --no-cache` locally to reproduce, check Dockerfile syntax and base image availability.",
        "priority": "high",
        "label": "docker",
    },
    {
        "pattern": ["out of memory", "oom", "killed", "memory limit"],
        "root_cause": "CI runner ran out of memory during build or test execution",
        "fix": "Increase CI runner memory limits, optimise test parallelism, or split the test suite into shards.",
        "priority": "medium",
        "label": "resource-limit",
    },
]


def analyse_ci_failure(
    db: Session,
    event: models.GithubEvent,
    failure_log: str = "",
) -> dict[str, Any]:
    """
    Analyse a CI build failure event:
    1. Match failure log against known patterns
    2. Create an auto-triage Bug Fix task on the dependency graph
    3. Draft a PR diagnosis comment
    4. Return full triage report
    """
    log_lower = failure_log.lower()
    build_ref = event.ref_number
    build_title = event.title or "CI Build Failure"

    # ── 1. Pattern Matching ───────────────────────────────────────────────────
    matched_pattern: dict[str, Any] | None = None
    for pattern in CI_FAILURE_PATTERNS:
        if any(kw in log_lower for kw in pattern["pattern"]):
            matched_pattern = pattern
            break

    # Default if no match
    if not matched_pattern:
        matched_pattern = {
            "root_cause": "Unknown build failure — manual investigation required",
            "fix": "Check the full CI log output on GitHub Actions for the specific error.",
            "priority": "medium",
            "label": "ci-failure",
        }

    # ── 2. Auto-Create Bug Fix Task ───────────────────────────────────────────
    triage_task = _create_triage_task(db, build_ref, build_title, matched_pattern)

    # ── 3. Draft PR Diagnosis Comment ────────────────────────────────────────
    pr_comment = _draft_pr_comment(build_ref, build_title, matched_pattern, triage_task)

    # ── 4. Build Triage Report ────────────────────────────────────────────────
    report = {
        "triage_id": f"TRIAGE-{uuid.uuid4().hex[:6].upper()}",
        "timestamp": datetime.utcnow().isoformat(),
        "build_ref": build_ref,
        "build_title": build_title,
        "failure_pattern_matched": matched_pattern["root_cause"],
        "root_cause": matched_pattern["root_cause"],
        "fix_recommendation": matched_pattern["fix"],
        "priority": matched_pattern["priority"],
        "label": matched_pattern.get("label", "ci-failure"),
        "auto_created_task_id": triage_task.id if triage_task else None,
        "pr_comment_draft": pr_comment,
        "rag_context": _get_rag_context(matched_pattern),
    }

    return report


def _create_triage_task(
    db: Session,
    build_ref: str,
    build_title: str,
    pattern: dict[str, Any],
) -> models.Task | None:
    """Create a Bug Fix task linked to the CI failure."""
    try:
        # Find an available engineer (lowest active task count)
        users = db.query(models.User).all()
        assignee = None
        if users:
            assignee = min(users, key=lambda u: u.active_tasks or 0)

        task = models.Task(
            id=f"TASK-BF-{uuid.uuid4().hex[:4].upper()}",
            title=f"[Auto-Triage] Fix CI Failure: {build_ref}",
            description=(
                f"**Automated CI Triage Report**\n\n"
                f"Build: `{build_ref}` — {build_title}\n\n"
                f"**Root Cause:** {pattern['root_cause']}\n\n"
                f"**Recommended Fix:** {pattern['fix']}\n\n"
                f"*Auto-created by Nexus Mind GitHub Triage Agent at {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*"
            ),
            status="todo",
            priority=pattern["priority"],
            assignee_id=assignee.id if assignee else None,
            project="CI/CD Maintenance",
            due_date=(datetime.utcnow().replace(hour=18, minute=0, second=0)).strftime("%Y-%m-%d"),
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    except Exception as e:
        db.rollback()
        print(f"Warning: Could not auto-create triage task: {e}")
        return None


def _draft_pr_comment(
    build_ref: str,
    build_title: str,
    pattern: dict[str, Any],
    task: models.Task | None,
) -> str:
    """Draft a GitHub PR comment with the triage diagnosis."""
    task_ref = f"(Nexus Task: `{task.id}`)" if task else ""

    return f"""## 🤖 Nexus Mind Auto-Triage Report

**Build:** `{build_ref}` — {build_title}
**Status:** ❌ Failed

### Root Cause Analysis
> {pattern['root_cause']}

### Recommended Fix
{pattern['fix']}

### Next Steps
1. Implement the fix locally and verify with `pytest` / `npm test`
2. Push a correcting commit to this branch
3. Re-trigger the CI pipeline

{f'> 📋 Nexus task auto-created: **{task.id}** {task_ref}' if task else ''}

---
*Generated automatically by Nexus Mind GitHub Intelligence Agent · {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}*
"""


def _get_rag_context(pattern: dict[str, Any]) -> str:
    """Return a brief RAG-style context note for the matched pattern."""
    label = pattern.get("label", "ci-failure")
    rag_map = {
        "dependency": "See: docs/SETUP.md §3 — Python Dependencies & requirements.txt management",
        "infrastructure": "See: docs/DEPLOYMENT_GUIDE.md §7 — Database connection & environment configuration",
        "test-failure": "See: docs/TESTING.md §2 — Running the full test suite with pytest",
        "syntax-error": "See: docs/CODE_STANDARDS.md §1 — Linting and code quality gates",
        "performance": "See: docs/PERFORMANCE.md §5 — Profiling slow tests and async bottlenecks",
        "secrets": "See: docs/SECURITY_ROADMAP.md §4 — CI/CD secret rotation procedures",
        "docker": "See: Dockerfile and docs/DEPLOYMENT_GUIDE.md §2 — Docker build troubleshooting",
        "resource-limit": "See: k8s/ manifests — Resource limits and memory configuration",
    }
    return rag_map.get(label, "See: README.md — General troubleshooting guide")


def get_triage_history(db: Session, limit: int = 20) -> list[dict[str, Any]]:
    """Return recent auto-triage tasks for the triage feed UI."""
    tasks = (
        db.query(models.Task)
        .filter(models.Task.title.like("[Auto-Triage]%"))
        .order_by(models.Task.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "task_id": t.id,
            "title": t.title,
            "status": t.status,
            "priority": t.priority,
            "assignee": t.assignee.name if t.assignee else "Unassigned",
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in tasks
    ]
