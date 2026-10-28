import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.auth import require_current_user
from app.database import get_db
from app.ai_engine import generate_business_ideas

router = APIRouter(prefix="/api/ideas", tags=["Business Ideas"])

class GenerateIdeaRequest(BaseModel):
    budget: float = 25000
    skills: List[str] = []
    location: str = "Village"
    language: str = "en"
    custom_prompt: Optional[str] = ""

class SaveIdeaRequest(BaseModel):
    idea_title: str
    idea_data: dict

@router.post("/generate")
def generate_ideas(req: GenerateIdeaRequest, user: dict = Depends(require_current_user)):
    ideas = generate_business_ideas(
        budget=req.budget,
        skills=req.skills,
        location=req.location,
        language=req.language or user.get("preferred_language", "en"),
        custom_prompt=req.custom_prompt or ""
    )
    return {"success": True, "ideas": ideas}

@router.post("/save")
def save_idea(req: SaveIdeaRequest, user: dict = Depends(require_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO saved_ideas (user_id, idea_title, idea_data)
            VALUES (?, ?, ?)
        """, (user["id"], req.idea_title, json.dumps(req.idea_data)))
        conn.commit()
        idea_id = cursor.lastrowid
    return {"success": True, "id": idea_id, "message": "Business idea saved to your profile."}

@router.get("/saved")
def get_saved_ideas(user: dict = Depends(require_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, idea_title, idea_data, created_at FROM saved_ideas WHERE user_id = ? ORDER BY id DESC", (user["id"],))
        rows = cursor.fetchall()
        result = []
        for r in rows:
            result.append({
                "id": r["id"],
                "idea_title": r["idea_title"],
                "idea_data": json.loads(r["idea_data"]),
                "created_at": r["created_at"]
            })
    return {"saved_ideas": result}

@router.delete("/{idea_id}")
def delete_saved_idea(idea_id: int, user: dict = Depends(require_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM saved_ideas WHERE id = ? AND user_id = ?", (idea_id, user["id"]))
        conn.commit()
    return {"success": True, "message": "Saved idea deleted."}
