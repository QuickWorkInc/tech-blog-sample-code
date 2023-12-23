# TestRootのconftest.py
# テスト全域で使用するfixtureなどを定義する


from typing import Any, Generator

import pytest
from app.db import Base, get_db
from app.main import app
from fastapi.testclient import TestClient
from pytest_postgresql import factories
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

# テスト用のDBをセットアップするためのfixture
# 既定ではdbname=testでDBが作成されテストケースの実行毎にDBは削除され１から再作成される
postgresql_noproc = factories.postgresql_noproc()
postgresql_fixture = factories.postgresql(
    "postgresql_noproc",
)


# pytest.fixtureのデコレーターを付与した関数はfixture関数になる
@pytest.fixture
def db(
    postgresql_fixture: Any,
) -> Generator[Session, None, None]:
    """テスト用DBセッションをSetupするFixture"""
    # 接続URIを作成
    uri = (
        f"postgresql://"
        f"{postgresql_fixture.info.user}:@{postgresql_fixture.info.host}:{postgresql_fixture.info.port}"
        f"/{postgresql_fixture.info.dbname}"
    )

    # engineを作成
    engine = create_engine(uri, echo=False, poolclass=NullPool)

    # SQLAlchemyで定義しているテーブルを全て作成する
    Base.metadata.create_all(engine)
    SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Sessionを生成
    db: Session = None
    try:
        db = SessionFactory()
        yield db
        db.commit()
    except Exception:
        db.rollback()
    finally:
        # teardown
        db.close()


@pytest.fixture
def client(db: Session):
    """テスト用HTTPクライアントをSetupするFixture"""

    # FastAPIのDependsで呼ばれるget_dbのレスポンスをテスト用のDBセッションに置き換える
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)
