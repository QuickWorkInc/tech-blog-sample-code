from typing import Any

import pytest
from app.crud.feature1 import get_feature1_by_id
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.mark.parametrize(
    # テストケースで使用する引数名を配列で指定する
    ["id", "expected_hit", "expected_column1", "expected_column2"],
    # パラメータを指定する(引数名と同じ順番で指定する。idはテストケースのID)
    [
        pytest.param(1, True, "column1_1", "column2_1", id="success"),
        pytest.param(99, False, None, None, id="not_found"),
    ],
)
def test_get_feature1_by_id(
    # fixture: db(テスト用DBのセッション)
    db: Session,
    # fixture: setup_db_for_test_feature1(テストデータInsert)
    setup_db_for_test_feature1: None,
    # parametrizeで指定した引数名を指定する(順番が一致している必要はない)
    id: int,
    expected_hit: bool,
    expected_column1: str | None,
    expected_column2: str | None,
) -> None:
    feature1_obj = get_feature1_by_id(db, id=id)
    if expected_hit:
        assert feature1_obj is not None
        assert feature1_obj.column1 == expected_column1
        assert feature1_obj.column2 == expected_column2
    else:
        assert feature1_obj is None


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
