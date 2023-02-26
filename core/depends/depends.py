from core.db import session


def get_db():
    db = session.SessionLocal()
    try:
        yield db
    finally:
        db.close()