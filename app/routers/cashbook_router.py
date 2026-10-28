import io
import csv
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel
from app.auth import require_current_user
from app.database import get_db

router = APIRouter(prefix="/api/cashbook", tags=["Daily Cash Book"])

class TransactionCreate(BaseModel):
    date: str
    type: str  # 'income' or 'expense'
    category: str
    amount: float
    payment_mode: Optional[str] = "Cash"
    notes: Optional[str] = ""

@router.get("/transactions")
def get_transactions(
    type: Optional[str] = None,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    user: dict = Depends(require_current_user)
):
    query = "SELECT id, date, type, category, amount, payment_mode, notes, created_at FROM transactions WHERE user_id = ?"
    params = [user["id"]]

    if type:
        query += " AND type = ?"
        params.append(type)
    if category:
        query += " AND category = ?"
        params.append(category)
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)

    query += " ORDER BY date DESC, id DESC LIMIT ?"
    params.append(limit)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

    return {"transactions": [dict(r) for r in rows]}

@router.post("/transactions")
def add_transaction(txn: TransactionCreate, user: dict = Depends(require_current_user)):
    if txn.type not in ("income", "expense"):
        raise HTTPException(status_code=400, detail="Transaction type must be 'income' or 'expense'.")
    if txn.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero.")

    # Validate and normalize date format (supports YYYY-MM-DD, DD-MM-YYYY, YYYY/MM/DD, DD/MM/YYYY)
    raw_date = txn.date.strip()
    clean_date = None
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y"):
        try:
            parsed = datetime.strptime(raw_date, fmt)
            clean_date = parsed.strftime("%Y-%m-%d")
            break
        except ValueError:
            continue

    if not clean_date:
        raise HTTPException(status_code=400, detail="Invalid date format. Please use YYYY-MM-DD or DD-MM-YYYY.")

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (user_id, date, type, category, amount, payment_mode, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user["id"], clean_date, txn.type, txn.category,
            round(txn.amount, 2), txn.payment_mode or "Cash", txn.notes or ""
        ))
        conn.commit()
        txn_id = cursor.lastrowid

    return {"success": True, "id": txn_id, "message": "Transaction recorded successfully."}

@router.delete("/transactions/{txn_id}")
def delete_transaction(txn_id: int, user: dict = Depends(require_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", (txn_id, user["id"]))
        conn.commit()
    return {"success": True, "message": "Transaction deleted."}

@router.get("/summary")
def get_financial_summary(user: dict = Depends(require_current_user)):
    today = datetime.now().date()
    # Weekly: last 7 days
    week_ago = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    # Monthly: last 30 days
    month_ago = (today - timedelta(days=30)).strftime("%Y-%m-%d")

    with get_db() as conn:
        cursor = conn.cursor()

        # All-time totals
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
                SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expense
            FROM transactions WHERE user_id = ?
        """, (user["id"],))
        all_row = cursor.fetchone()
        all_income = all_row["total_income"] or 0.0
        all_expense = all_row["total_expense"] or 0.0

        # Weekly totals
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as weekly_income,
                SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as weekly_expense
            FROM transactions WHERE user_id = ? AND date >= ?
        """, (user["id"], week_ago))
        week_row = cursor.fetchone()
        week_income = week_row["weekly_income"] or 0.0
        week_expense = week_row["weekly_expense"] or 0.0

        # Monthly totals
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as monthly_income,
                SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as monthly_expense
            FROM transactions WHERE user_id = ? AND date >= ?
        """, (user["id"], month_ago))
        month_row = cursor.fetchone()
        month_income = month_row["monthly_income"] or 0.0
        month_expense = month_row["monthly_expense"] or 0.0

        # Category Breakdown for Expenses (Last 30 days)
        cursor.execute("""
            SELECT category, SUM(amount) as total
            FROM transactions
            WHERE user_id = ? AND type = 'expense' AND date >= ?
            GROUP BY category ORDER BY total DESC
        """, (user["id"], month_ago))
        expense_categories = [{"category": r["category"], "total": r["total"]} for r in cursor.fetchall()]

        # Category Breakdown for Income (Last 30 days)
        cursor.execute("""
            SELECT category, SUM(amount) as total
            FROM transactions
            WHERE user_id = ? AND type = 'income' AND date >= ?
            GROUP BY category ORDER BY total DESC
        """, (user["id"], month_ago))
        income_categories = [{"category": r["category"], "total": r["total"]} for r in cursor.fetchall()]

        # Daily Trend for last 14 days (for charts)
        fourteen_days_ago = (today - timedelta(days=14)).strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT date,
                   SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as day_income,
                   SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as day_expense
            FROM transactions
            WHERE user_id = ? AND date >= ?
            GROUP BY date ORDER BY date ASC
        """, (user["id"], fourteen_days_ago))
        daily_trends = [dict(r) for r in cursor.fetchall()]

    return {
        "all_time": {
            "total_income": round(all_income, 2),
            "total_expense": round(all_expense, 2),
            "net_balance": round(all_income - all_expense, 2)
        },
        "weekly": {
            "income": round(week_income, 2),
            "expense": round(week_expense, 2),
            "net_profit": round(week_income - week_expense, 2)
        },
        "monthly": {
            "income": round(month_income, 2),
            "expense": round(month_expense, 2),
            "net_profit": round(month_income - month_expense, 2)
        },
        "expense_breakdown": expense_categories,
        "income_breakdown": income_categories,
        "daily_trends": daily_trends
    }

@router.get("/export-csv")
def export_transactions_csv(user: dict = Depends(require_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date, type, category, amount, payment_mode, notes, created_at
            FROM transactions
            WHERE user_id = ?
            ORDER BY date DESC, id DESC
        """, (user["id"],))
        rows = cursor.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Type", "Category", "Amount (INR)", "Payment Mode", "Notes", "Timestamp"])

    for r in rows:
        writer.writerow([r["date"], r["type"].upper(), r["category"], f"{r['amount']:.2f}", r["payment_mode"], r["notes"], r["created_at"]])

    csv_data = output.getvalue()
    filename = f"RuralBiz_CashBook_{user['username']}_{datetime.now().strftime('%Y%m%d')}.csv"

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
