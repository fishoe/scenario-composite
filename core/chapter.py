from fastapi import APIRouter, Depends, Request
from starlette.responses import Response

from core import scenario
from core.request import pageable
from core.response import catalog
from core.helper.schema_helper import HeaderAndCookieSchemaHelper, QuerySchemaHelper, JsonSchemaHelper

CATALOG_RESPONSE = catalog.CatalogResponse
PAGEABLE_REQUEST = pageable.QueryPageParams
API_SCENARIO = scenario.APIScenario


def extract_field_from_dict_obj(obj, field_names: list, defaults=None):
    if defaults is None:
        defaults = {}
    return {name: obj.get(name, defaults.get(name, None)) for name in field_names}


def get_name_from_header_specs(fields):
    return [spec.get("name") for spec in fields]


def get_default_from_header_specs(fields):
    return {spec.get("name"): spec.get("schema", {}).get("default", None)
            for spec in fields}


class APIChapter:
    def __init__(
            self,
            prefix: str,
            scenarios: list[API_SCENARIO]
    ):
        self.name = prefix
        self.prefix = "/" + prefix
        self.scenarios = scenarios
        self.api_docs = {}

    def docs(self):
        if self.api_docs:
            return self.api_docs

        for i in ["summary", "detail", "create", "update", "delete"]:
            header_schema = HeaderAndCookieSchemaHelper()
            cookie_schema = HeaderAndCookieSchemaHelper()
            query_schema = QuerySchemaHelper()
            json_schema = JsonSchemaHelper()
            for _scenario in self.scenarios:
                if _scenario.has_scene(i):
                    scenario_api_spec = _scenario.get_api_spec(i)
                    name, spec = scenario_api_spec
                    header_schema.add_fields(spec.get("header", []))
                    cookie_schema.add_fields(spec.get("cookie", []))
                    query_schema.add_fields(spec.get("query", []))
                    if name is None:
                        json_schema.add_fields(spec.get("json", []))
                    elif isinstance(scenario_api_spec, list):
                        json_schema.add_nested_list_schema(name, spec.get("json", []))
                    else:
                        json_schema.add_nested_schema(name, spec.get("json", []))
            docs = {
                "header": header_schema.get_schemas(""),
                "cookie": cookie_schema.get_schemas(""),
                "query": query_schema.get_schemas(f"{self.name}_{i}_query"),
                "json": json_schema.get_schemas(f"{self.name}_{i}_json"),
            }
            self.api_docs[i] = docs
        return self.api_docs

    def _get_header_field(self, request: Request, scene_name: str):
        fields = self.api_docs.get(scene_name)["header"]
        names = get_name_from_header_specs(fields)
        defaults = get_default_from_header_specs(fields)
        return extract_field_from_dict_obj(request.headers, names, defaults)

    def _get_cookie_field(self, request: Request, scene_name: str):
        fields = self.api_docs.get(scene_name)["cookie"]
        names = get_name_from_header_specs(fields)
        defaults = get_default_from_header_specs(fields)
        return extract_field_from_dict_obj(request.cookies, names, defaults)

    def _get_docs_type(self, scene_name: str):
        self.docs()
        json = self.api_docs.get(scene_name, {}).get("json", None)
        query = self.api_docs.get(scene_name, {}).get("query", None)
        header = self.api_docs.get(scene_name, {}).get("header", [])
        cookie = self.api_docs.get(scene_name, {}).get("cookie", [])
        return json, query, header, cookie

    def _add_catalog_endpoint(self, router: APIRouter):
        if self.api_docs.get("summary", None) is None:
            self.docs()

        json, query, header, cookie = self._get_docs_type("summary")

        def _catalog(
                request: Request,
                page_param=Depends(PAGEABLE_REQUEST),
                query_param=Depends(query),
        ):
            header_param = self._get_header_field(request, "summary")
            cookie_param = self._get_cookie_field(request, "summary")

            offset, limit = page_param.get_offset_and_limit()

            # logic here

            return {}

        router.add_api_route(
            "",
            endpoint=_catalog,
            methods=["GET"],
            response_model=CATALOG_RESPONSE[json]
        )

    def _add_detail_endpoint(self, router: APIRouter):
        if self.api_docs.get("detail", None) is None:
            self.docs()

        json, query, header, cookie = self._get_docs_type("detail")

        def detail(
                item_id: int,
                request: Request,
                query_param=Depends(query),
        ):
            header_param = self._get_header_field(request, "detail")
            cookie_param = self._get_cookie_field(request, "detail")

            return Response()

        router.add_api_route(
            "/{item_id}",
            endpoint=detail,
            methods=["GET"],
            response_model=json
        )

    def _add_create_endpoint(self, router: APIRouter):
        if self.api_docs.get("create", None) is None:
            self.docs()

        json, query, header, cookie = self._get_docs_type("create")
        response_model = self.api_docs.get("detail", {}).get("json", {})

        def create(
                request: Request,
                json_param=Depends(json),
                query_param=Depends(query),
        ):
            header_param = self._get_header_field(request, "create")
            cookie_param = self._get_cookie_field(request, "create")

            return Response()

        router.add_api_route(
            "",
            endpoint=create,
            methods=["POST"],
            response_model=response_model
        )

    def _add_update_endpoint(self, router: APIRouter):
        if self.api_docs.get("update", None) is None:
            self.docs()

        json, query, header, cookie = self._get_docs_type("update")
        response_model = self.api_docs.get("detail", {}).get("json", {})

        def update(
                item_id: int,
                request: Request,
                json_param=Depends(json),
                query_param=Depends(query),
        ):
            header_param = self._get_header_field(request, "update")
            cookie_param = self._get_cookie_field(request, "update")

            return Response()

        router.add_api_route(
            "/{item_id}",
            endpoint=update,
            methods=["PUT"],
            response_model=response_model
        )

    def _add_delete_endpoint(self, router: APIRouter):
        if self.api_docs.get("delete", None) is None:
            self.docs()

        json, query, header, cookie = self._get_docs_type("delete")

        def delete(
                item_id: int,
                request: Request,
                query_param=Depends(query),
        ):
            header_param = self._get_header_field(request, "delete")
            cookie_param = self._get_cookie_field(request, "delete")

            return Response()

        router.add_api_route(
            "/{item_id}",
            endpoint=delete,
            methods=["DELETE"],
            response_model=json
        )

    @property
    def route(self):
        router = APIRouter(prefix=self.prefix)
        self._add_catalog_endpoint(router)
        self._add_detail_endpoint(router)
        self._add_create_endpoint(router)
        self._add_update_endpoint(router)
        self._add_delete_endpoint(router)
        return router
