import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.auth import require_current_user
from app.database import get_db
from app.ai_engine import calculate_financial_plan, calculate_smart_pricing

router = APIRouter(prefix="/api/finance", tags=["Financial Planning & Pricing"])

class FinancialCalcRequest(BaseModel):
    daily_sales_units: float = 30.0
    selling_price_per_unit: float = 120.0
    cost_per_unit: float = 75.0
    daily_operating_cost: float = 300.0
    fixed_startup_cost: float = 35000.0
    working_capital_days: int = 30

class SmartPricingRequest(BaseModel):
    product_name: str = "Handmade Product"
    raw_material_cost: float = 45.0
    direct_labor_cost: float = 20.0
    packaging_cost: float = 8.0
    utilities_and_fuel: float = 5.0
    other_overhead: float = 4.0
    target_margin_pct: float = 25.0
    competitor_market_price: Optional[float] = 110.0

class SavePricingRequest(BaseModel):
    product_name: str
    calculation_data: dict

@router.post("/calculate")
def calculate_plan(req: FinancialCalcRequest, user: dict = Depends(require_current_user)):
    result = calculate_financial_plan(
        daily_sales_units=req.daily_sales_units,
        selling_price_per_unit=req.selling_price_per_unit,
        cost_per_unit=req.cost_per_unit,
        daily_operating_cost=req.daily_operating_cost,
        fixed_startup_cost=req.fixed_startup_cost,
        working_capital_days=req.working_capital_days
    )
    return {"success": True, "results": result}

@router.post("/pricing")
def smart_pricing(req: SmartPricingRequest, user: dict = Depends(require_current_user)):
    result = calculate_smart_pricing(
        raw_material_cost=req.raw_material_cost,
        direct_labor_cost=req.direct_labor_cost,
        packaging_cost=req.packaging_cost,
        utilities_and_fuel=req.utilities_and_fuel,
        other_overhead=req.other_overhead,
        target_margin_pct=req.target_margin_pct,
        competitor_market_price=req.competitor_market_price
    )
    return {"success": True, "product_name": req.product_name, "pricing": result}

@router.post("/save-pricing")
def save_pricing(req: SavePricingRequest, user: dict = Depends(require_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pricing_calculations (user_id, product_name, calculation_data)
            VALUES (?, ?, ?)
        """, (user["id"], req.product_name, json.dumps(req.calculation_data)))
        conn.commit()
        saved_id = cursor.lastrowid
    return {"success": True, "id": saved_id, "message": "Pricing calculation saved."}

@router.get("/saved-pricings")
def get_saved_pricings(user: dict = Depends(require_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, product_name, calculation_data, created_at FROM pricing_calculations WHERE user_id = ? ORDER BY id DESC", (user["id"],))
        rows = cursor.fetchall()
        result = []
        for r in rows:
            result.append({
                "id": r["id"],
                "product_name": r["product_name"],
                "calculation_data": json.loads(r["calculation_data"]),
                "created_at": r["created_at"]
            })
    return {"saved_pricings": result}

@router.delete("/saved-pricings/{pricing_id}")
def delete_saved_pricing(pricing_id: int, user: dict = Depends(require_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pricing_calculations WHERE id = ? AND user_id = ?", (pricing_id, user["id"]))
        conn.commit()
    return {"success": True, "message": "Saved pricing deleted."}
