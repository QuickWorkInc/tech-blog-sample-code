from app.crud.feature1 import get_feature1_by_id
from app.db import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/feature1",
    tags=["feature1"],
)


class GetFeature1ByIdResponse(BaseModel):
    column1: str
    column2: str


@router.get(
    "/{id}",
    response_description="OK",
    status_code=status.HTTP_200_OK,
    summary="Get feature1 by id",
)
def router_get_feature1_by_id(
    id: int, db: Session = Depends(get_db)
) -> GetFeature1ByIdResponse:
    res = get_feature1_by_id(db, id=id)
    if not res:
        raise HTTPException(status_code=404, detail="Feature1 not found")
    return res
