from fastapi import APIRouter, HTTPException, Depends, Response, Request
from pydantic import BaseModel, Field
from typing import Optional
from app.database import get_db
from app.auth import (
    hash_password, verify_password, create_session,
    get_current_user, require_current_user, active_sessions
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    username: str
    password: str
    full_name: str
    phone: Optional[str] = ""
    village_town: Optional[str] = ""
    district: Optional[str] = ""
    state: Optional[str] = "Tamil Nadu"
    preferred_language: Optional[str] = "en"
    business_type: Optional[str] = ""

class LoginRequest(BaseModel):
    username: str
    password: str

class ProfileUpdateRequest(BaseModel):
    full_name: str
    phone: Optional[str] = ""
    village_town: Optional[str] = ""
    district: Optional[str] = ""
    state: Optional[str] = "Tamil Nadu"
    preferred_language: Optional[str] = "en"
    business_type: Optional[str] = ""

@router.post("/register")
def register(data: RegisterRequest, response: Response):
    data.username = data.username.strip().lower()
    if len(data.username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters.")
    if len(data.password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters.")

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (data.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username is already registered. Please log in.")

        pwd_hash = hash_password(data.password)
        cursor.execute("""
            INSERT INTO users (username, full_name, phone, password_hash, village_town, district, state, preferred_language, business_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.username, data.full_name, data.phone or "", pwd_hash,
            data.village_town or "", data.district or "", data.state or "Tamil Nadu",
            data.preferred_language or "en", data.business_type or ""
        ))
        user_id = cursor.lastrowid
        conn.commit()

    token = create_session(user_id, data.username, data.full_name, data.preferred_language or "en")
    response.set_cookie(key="session_token", value=token, max_age=7*24*3600, httponly=False)
    
    return {
        "success": True,
        "token": token,
        "user": {
            "id": user_id,
            "username": data.username,
            "full_name": data.full_name,
            "phone": data.phone,
            "village_town": data.village_town,
            "district": data.district,
            "state": data.state,
            "preferred_language": data.preferred_language,
            "business_type": data.business_type
        }
    }

@router.post("/login")
def login(data: LoginRequest, response: Response):
    username = data.username.strip().lower()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, full_name, phone, password_hash, village_town, district, state, preferred_language, business_type
            FROM users WHERE username = ?
        """, (username,))
        row = cursor.fetchone()
        if not row or not verify_password(row["password_hash"], data.password):
            raise HTTPException(status_code=400, detail="Invalid username or password.")

    token = create_session(row["id"], row["username"], row["full_name"], row["preferred_language"])
    response.set_cookie(key="session_token", value=token, max_age=7*24*3600, httponly=False)

    return {
        "success": True,
        "token": token,
        "user": {
            "id": row["id"],
            "username": row["username"],
            "full_name": row["full_name"],
            "phone": row["phone"],
            "village_town": row["village_town"],
            "district": row["district"],
            "state": row["state"],
            "preferred_language": row["preferred_language"],
            "business_type": row["business_type"]
        }
    }

@router.post("/demo-login")
def demo_login(response: Response):
    """Seed or fetch a demo user for instant 1-click exploration."""
    demo_username = "demo_entrepreneur"
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, full_name, phone, village_town, district, state, preferred_language, business_type FROM users WHERE username = ?", (demo_username,))
        row = cursor.fetchone()
        if not row:
            pwd_hash = hash_password("demo1234")
            cursor.execute("""
                INSERT INTO users (username, full_name, phone, password_hash, village_town, district, state, preferred_language, business_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                demo_username, "Muthuselvi M (முத்துச்செல்வி)", "9842109876", pwd_hash,
                "Alanganallur", "Madurai", "Tamil Nadu", "ta", "Food Processing & Snacks"
            ))
            user_id = cursor.lastrowid
            
            # Seed a few realistic initial cashbook transactions for demo
            sample_txns = [
                ("2026-10-24", "income", "Sales", 2800.0, "Cash", "Millet cookies & idli podi weekly shandy sales"),
                ("2026-10-24", "expense", "Raw Materials", 1200.0, "Cash", "Purchased 20 kg whole ragi & kambu"),
                ("2026-10-25", "income", "Sales", 3450.0, "UPI", "Direct supply to village school staff"),
                ("2026-10-26", "expense", "Packaging", 650.0, "UPI", "Bought 100 stand-up zip pouches"),
                ("2026-10-27", "income", "Sales", 4100.0, "Cash", "Advance order for temple festival sweets"),
                ("2026-10-27", "expense", "Transport", 250.0, "Cash", "Auto fare to Taluk shandy"),
                ("2026-10-28", "income", "Sales", 1900.0, "UPI", "Regular morning local shop sales")
            ]
            for t_date, t_type, t_cat, t_amt, t_mode, t_note in sample_txns:
                cursor.execute("""
                    INSERT INTO transactions (user_id, date, type, category, amount, payment_mode, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, t_date, t_type, t_cat, t_amt, t_mode, t_note))

            conn.commit()
            cursor.execute("SELECT id, username, full_name, phone, village_town, district, state, preferred_language, business_type FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()

    token = create_session(row["id"], row["username"], row["full_name"], row["preferred_language"])
    response.set_cookie(key="session_token", value=token, max_age=7*24*3600, httponly=False)

    return {
        "success": True,
        "token": token,
        "user": dict(row)
    }

@router.get("/me")
def get_profile(user: dict = Depends(require_current_user)):
    return {"user": user}

@router.post("/profile")
def update_profile(data: ProfileUpdateRequest, user: dict = Depends(require_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET
                full_name = ?,
                phone = ?,
                village_town = ?,
                district = ?,
                state = ?,
                preferred_language = ?,
                business_type = ?
            WHERE id = ?
        """, (
            data.full_name, data.phone or "", data.village_town or "",
            data.district or "", data.state or "Tamil Nadu",
            data.preferred_language or "en", data.business_type or "",
            user["id"]
        ))
        conn.commit()

    return {"success": True, "message": "Profile updated successfully."}

@router.post("/logout")
def logout(request: Request, response: Response):
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    elif "session_token" in request.cookies:
        token = request.cookies.get("session_token")
    
    if token and token in active_sessions:
        del active_sessions[token]

    response.delete_cookie("session_token")
    return {"success": True, "message": "Logged out successfully."}
