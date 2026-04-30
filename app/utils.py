import jwt
from datetime import datetime, timedelta, timezone
from app.config import security_settings
from fastapi import status, HTTPException


def generate_access_token(
    data: dict,
    expiry: timedelta = timedelta(days=1),
) -> str:
    return jwt.encode(
        payload={
            **data,
            "exp": datetime.now(timezone.utc) + expiry,
        },
        algorithm=security_settings.JWT_ALGORITHM,
        key=security_settings.JWT_SECRET,
    )


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            jwt=token,
            algorithms=[security_settings.JWT_ALGORITHM],
            key=security_settings.JWT_SECRET,
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is Expired."
        )

    except jwt.PyJWTError:
        return None
