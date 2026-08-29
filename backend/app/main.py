from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import auth
from app.routers import hs_classifier
from app.routers import landed_cost
from app.routers import countries

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="AI-powered import/export intelligence platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(hs_classifier.router)
app.include_router(landed_cost.router)
app.include_router(countries.router)


@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to TradeFlow AI", "status": "running", "docs": "/docs"}


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": "0.1.0",
        "debug": settings.debug,
    }