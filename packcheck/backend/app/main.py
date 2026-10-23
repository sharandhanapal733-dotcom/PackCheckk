import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database_init import init_db
from app.api.auth import router as auth_router
from app.api.inspections import router as inspections_router
from app.api.rules import router as rules_router
from app.api.reports import router as reports_router
from app.api.dashboard import router as dashboard_router
from app.api.products import router as products_router

app = FastAPI(
    title="PackCheck — Legal Metrology Compliance System",
    description="Software System to check compliance of Packaged Commodities under Legal Metrology (Packaged Commodities) Rules, 2011 (SIH Problem SIH26034)",
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

# Mount static file directories for uploads and reports
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")
app.mount("/reports", StaticFiles(directory=str(settings.REPORT_DIR)), name="reports")

# Include Routers
app.include_router(auth_router)
app.include_router(inspections_router)
app.include_router(rules_router)
app.include_router(reports_router)
app.include_router(dashboard_router)
app.include_router(products_router)

@app.on_event("startup")
def on_startup():
    print("Initializing PackCheck database schema and seed data...")
    init_db()
    print("PackCheck backend engine started successfully on port 8001.")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "PackCheck Compliance Engine",
        "legal_reference": "Legal Metrology (Packaged Commodities) Rules, 2011",
        "problem_statement": "SIH26034"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
