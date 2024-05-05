from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

# 通常のWriterインスタンス用(Sync)
engine = create_engine(
    url="postgresql://localhost:5432/app",
    echo=False,
)
SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    session: Session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()


Base = declarative_base()
