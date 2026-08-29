from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.landed_cost import LandedCostRequest, LandedCostResponse
from app.services.landed_cost_service import calculate_landed_cost

router = APIRouter(prefix="/landed-cost", tags=["Landed Cost Calculator"])


@router.post("/calculate", response_model=LandedCostResponse)
async def calculate(request: LandedCostRequest, db: Session = Depends(get_db)):
    try:
        return calculate_landed_cost(request, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")