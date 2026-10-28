from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.auth import require_current_user
from app.ai_engine import analyze_local_market

router = APIRouter(prefix="/api/market", tags=["Hyper-Local Market Analysis"])

class MarketAnalysisRequest(BaseModel):
    business_type: str = "Rural Agro-Products & Snacks"
    village_town: Optional[str] = "Alanganallur"
    district: Optional[str] = "Madurai"
    language: Optional[str] = "en"

@router.post("/analyze")
def run_market_analysis(req: MarketAnalysisRequest, user: dict = Depends(require_current_user)):
    lang = req.language or user.get("preferred_language", "en")
    village = req.village_town or user.get("village_town", "Local Village")
    district = req.district or user.get("district", "District")

    analysis = analyze_local_market(
        business_type=req.business_type,
        village_town=village,
        district=district,
        language=lang
    )
    return {"success": True, "analysis": analysis}
