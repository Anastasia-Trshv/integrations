from fastapi import Depends, Header, HTTPException, status
from app.core.config import settings


async def api_key_auth(x_api_key: str | None = Header(default=None, alias=settings.api_key_header)):
    if x_api_key != settings.default_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return True


async def internal_auth(x_internal_token: str | None = Header(default=None, alias=settings.internal_token_header)):
    if x_internal_token != settings.internal_token_default:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid internal token")
    return True

