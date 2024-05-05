from app.models.models import Feature1Sample
from sqlalchemy.orm import Session


def get_feature1_by_id(db: Session, id: int) -> Feature1Sample | None:
    return db.query(Feature1Sample).filter(Feature1Sample.id == id).first()
