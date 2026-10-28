import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.auth import require_current_user
from app.database import get_db
from app.ai_engine import assess_microloan_readiness, SCHEMES_GUIDE, DOCUMENTS_CHECKLIST

router = APIRouter(prefix="/api/loan", tags=["Microloan Readiness Assistant"])

class LoanAssessRequest(BaseModel):
    requested_amount: float = 45000.0
    monthly_net_profit: float = 18000.0
    checked_documents: List[str] = ["doc_aadhaar", "doc_pan", "doc_bank_passbook", "doc_photo"]
    has_existing_loan: bool = False
    existing_emi: float = 0.0

class SaveLoanAssessmentRequest(BaseModel):
    loan_scheme: str
    requested_amount: float
    readiness_score: int
    checklist_data: dict

@router.get("/schemes")
def get_schemes():
    return {"schemes": SCHEMES_GUIDE}

@router.get("/checklist")
def get_checklist():
    return {"checklist": DOCUMENTS_CHECKLIST}

@router.post("/assess")
def assess_loan(req: LoanAssessRequest, user: dict = Depends(require_current_user)):
    result = assess_microloan_readiness(
        requested_amount=req.requested_amount,
        monthly_net_profit=req.monthly_net_profit,
        checked_documents=req.checked_documents,
        has_existing_loan=req.has_existing_loan,
        existing_emi=req.existing_emi
    )
    return {"success": True, "assessment": result}

@router.post("/save-assessment")
def save_assessment(req: SaveLoanAssessmentRequest, user: dict = Depends(require_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO loan_assessments (user_id, loan_scheme, requested_amount, readiness_score, checklist_data)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user["id"], req.loan_scheme, req.requested_amount,
            req.readiness_score, json.dumps(req.checklist_data)
        ))
        conn.commit()
        saved_id = cursor.lastrowid
    return {"success": True, "id": saved_id, "message": "Loan readiness assessment saved."}

@router.get("/saved-assessments")
def get_saved_assessments(user: dict = Depends(require_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, loan_scheme, requested_amount, readiness_score, checklist_data, created_at
            FROM loan_assessments WHERE user_id = ? ORDER BY id DESC
        """, (user["id"],))
        rows = cursor.fetchall()
        result = []
        for r in rows:
            result.append({
                "id": r["id"],
                "loan_scheme": r["loan_scheme"],
                "requested_amount": r["requested_amount"],
                "readiness_score": r["readiness_score"],
                "checklist_data": json.loads(r["checklist_data"]) if r["checklist_data"] else {},
                "created_at": r["created_at"]
            })
    return {"assessments": result}
