import os
import uuid
import hashlib

import bcrypt
from fastapi import Request


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def generate_client_fingerprint(request: Request) -> str:
    user_agent = request.headers.get("user-agent", "unknown")
    accept_language = request.headers.get("accept-language", "unknown")
    client_fingerprint = f"{user_agent}-{accept_language}"
    return hashlib.sha256(client_fingerprint.encode("utf-8")).hexdigest()


def generate_unique_file_name(file_name: str) -> str:
    unique_id_length = 15
    unique_id = uuid.uuid4().hex[:unique_id_length]
    _, file_extension = os.path.splitext(file_name)
    return f"{unique_id}{file_extension}"
