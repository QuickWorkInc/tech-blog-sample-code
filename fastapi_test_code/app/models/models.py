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


class Feature2Sample(Base):
    """feature2用のサンプルテーブル"""

    __tablename__ = "feature2_sample"

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
