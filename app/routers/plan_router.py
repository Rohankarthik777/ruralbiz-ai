import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.auth import require_current_user
from app.database import get_db
from app.ai_engine import generate_business_plan

router = APIRouter(prefix="/api/plans", tags=["Business Plan Generator"])

class GeneratePlanRequest(BaseModel):
    title: str = "Country Poultry Farm Unit"
    category: str = "Livestock & Poultry"
    location: str = "Alanganallur, Madurai"
    startup_budget: float = 35000.0
    monthly_sales_target: float = 40000.0
    language: Optional[str] = "en"

class SavePlanRequest(BaseModel):
    title: str
    business_category: str
    location: str
    startup_cost: float
    plan_data: Dict[str, Any]

class UpdatePlanRequest(BaseModel):
    title: str
    plan_data: Dict[str, Any]

@router.post("/generate")
def create_plan(req: GeneratePlanRequest, user: dict = Depends(require_current_user)):
    lang = req.language or user.get("preferred_language", "en")
    owner = user.get("full_name", "Rural Entrepreneur")
    plan = generate_business_plan(
        title=req.title,
        category=req.category,
        location=req.location,
        startup_budget=req.startup_budget,
        monthly_sales_target=req.monthly_sales_target,
        owner_name=owner,
        language=lang
    )
    return {"success": True, "plan": plan}

@router.post("/save")
def save_plan(req: SavePlanRequest, user: dict = Depends(require_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO business_plans (user_id, title, business_category, location, startup_cost, plan_data)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user["id"], req.title, req.business_category, req.location,
            req.startup_cost, json.dumps(req.plan_data)
        ))
        conn.commit()
        plan_id = cursor.lastrowid
    return {"success": True, "id": plan_id, "message": "Business plan saved successfully."}

@router.get("")
def list_plans(user: dict = Depends(require_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, business_category, location, startup_cost, created_at, updated_at
            FROM business_plans WHERE user_id = ? ORDER BY id DESC
        """, (user["id"],))
        rows = cursor.fetchall()
    return {"plans": [dict(r) for r in rows]}

@router.get("/{plan_id}")
def get_plan(plan_id: int, user: dict = Depends(require_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, business_category, location, startup_cost, plan_data, created_at, updated_at
            FROM business_plans WHERE id = ? AND user_id = ?
        """, (plan_id, user["id"]))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Business plan not found.")
        data = dict(row)
        data["plan_data"] = json.loads(data["plan_data"])
    return {"plan": data}

@router.put("/{plan_id}")
def update_plan(plan_id: int, req: UpdatePlanRequest, user: dict = Depends(require_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE business_plans
            SET title = ?, plan_data = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ?
        """, (req.title, json.dumps(req.plan_data), plan_id, user["id"]))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Business plan not found.")
    return {"success": True, "message": "Business plan updated successfully."}

@router.delete("/{plan_id}")
def delete_plan(plan_id: int, user: dict = Depends(require_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM business_plans WHERE id = ? AND user_id = ?", (plan_id, user["id"]))
        conn.commit()
    return {"success": True, "message": "Business plan deleted."}
