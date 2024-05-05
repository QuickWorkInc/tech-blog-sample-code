# pytest でテストケース毎に DB を自動的に初期化する方法

# 概要

Web バックエンドのテストコードを書く場合、その多くは DB に依存していることが多いです。
DB 関連のテストは、テストデータの準備やテストケース毎の DB 処理化を適切に行うことが重要ですが、手間がかかる場合あるため、Mock で擬似的にテストしてしまうことも多いかと思います。

ただ、Mock を使ったテストは本質的な問題を検知できない意味のないテストになってしまう可能性があり、可能な限り DB の Mock を行わずに、実際の DB を使用してテストすることが望ましいと考えています。

本記事では、pytest、sqlalchemy、PostgreSQL を使った場合に、テストケース毎に DB を簡単に初期化しつつ、テストケース毎の前提データ登録も簡単うことでテスト開発体験を向上させる方法を紹介します。

## 前提環境

本記事では、以下の環境を前提として説明いたします。

- python: 3.11
- SQLAlchemy: 1.4
- PostgreSQL: 13 (サンプルコードでは docker で構築しています)

## pytest を使ったテストの基本

pytest で効率的なテストを実装するためには、conftest.py や fixture の理解が重要です。

基本的な説明は以下に詳しく記述しているので参照いただければと思います。

conftest.py と fixture を使うことで、テスト用 DB のセットアップやテストデータ登録をシンプルに記述することが可能です。

https://zenn.dev/tk_resilie/articles/python_test_template

## テスト用 DB セットアップ、テストデータ登録、テストケースの実装方法

### テスト用 DB の fixture の作成（Posgresql の場合）

特段のセットアップをせずに DB 連携ありのテストケースを pytest を実行した場合、ローカル開発環境で使用している DB を使用することになります。ローカル開発環境の DB の状態はテスト実行によって都度変更されてしまう場合があり、毎回テスト結果が変わってしまう恐れがあります。
そのため、テスト実行毎に状態が初期化されるテスト用 DB をセットアップできることが望まく、これを簡単に行うことができる以下のライブラリが提供されています。

PostgreSQL 用: pytest-postgresql 　（今回はこちらを使用）
MySQL 用: pytest-mysql

このライブラリを使うことで、テスト毎に毎回データがリセットされるテスト用の DB を扱う fixture を簡単に作ることができます。
テスト用 DB の fixture を使用するとローカルに docker 等で構築した postgresql サーバーに対して接続して、１つのテストケース毎にテスト用の databse を作成 → テスト実施 → database を削除という処理を行うことができます。

サンプルコードは以下の通りです。
① の箇所で、pytest_postgresql の機能を使って、postgresql の fixture を作成しています。この fixture はテスト用 DB への接続情報を保持し、databse のセットアップやテスト後の database 削除処理を行います。
② では ① で作成した postgresql_fixture を使って、各テストから直接呼び出す fixture を定義しています。
この fixture では、テスト用のテーブルの作成を行い DB セッションを返しています。
今回は sqlalchemy を使用しているため、create_all 関数を使って、sqlalchemy の model で定義されたテーブルを全て作成するようにしています。

tests/conftest.py

```python

from typing import Any, Generator

import pytest
from app.db import Base
from pytest_postgresql import factories
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.models.models import Team

# ①ライブラリを使ってテスト用のDBをセットアップするためのfixtureを作成
# 既定ではdbname=testでDBが作成されテストケースの実行毎にDBは削除され１から再作成される
postgresql_noproc = factories.postgresql_noproc()
postgresql_fixture = factories.postgresql(
    "postgresql_noproc",
)

# ②pytest.fixtureのデコレーターを付与した関数はfixture関数になる
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
```

テストに使用するサンプルのテーブル情報は以下の通りです。

app/models/models.py

```python
from app.db import Base
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.sql.functions import current_timestamp

class Feature1Sample(Base):
    """feature1用のサンプルテーブル"""

    __tablename__ = "feature1_sample"

    id = Column(Integer, primary_key=True)
    column1 = Column(TEXT)
    column2 = Column(TEXT)
    created_at = Column(
        DateTime(True), server_default=current_timestamp(), nullable=False
    )
    updated_at = Column(
        DateTime(True),
        server_default=current_timestamp(),
        onupdate=current_timestamp(),
        nullable=False,
    )
```

### テスト用データの登録

テスト毎に固有のテストデータを登録する部分は、バックエンドのテストにおいて非常に重要な部分です。pytest では conftest.py にテストデータ登録処理を fixture として記述することで、わかりやすくデータを管理することができます。
下記ソースコードの ① では、テストケース毎のテストデータ登録用の fixture を定義しています。この fixture をテストケースから呼び出すことで、テストケース実行前に、任意のデータを登録(Insert)することができます。

全ての登録処理を ① にまとめて記述するることもできますが、複数のテーブルに対してデータを Insert する場合にわかりずらくなるため、② のように関数を分けて実装するとわかりやすいです。
この conftest.py は feature1 の配下に配置されているため、feature1 配下のテストケースからしか読み込まれない仕様になっています。これにより、テストデータのスコープを制限することができ、意図しない依存関係が生まれないようにしています。

tests/feature1/copnftest.py

```python
import pytest
from app.models.models import Feature1Sample
from sqlalchemy.orm import Session

# ①テストケース毎のテストデータInsert用のfixture
@pytest.fixture
def setup_db_for_test_feature1(
    # fixture: db(テスト用DBのセッション)
    db: Session
) -> None:
    _insert_feature1_sample(db)

# ②各テーブル(Model)へのデータInsert処理
def _insert_feature1_sample(db: Session) -> None:
    data = [
        Feature1Sample(column1=f"column1_{i}", column2=f"column2_{i}")
        for i in range(1, 4)
    ]
    db.add_all(data)
    db.commit()
```

### テストケースの実装

テストケースの実装では、１つのテスト対象の関数に対して、複数のパラメータパターンでテストしたい場合が多いですが、普通に記述してしまうと、多くの冗長なテスト関数を記述することになり、保守性が悪化します。

そこで、同じテスト対象の関数に対する複数のパラメータのテストを１つのロジックで共通化するために parametrize を使用しています。
以下 ① のように@pytest.mark.parametrize のデコレータに対して、パラメーターの引数名、パラメータ配列の順で定義します。
配列で定義した引数名は、② のテストロジックの引数に同名で定義する必要があります。

pytest.param ではパラメータセットを定義します。引数の定義と同一順序で値を記述します。今回の例でいうと、"id", "expected_hit", "expected_column1", "expected_column2"の順でパラメータを記述します。
末尾の id はテストケース毎の任意の識別 id を定義できます。

id 定義は必須でありませんが、定義することで以下のようにテスト関数内の任意のパラメータのテストのみを選択的に実行することもできます。

`pytest tests/feature1/test_feature1.py::test_get_feature1_by_id[success]`

macOS の場合は以下のように[]にエスケープが必要です。
`pytest tests/feature1/test_feature1.py::test_get_feature1_by_id\[success\]`

以下の例では、② 以降で定義したテストロジックを２つのパラメータパターンで実行することができます。

parametrize によるテスト関数の共通化は、コードの冗長性を排除して保守性を向上させる効果がありますが、過度な共通化は、逆に保守性および可読性の悪化を招く可能性があるため、共通化が難しい場合はテスト関数を分ける判断も重要です。

```python
import pytest
from app.crud.feature1 import get_feature1_by_id
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# ①parametrizeを使用することで、1つのロジックで複数のパラメータをテストできる
@pytest.mark.parametrize(
    # テストケースで使用する引数名を配列で指定する
    ["id", "expected_hit", "expected_column1", "expected_column2"],
    # パラメータを指定する(引数名と同じ順番で指定する。idはテストケースのID)
    [
        pytest.param(1, True, "column1_1", "column2_1", id="success"),
        pytest.param(99, False, None, None, id="not_found"),
    ],
)
# ②テストロジックはparametrizeに指定したパラメータの配列分だけ実行される
def test_get_feature1_by_id(
    # fixture: db(テスト用DBのセッション)
    db: Session,
    # fixture: setup_db_for_test_feature1(テストデータInsert)
    setup_db_for_test_feature1: None,
    # parametrizeで指定した引数名を指定する(順番が一致している必要はないが指定した引数は全て記述する必要がある)
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
```

### テスト実行例

DB を docker で構築する場合の docker compose のサンプルです。
テスト実行前に`docker compose up -d` で起動しておきます。

compose.yml

```yml
services:
  db:
    image: postgres
    volumes:
      - postgres-volume:/data/postgres
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: pass
      PGDATA: /data/postgres
      POSTGRES_HOST_AUTH_METHOD: "trust"
    ports:
      - "5432:5432"
    networks:
      - api-network

networks:
  api-network:
    driver: bridge

volumes:
  postgres-volume:
```

テストを実行するためのコマンド例は以下の通りです。

```bash
# 必要なライブラリのインストール
$ python -m venv venv
$ . venv/bin/activate
$ pip install pytest pytest-postgresql sqlalchemy

# テスト実行(全テストケース)
$ pytest tests

# テスト実行(特定のテスト関数の指定したパラメータIDのみ実行)
$ pytest tests/feature1/test_feature1.py::test_get_feature1_by_id[success]
```

## まとめ

pytest、sqlalchemy、PostgreSQL を使った場合の効率的な実装方法について説明しました。
Web バックエンドのテスト実装は、DB 部分を適切に対応できると、一気にテスト体験が向上するため、ぜひお試しください。
また今回は PostgreSQL を使用しましたが、MySQL 向けの同等のライブラリが提供されているため、同じように実装が可能です。
テスト体験の向上は、テストカバー率の向上につながりアプリケーションの品質向上につながると感がえております。

SalesNowのプロダクトや文化についてもっと知りたいと思われた方は、カジュアル面談でお話しましょう。
https://open.talentio.com/r/1/c/quickwork/homes/4033