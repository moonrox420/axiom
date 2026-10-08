from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    user_id: str
    email: str
    exp: datetime


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    user_id: str, email: str, expires_delta: timedelta | None = None
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode: dict[str, Any] = {
        "user_id": user_id,
        "email": email,
        "exp": expire,
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        user_id: str = payload.get("user_id")
        email: str = payload.get("email")
        exp: int = payload.get("exp")
        
        if user_id is None or email is None:
            raise JWTError("Invalid token")
        
        return TokenData(user_id=user_id, email=email, exp=datetime.fromtimestamp(exp, tz=timezone.utc))
    except JWTError as exc:
        raise JWTError("Could not validate credentials") from exc