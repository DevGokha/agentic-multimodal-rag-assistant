import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Fallback to local sqlite if DATABASE_URL is not set (useful for local development)
# Render or cloud DB will provide DATABASE_URL starting with postgresql:// or postgres://
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./sql_app.db")

# SQLAlchemy requires "postgresql://" not "postgres://"
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {}
# SQLite needs specific connect_args
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
