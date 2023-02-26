from typing import Type

from fastapi import HTTPException
from sqlalchemy.orm.session import Session


class DBHelper:
    def __init__(self, model: Type[any]):
        self.model = model

    def get(self, db: Session, entity_id, allow_deleted: bool = False, deleted_key: str = "is_deleted"):
        entity = db.query(self.model).get(entity_id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Entity not found")
        elif hasattr(entity, deleted_key) and not allow_deleted and entity.is_deleted:
            raise HTTPException(status_code=404, detail="Entity not found")
        return entity

    def find_query(self, db: Session, filter_args: list[any] = None, sort: list[any] = None):
        query = db.query(self.model)
        if filter_args:
            return query.filter(*filter_args).order_by(*sort)
        return query

    def find_and_count(self, db: Session,
                       filter_args: list[any] = None, sort: list[any] = None,
                       offset: int = 0, limit: int = 10):
        query = self.find_query(db, filter_args, sort)
        return query.offset(offset).limit(limit).all(), query.count()

    def create_entity(self):
        return self.model()

    def apply_commit_refresh(self, db: Session, entity):
        self.apply(db, entity)
        self.commit(db)
        self.refresh(db, entity)

    @staticmethod
    def apply(db: Session, entity):
        db.add(entity)

    @staticmethod
    def apply_all(db: Session, entities):
        db.add_all(entities)

    @staticmethod
    def commit(db: Session):
        db.commit()

    @staticmethod
    def rollback(db: Session):
        db.rollback()

    @staticmethod
    def refresh(db: Session, entity):
        db.refresh(entity)
