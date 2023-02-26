from core.db.base_class import Base
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class User(Base):
    name: str = Column(String(40))
    age: int = Column(Integer())
    address: str = Column(String(40))
    is_deleted: bool = Column(Boolean(), default=False)

    items = relationship("Item", back_populates="user")


class Item(Base):
    name: str = Column(String(40))
    price: int = Column(Integer())
    user_id: int = Column(Integer(), ForeignKey("user.id"))
    is_deleted: bool = Column(Boolean(), default=False)

    user = relationship("User", back_populates="items")


class UserFile(Base):
    name: str = Column(String(40))
    user_id: int = Column(Integer(), ForeignKey("user.id"))
    is_deleted: bool = Column(Boolean(), default=False)

    user = relationship("User")
