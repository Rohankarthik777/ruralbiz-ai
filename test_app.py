import json
import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

    # Also test index page
    index_res = client.get("/")
    assert index_res.status_code == 200
    assert "RuralBiz AI" in index_res.text

def test_auth_workflow():
    uid = int(time.time() * 1000)
    username = f"user_{uid}"
    reg_data = {
        "username": username,
        "password": "pass1234_test",
        "full_name": "Selvan Murugan",
        "phone": "9876543210",
        "village_town": "Vadipatti",
        "district": "Madurai",
        "state": "Tamil Nadu",
        "preferred_language": "ta",
        "business_type": "Poultry & Eggs"
    }
    res = client.post("/api/auth/register", json=reg_data)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "token" in data
    token = data["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get profile
    res_me = client.get("/api/auth/me", headers=headers)
    assert res_me.status_code == 200
    assert res_me.json()["user"]["username"] == username

    # 3. Update profile
    update_data = {
        "full_name": "Selvan Murugan B.Sc",
        "phone": "9876543211",
        "village_town": "Vadipatti Town",
        "district": "Madurai",
        "state": "Tamil Nadu",
        "preferred_language": "en",
        "business_type": "Organic Poultry"
    }
    res_up = client.post("/api/auth/profile", json=update_data, headers=headers)
    assert res_up.status_code == 200

    # 4. Demo Login test
    res_demo = client.post("/api/auth/demo-login")
    assert res_demo.status_code == 200
    assert res_demo.json()["success"] is True
    assert "token" in res_demo.json()

def test_business_ideas():
    # Login as demo user
    demo_res = client.post("/api/auth/demo-login")
    token = demo_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Generate ideas
    res = client.post("/api/ideas/generate", json={
        "budget": 30000,
        "skills": ["Livestock Care", "Feeding"],
        "location": "Village",
        "language": "en"
    }, headers=headers)
    assert res.status_code == 200
    ideas = res.json()["ideas"]
    assert len(ideas) > 0
    first_idea = ideas[0]
    assert "title" in first_idea
    assert "materials" in first_idea
    assert "steps" in first_idea

    # Save idea
    save_res = client.post("/api/ideas/save", json={
        "idea_title": first_idea["title"],
        "idea_data": first_idea
    }, headers=headers)
    assert save_res.status_code == 200
    saved_id = save_res.json()["id"]

    # List saved ideas
    get_res = client.get("/api/ideas/saved", headers=headers)
    assert get_res.status_code == 200
    assert len(get_res.json()["saved_ideas"]) >= 1

    # Delete idea
    del_res = client.delete(f"/api/ideas/{saved_id}", headers=headers)
    assert del_res.status_code == 200

def test_financial_calculator_and_pricing():
    demo_res = client.post("/api/auth/demo-login")
    token = demo_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Financial plan
    calc_res = client.post("/api/finance/calculate", json={
        "daily_sales_units": 40,
        "selling_price_per_unit": 150,
        "cost_per_unit": 90,
        "daily_operating_cost": 400,
        "fixed_startup_cost": 30000,
        "working_capital_days": 30
    }, headers=headers)
    assert calc_res.status_code == 200
    results = calc_res.json()["results"]
    assert "daily" in results
    assert "monthly" in results
    assert "break_even" in results
    assert results["daily"]["revenue"] == 6000.0
    assert results["break_even"]["contribution_margin_per_unit"] == 60.0

    # Smart pricing
    price_res = client.post("/api/finance/pricing", json={
        "product_name": "Cold-Pressed Groundnut Oil (1L)",
        "raw_material_cost": 160.0,
        "direct_labor_cost": 25.0,
        "packaging_cost": 15.0,
        "utilities_and_fuel": 10.0,
        "other_overhead": 10.0,
        "target_margin_pct": 25.0,
        "competitor_market_price": 280.0
    }, headers=headers)
    assert price_res.status_code == 200
    pdata = price_res.json()["pricing"]
    assert pdata["cost_breakdown"]["total_unit_cost"] == 220.0
    assert pdata["pricing_summary"]["suggested_price"] > 220.0

def test_cashbook():
    demo_res = client.post("/api/auth/demo-login")
    token = demo_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Add transaction
    txn_res = client.post("/api/cashbook/transactions", json={
        "date": "2026-10-28",
        "type": "income",
        "category": "Sales",
        "amount": 2400.0,
        "payment_mode": "UPI",
        "notes": "Direct shandy stall retail revenue"
    }, headers=headers)
    assert txn_res.status_code == 200
    txn_id = txn_res.json()["id"]

    # Summary
    summary_res = client.get("/api/cashbook/summary", headers=headers)
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert "weekly" in summary
    assert "monthly" in summary
    assert summary["all_time"]["total_income"] > 0

    # CSV Export
    csv_res = client.get("/api/cashbook/export-csv", headers=headers)
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers.get("content-type", "")
    assert "Amount (INR)" in csv_res.text

    # Delete transaction
    del_res = client.delete(f"/api/cashbook/transactions/{txn_id}", headers=headers)
    assert del_res.status_code == 200

def test_market_analysis():
    demo_res = client.post("/api/auth/demo-login")
    token = demo_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/market/analyze", json={
        "business_type": "Millet Snacks",
        "village_town": "Alanganallur",
        "district": "Madurai",
        "language": "ta"
    }, headers=headers)
    assert res.status_code == 200
    analysis = res.json()["analysis"]
    assert "seasonal_demand" in analysis
    assert "customer_segments" in analysis
    assert len(analysis["survey_questions"]) == 10

def test_chatbot_advisory():
    # Chat in English
    res_en = client.post("/api/chat", json={
        "message": "What is MUDRA loan and how to apply?",
        "language": "en"
    })
    assert res_en.status_code == 200
    assert "Shishu" in res_en.json()["reply"]

    # Chat in Tamil
    res_ta = client.post("/api/chat", json={
        "message": "லாப வரம்பு மற்றும் விற்பனை விலை எப்படி கணக்கிடுவது?",
        "language": "ta"
    })
    assert res_ta.status_code == 200
    assert "விற்பனை விலை" in res_ta.json()["reply"]

def test_business_plan():
    demo_res = client.post("/api/auth/demo-login")
    token = demo_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Generate
    gen_res = client.post("/api/plans/generate", json={
        "title": "Millet Value-Added Food Unit",
        "category": "Food Processing",
        "location": "Alanganallur, Madurai",
        "startup_budget": 50000,
        "monthly_sales_target": 60000,
        "language": "en"
    }, headers=headers)
    assert gen_res.status_code == 200
    plan_obj = gen_res.json()["plan"]
    assert len(plan_obj["sections"]) >= 6

    # Save
    save_res = client.post("/api/plans/save", json={
        "title": plan_obj["metadata"]["title"],
        "business_category": plan_obj["metadata"]["category"],
        "location": plan_obj["metadata"]["location"],
        "startup_cost": plan_obj["metadata"]["startup_capital"],
        "plan_data": plan_obj
    }, headers=headers)
    assert save_res.status_code == 200
    plan_id = save_res.json()["id"]

    # Fetch
    get_res = client.get(f"/api/plans/{plan_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["plan"]["title"] == "Millet Value-Added Food Unit"

def test_microloan_assistant():
    demo_res = client.post("/api/auth/demo-login")
    token = demo_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Schemes
    schemes_res = client.get("/api/loan/schemes")
    assert schemes_res.status_code == 200
    assert len(schemes_res.json()["schemes"]) >= 4

    # Checklist
    chk_res = client.get("/api/loan/checklist")
    assert chk_res.status_code == 200
    assert len(chk_res.json()["checklist"]) >= 6

    # Assess
    assess_res = client.post("/api/loan/assess", json={
        "requested_amount": 40000,
        "monthly_net_profit": 15000,
        "checked_documents": ["doc_aadhaar", "doc_pan", "doc_bank_passbook", "doc_photo", "doc_quotation", "doc_business_plan"],
        "has_existing_loan": False,
        "existing_emi": 0
    }, headers=headers)
    assert assess_res.status_code == 200
    assessment = assess_res.json()["assessment"]
    assert assessment["score"] >= 80
    assert "estimated_monthly_emi" in assessment
    assert assessment["dscr_ratio"] > 1.5

def test_date_formats_and_enrichment():
    demo_res = client.post("/api/auth/demo-login")
    token = demo_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Test DD-MM-YYYY date format in cashbook
    res_date = client.post("/api/cashbook/transactions", json={
        "date": "28-10-2026",
        "type": "income",
        "category": "Sales Revenue",
        "amount": 1500.0,
        "payment_mode": "UPI",
        "notes": "Testing DD-MM-YYYY format"
    }, headers=headers)
    assert res_date.status_code == 200
    assert res_date.json()["success"] is True

    # 2. Test ideas generation returns Tamil titles and materials
    res_ideas = client.post("/api/ideas/generate", json={
        "budget": 25000,
        "skills": ["Livestock"],
        "location": "Village",
        "language": "ta"
    }, headers=headers)
    assert res_ideas.status_code == 200
    ideas = res_ideas.json()["ideas"]
    assert len(ideas) > 0
    first = ideas[0]
    assert "ta_title" in first and len(first["ta_title"]) > 0
    assert "ta_category" in first and len(first["ta_category"]) > 0
    assert len(first["materials"]) > 0
    assert "ta_item" in first["materials"][0] and len(first["materials"][0]["ta_item"]) > 0

if __name__ == "__main__":
    print("Running automated feature tests...")
    test_health()
    test_auth_workflow()
    test_business_ideas()
    test_financial_calculator_and_pricing()
    test_cashbook()
    test_market_analysis()
    test_chatbot_advisory()
    test_business_plan()
    test_microloan_assistant()
    test_date_formats_and_enrichment()
    print("ALL 9 CORE FEATURE MODULE TESTS PASSED PERFECTLY!")
