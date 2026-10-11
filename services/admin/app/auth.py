from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AdminIdentity:
    username: str


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_access_token(subject: str) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    claims = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    }
    return jwt.encode(claims, settings.jwt_secret, algorithm="HS256")


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        get_settings().jwt_secret,
        algorithms=["HS256"],
        options={"verify_exp": False, "require": ["sub"]},
    )


def unauthorized(message: str) -> HTTPException:
    return HTTPException(status_code=401, detail={"code": "unauthorized", "message": message})


def require_admin(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> AdminIdentity:
    if credentials is None:
        raise unauthorized("missing bearer token")
    try:
        claims = decode_token(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise unauthorized("invalid token") from exc
    return AdminIdentity(username=claims["sub"])
