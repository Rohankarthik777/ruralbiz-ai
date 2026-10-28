import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.database import init_db
from app.routers import (
    auth_router, idea_router, finance_router,
    cashbook_router, market_router, chatbot_router,
    plan_router, loan_router
)

# Initialize Database on startup
init_db()

app = FastAPI(
    title="RuralBiz AI",
    description="AI-Driven Hyper-Local Business Advisory and Financial Structuring Assistant for Rural Micro-Entrepreneurs",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent

# Mount Static Files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Include API Routers
app.include_router(auth_router.router)
app.include_router(idea_router.router)
app.include_router(finance_router.router)
app.include_router(cashbook_router.router)
app.include_router(market_router.router)
app.include_router(chatbot_router.router)
app.include_router(plan_router.router)
app.include_router(loan_router.router)

@app.get("/", response_class=HTMLResponse)
def index_view(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": "RuralBiz AI",
        "version": "1.0.0"
    }
