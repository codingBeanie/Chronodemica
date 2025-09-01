from typing import List, Optional, Type, TypeVar
from fastapi import HTTPException
from sqlmodel import SQLModel, Session, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

T = TypeVar("T", bound=SQLModel)


def create_item(db: Session, obj_in: T) -> T:
    try:
        db.add(obj_in)
        db.commit()
        db.refresh(obj_in)
        return obj_in
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Integrity error: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


def get_item(db: Session, model: Type[T], id: int) -> Optional[T]:
    try:
        return db.get(model, id)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


def get_items(db: Session, model: Type[T], skip: int = 0, limit: int = 100, filters: dict = None, sort_by: str = None, sort_direction: str = "asc") -> List[T]:
    try:
        statement = select(model)
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(model, field):
                    column = getattr(model, field)
                    statement = statement.where(column == value)
        
        # Apply sorting
        if sort_by and hasattr(model, sort_by):
            column = getattr(model, sort_by)
            if sort_direction.lower() == "desc":
                statement = statement.order_by(column.desc())
            else:
                statement = statement.order_by(column.asc())
        
        # Apply pagination
        statement = statement.offset(skip).limit(limit)
        
        return db.exec(statement).all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


def update_item(db: Session, db_obj: T, obj_in: dict) -> T:
    try:
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Integrity error: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


def delete_item(db: Session, model: Type[T], id: int) -> T:
    try:
        obj = db.get(model, id)
        if not obj:
            raise HTTPException(status_code=404, detail="Item not found")
        db.delete(obj)
        db.commit()
        return obj
    except HTTPException:
        raise
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Cannot delete: referenced by other records")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")