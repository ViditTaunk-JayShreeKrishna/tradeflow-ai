from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.database import get_db
from app.models.hs_code import HSCode
from app.ml.classifier import predict, is_model_ready

router = APIRouter(prefix="/hs-classifier", tags=["HS Code Classifier"])


class ClassifyRequest(BaseModel):
    description: str


class HSPrediction(BaseModel):
    hs_code: str
    description: str
    confidence: float
    confidence_pct: str


class ClassifyResponse(BaseModel):
    predicted_hs_code: str
    description: str
    confidence: float
    confidence_pct: str
    top_3: List[HSPrediction]
    model_version: str
    model_ready: bool


def enrich_with_description(hs_code: str, db: Session) -> str:
    record = db.query(HSCode).filter(HSCode.code == hs_code).first()
    return record.description if record else "Description not available"


@router.get("/status")
async def model_status():
    ready = is_model_ready()
    return {
        "model_ready": ready,
        "message": "Model loaded and ready" if ready else "Model not trained yet. Run training script first.",
    }


@router.post("/classify", response_model=ClassifyResponse)
async def classify(request: ClassifyRequest, db: Session = Depends(get_db)):
    if not request.description.strip():
        raise HTTPException(status_code=400, detail="Description cannot be empty")

    result = predict(request.description)

    if result is None:
        raise HTTPException(
            status_code=503,
            detail="ML model not ready. Please train the model first by running: python -m app.ml.train"
        )

    # Enrich top 3 with descriptions from database
    enriched_top_3 = []
    for pred in result["top_3"]:
        enriched_top_3.append(HSPrediction(
            hs_code=pred["hs_code"],
            description=enrich_with_description(pred["hs_code"], db),
            confidence=pred["confidence"],
            confidence_pct=f"{pred['confidence']:.1%}",
        ))

    return ClassifyResponse(
        predicted_hs_code=result["predicted_hs_code"],
        description=enrich_with_description(result["predicted_hs_code"], db),
        confidence=result["confidence"],
        confidence_pct=f"{result['confidence']:.1%}",
        top_3=enriched_top_3,
        model_version=result["model_version"],
        model_ready=True,
    )