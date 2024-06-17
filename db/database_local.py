from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import POOL_SIZE, MAX_OVERFLOW, POOL_TIMEOUT, POOL_RECYCLE, POOL_PRE_PING, DATABASE_URL_LOCAL
from src.database import Base

engine = create_engine(DATABASE_URL_LOCAL, pool_size=POOL_SIZE, max_overflow=MAX_OVERFLOW, pool_timeout=POOL_TIMEOUT,
                       pool_recycle=POOL_RECYCLE, pre_ping=POOL_PRE_PING)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()

    try:
        return db
    finally:
        db.close()
