from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine(
    "",
    pool_pre_ping=True,
    pool_size=50,
    max_overflow=100)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
