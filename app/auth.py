import hashlib
import os
import secrets
import hmac
import time
from typing import Optional, Dict
from fastapi import Request, HTTPException, status, Depends
from app.database import get_db

SECRET_KEY = os.environ.get("SESSION_SECRET", "ruralbiz-ai-secure-secret-key-2026-chennai-tamilnadu")
SESSION_EXPIRE_SECONDS = 7 * 24 * 3600  # 7 days

# In-memory session store (mapping token -> user_dict)
active_sessions: Dict[str, dict] = {}

def hash_password(password: str) -> str:
    """Hash password using PBKDF2 with SHA256 and random salt."""
    salt = os.urandom(16)
    kdf = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100_000)
    return salt.hex() + ":" + kdf.hex()

def verify_password(stored_password_hash: str, provided_password: str) -> bool:
    """Verify password against stored salt:hash."""
    try:
        salt_hex, hash_hex = stored_password_hash.split(":")
        salt = bytes.fromhex(salt_hex)
        kdf = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100_000)
        return hmac.compare_digest(kdf.hex(), hash_hex)
    except Exception:
        return False

def create_session(user_id: int, username: str, full_name: str, language: str) -> str:
    """Create a new session token and store session info."""
    token = secrets.token_urlsafe(32)
    active_sessions[token] = {
        "user_id": user_id,
        "username": username,
        "full_name": full_name,
        "language": language,
        "expires_at": time.time() + SESSION_EXPIRE_SECONDS
    }
    return token

def get_current_user(request: Request) -> Optional[dict]:
    """Retrieve user from Authorization header or Cookie."""
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    elif "session_token" in request.cookies:
        token = request.cookies.get("session_token")

    if not token or token not in active_sessions:
        return None

    session = active_sessions[token]
    if time.time() > session["expires_at"]:
        del active_sessions[token]
        return None

    # Fetch latest user details from DB
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, full_name, phone, village_town, district, state, preferred_language, business_type FROM users WHERE id = ?", (session["user_id"],))
        row = cursor.fetchone()
        if not row:
            return None
        return dict(row)

def require_current_user(request: Request) -> dict:
    user = get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in."
        )
    return user
