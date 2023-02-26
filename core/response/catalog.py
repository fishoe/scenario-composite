from pydantic import BaseModel
from pydantic.generics import GenericModel
from typing import TypeVar, Generic

ItemType = TypeVar("ItemType", bound=BaseModel)


class CatalogResponse(GenericModel, Generic[ItemType]):
    summaries: list[ItemType]
    length: int
    total: int
