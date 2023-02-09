from fastapi import Query


class CatalogParams:
    def __init__(
        self,
        page: int | None = Query(0, ge=1),
        page_size: int | None = Query(10, ge=1, alias="page-size"),
        q: str | None = Query(None),
        sort: str | None = Query(None)
    ):
        self.page = page
        self.page_size = page_size
        self.q = q
        self.sort = sort

    def get_limit(self) -> int:
        return self.page_size

    def get_skip(self) -> int:
        return (self.page - 1) * self.page_size

    def get_offset_and_limit(self) -> tuple[int, int]:
        return self.get_skip(), self.get_limit()
