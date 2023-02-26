from fastapi import Header
from pydantic import BaseModel, Field


class PageParams:
    def get_offset_and_limit(self):
        raise NotImplementedError

    def get_search_params(self):
        raise NotImplementedError

    def get_sort_params(self):
        raise NotImplementedError

    def get_filter_params(self):
        raise NotImplementedError


class QueryPageParams(BaseModel, PageParams):
    page: int = Field(default=0, ge=0)
    size: int = Field(default=10, ge=1)
    q: str | None = Field(default="")
    sort: str | None = Field(default="")
    filter: str | None = Field(default="")

    def get_offset_and_limit(self):
        return self.page * self.size, self.size

    def get_search_params(self):
        return self.q

    def get_sort_params(self):
        return self.sort

    def get_filter_params(self):
        return self.filter


class HeaderPageParams(PageParams):
    def __init__(
            self,
            page: int = Header(default=0, ge=0),
            size: int = Header(default=10, ge=1),
            q: str | None = Header(default=""),
            sort: str | None = Header(default=""),
            filter_attr: str | None = Header(default="", alias="filter")
    ):
        self.page = page
        self.size = size
        self.q = q
        self.sort = sort
        self.filter = filter_attr

    def get_offset_and_limit(self):
        return self.page * self.size, self.size

    def get_search_params(self):
        return self.q

    def get_sort_params(self):
        return self.sort

    def get_filter_params(self):
        return self.filter
