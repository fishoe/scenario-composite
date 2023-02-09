from functools import reduce

from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import create_model

from core.responses import CatalogResponse
from core.requests import CatalogParams
from core.scenario import Scenario


def reduce_dict(fields):
    return reduce(lambda x, y: {**x, **y}, fields, {})


class BaseChapterEndPoint:
    def __init__(self, router_args: dict = None):
        self.router_args = router_args or {}
        self.endpoint = None

    def __call__(self, router: APIRouter):
        router.add_api_route(**self.router_args)
        return router


class BaseChapter:
    def __init__(self, prefix: str, scenarios: list[Scenario]):
        self.prefix = prefix
        self.scenarios = scenarios

    @property
    def router(self):
        raise NotImplementedError


class BaseAPIChapter(BaseChapter):
    def __init__(self, prefix: str, scenarios: list[Scenario]):
        super().__init__(prefix, scenarios)
        default_types = [
            "summary_response",
            "detail_response",
            "modify_request",
            "create_request"
        ]
        self.io_types = {
            i: self._create_pydantic_type(i) for i in default_types
        }

    def _create_pydantic_type(self, scenario_type: str):
        response_fields = reduce_dict([getattr(scenario, scenario_type)() for scenario in self.scenarios])
        type_name = scenario_type.title().replace("_", "")
        response_type = create_model(type_name, **response_fields)
        return response_type

    def _define_catalog(self, router):
        async def catalog(
                page_metadata: CatalogParams = Depends(CatalogParams),
        ):
            return None

        BaseChapterEndPoint({
            "path": "/",
            "endpoint": catalog,
            "methods": ["GET"],
            "response_model": CatalogResponse[self.io_types["summary_response"]],
        })(router)

    def _define_detail(self, router):
        async def detail(
                item_id: int,
        ):
            return None

        BaseChapterEndPoint({
            "path": "/{item_id}",
            "endpoint": detail,
            "methods": ["GET"],
            "response_model": self.io_types["detail_response"],
        })(router)

    def _define_create(self, router):
        create_request = self.io_types["create_request"]

        async def create(
                request: create_request = Depends(),
        ):
            return None

        BaseChapterEndPoint({
            "path": "/",
            "endpoint": create,
            "methods": ["POST"],
        })(router)

    def _define_modify(self, router):
        modify_request = self.io_types["modify_request"]

        async def modify(
                request: modify_request = Body(),
        ):
            a = reduce_dict([scenario.modify({}, request) for scenario in self.scenarios])
            return a

        BaseChapterEndPoint({
            "path": "/",
            "endpoint": modify,
            "methods": ["PATCH"],
        })(router)

    @property
    def router(self):
        router = APIRouter(prefix=self.prefix)

        self._define_catalog(router)
        self._define_detail(router)
        self._define_create(router)
        self._define_modify(router)

        return router


class SampleChapter(BaseAPIChapter):
    def __init__(self, prefix: str, scenarios: list[Scenario]):
        super().__init__(prefix, scenarios)
        self.data = [{"num": n, "value": "none"} for n in range(20)]

    def _define_catalog(self, router):
        async def catalog(
                page_metadata: CatalogParams = Depends(CatalogParams),
        ):
            offset, limit = page_metadata.get_offset_and_limit()
            record = self.data[offset:offset + limit]
            items = [scenario.summary(record) for scenario in self.scenarios]
            items = list(zip(*items))
            items = [reduce_dict(item) for item in items]
            return CatalogResponse[self.io_types["summary_response"]](
                summaries=items,
                length=len(items),
                total=len(self.data),
            )

        BaseChapterEndPoint({
            "path": "/",
            "endpoint": catalog,
            "methods": ["GET"],
            "response_model": CatalogResponse[self.io_types["summary_response"]],
        })(router)

    def _define_detail(self, router):
        async def detail(
                item_id: int,
        ):
            try:
                record = self.data[item_id]
            except IndexError:
                raise HTTPException(status_code=404, detail="Item not found")
            result = reduce_dict([scenario.detail(record) for scenario in self.scenarios])
            return result

        BaseChapterEndPoint({
            "path": "/{item_id}",
            "endpoint": detail,
            "methods": ["GET"],
            "response_model": self.io_types["detail_response"],
        })(router)

    def _define_create(self, router):
        create_request = self.io_types["create_request"]

        async def create(
                request: create_request = Body(),
        ):
            record = reduce_dict([scenario.create({}, request) for scenario in self.scenarios])
            self.data.append(record)
            return record

        BaseChapterEndPoint({
            "path": "/",
            "endpoint": create,
            "methods": ["POST"],
        })(router)

    def _define_modify(self, router):
        modify_request = self.io_types["modify_request"]

        async def modify(
                item_id: int,
                request: modify_request = Body(),
        ):
            try:
                record = self.data[item_id]
            except IndexError:
                raise HTTPException(status_code=404, detail="Item not found")
            record = reduce_dict([scenario.modify(record, request) for scenario in self.scenarios])
            self.data.append(record)
            return record

        BaseChapterEndPoint({
            "path": "/{item_id}",
            "endpoint": modify,
            "methods": ["PATCH"],
        })(router)

    def _define_delete(self, router):
        async def delete(
                item_id: int,
        ):
            data = self.data.pop(item_id)
            return data

        BaseChapterEndPoint({
            "path": "/{item_id}",
            "endpoint": delete,
            "methods": ["DELETE"],
        })(router)
