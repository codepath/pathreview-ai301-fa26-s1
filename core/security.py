"""Security utilities for authentication and password handling."""

from datetime import UTC, datetime, timedelta
from typing import Any, cast

from jose import JWTError, jwt
from passlib.context import CryptContext

from core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Bcrypt hashed password
    """
    return str(pwd_context.hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password.

    Verification fails closed: if the stored hash is not something passlib can
    identify or parse, this returns False rather than propagating passlib's
    error to the caller.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Previously hashed password to compare against

    Returns:
        True if password matches, False otherwise (including when
        hashed_password is malformed or unrecognized)
    """
    try:
        return bool(pwd_context.verify(plain_password, hashed_password))
    except ValueError:
        # passlib raises UnknownHashError (a ValueError) when it cannot
        # identify the stored hash, and a bare ValueError from the bcrypt
        # handler when a bcrypt-prefixed hash will not parse. Neither is a
        # successful verification, so fail closed.
        return False


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token.

    Args:
        data: Dictionary of claims to encode in the token
        expires_delta: Optional custom expiration time delta. Defaults to
            access_token_expire_minutes from settings.

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )

    return str(encoded_jwt)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode a JWT access token.

    Args:
        token: JWT token to decode

    Returns:
        Dictionary of decoded claims if valid, None if invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return cast("dict[str, Any]", payload)
    except JWTError:
        return None
