from typing import Dict, Any
from fastapi import HTTPException
from sqlmodel import Session, select, func
from sqlalchemy.exc import SQLAlchemyError
from models import PopPeriod


def get_pop_size_sum(db: Session, period_id: int) -> Dict[str, Any]:
    """
    Calculate the total pop_size for all PopPeriod elements in a specific period.
    
    Args:
        db: Database session
        period_id: The ID of the period to calculate pop_size for
    
    Returns:
        Dict containing period_id and total_pop_size
    
    Raises:
        HTTPException: If database error occurs
    """
    try:
        statement = select(func.sum(PopPeriod.pop_size)).where(PopPeriod.period_id == period_id)
        result = db.exec(statement).first()
        
        total_pop_size = result if result is not None else 0
        
        return {
            "period_id": period_id,
            "total_pop_size": total_pop_size
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")