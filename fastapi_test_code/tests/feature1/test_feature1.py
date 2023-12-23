from typing import Any

import pytest
from app.crud.feature1 import get_feature1_by_id
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.mark.parametrize(
    ["id", "expected_column1", "expected_column2"],
    [pytest.param(1, "column1_1", "column2_1")],
)
def test_get_feature1_by_id(
    db: Session,
    setup_db_for_test_feature1: None,
    id: int,
    expected_column1: str,
    expected_column2: str,
) -> None:
    feature1_obj = get_feature1_by_id(db, id=id)
    assert feature1_obj.column1 == expected_column1
    assert feature1_obj.column2 == expected_column2


@pytest.mark.parametrize(
    ["id", "expected_status", "expected_response"],
    [
        # success
        pytest.param(
            1,
            status.HTTP_200_OK,
            {"column1": "column1_1", "column2": "column2_1"},
            id="success",
        ),
        # id not found error
        pytest.param(
            999,
            status.HTTP_404_NOT_FOUND,
            {"detail": "Feature1 not found"},
            id="failure_not_found",
        ),
    ],
)
def test_router_get_feture1_by_id(
    client: TestClient,
    db: Session,
    setup_db_for_test_feature1: None,
    id: int,
    expected_status: int,
    expected_response: dict[str, Any],
) -> None:
    response = client.get(f"/feature1/{id}")
    assert response.status_code == expected_status
    assert response.json() == expected_response
