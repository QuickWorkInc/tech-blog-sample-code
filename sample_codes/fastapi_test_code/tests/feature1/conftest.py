import pytest
from app.models.models import Feature1Sample
from sqlalchemy.orm import Session


@pytest.fixture
def setup_db_for_test_feature1(db: Session, setup_db_users: None) -> None:
    _insert_feature1_sample(db)


def _insert_feature1_sample(db: Session) -> None:
    data = [
        Feature1Sample(column1=f"column1_{i}", column2=f"column2_{i}")
        for i in range(1, 4)
    ]
    db.add_all(data)
    db.commit()
