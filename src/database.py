import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from . import models
from .config import POOL_SIZE, MAX_OVERFLOW, POOL_TIMEOUT, POOL_RECYCLE
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.environ.get('DATABASE_URL'), pool_size=POOL_SIZE, max_overflow=MAX_OVERFLOW, pool_timeout=POOL_TIMEOUT,
                       pool_recycle=POOL_RECYCLE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

models.Base.metadata.create_all(bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        return db
    finally:
        db.close()
