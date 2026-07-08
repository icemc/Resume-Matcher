"""Tenant (language) validation shared by routers.

Each supported language is treated as its own tenant. This module has no
FastAPI ``Depends`` wiring — the codebase has no dependency-injection
precedent, so tenant validation is a plain function called directly from
route handlers, matching the existing style.
"""

from fastapi import HTTPException

from app.routers.config import SUPPORTED_LANGUAGES


def validate_tenant_language(language: str) -> str:
    """Validate a tenant (language) code, raising 400 if unsupported."""
    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language: {language}. Supported: {SUPPORTED_LANGUAGES}",
        )
    return language
