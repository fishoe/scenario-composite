import inspect
from types import FunctionType
from typing import TypeVar, Type, Optional

from fastapi import FastAPI, Depends, Header, Cookie, Request, Body
from pydantic import BaseModel, Field, create_model
from core.helper import db_helper

from sample.models import sample

DB_HELPER = db_helper.DBHelper
app = FastAPI()

# class Foo:
#     def __init__(self, a: str, b: str):
#         self.a = a
#         self.b = b
#
#     def __call__(self):
#         return self.a + self.b
#
#
# bar = TypeVar("bar", bound=Foo)
#
#
# def delegate(typ: Type[bar], *args, **kwargs):
#     inst = typ(*args, **kwargs)
#     return inst()
#
#
# print(delegate(Foo, 5, 6))


_m = create_model("Foo", a=(str, Field(None)), b=((Optional[str] | None), Field(None)))

@app.get("/my-endpoint", openapi_extra={
    "parameters":
        [
            {"name": "X-My-Header", "in": "header", "schema": {"type": "string", "default": "d"}, "required": True},
            {"name": "X-My-Cookie", "in": "cookie", "schema": {"type": "string", "default": "e"}, "required": True},
        ]})
async def my_endpoint(
        request: Request,
        t: _m = Body(),
        coobase: str = Cookie("drive"),
):
    cookie = request.cookies.get("X-My-Cookie")
    header = request.headers.get("X-My-Header")
    return {"cookie": coobase, "header": header}


from fastapi import APIRouter
from core import chapter, scenario, actor, actor_role, scene

API_SCENARIO = scenario.APIScenario
API_ACTOR = actor.APIActor
JSON_ROLE = actor_role.JsonFieldRole
MODEL_ROLE = actor_role.ModelFieldRole
HEADER_ROLE = actor_role.HeaderFieldRole
Cast = scene.Cast
SummaryScene = scene.SummaryScene
DetailScene = scene.DetailScene
CreateScene = scene.CreateScene
UpdateScene = scene.UpdateScene
DeleteScene = scene.DeleteScene

foo = API_SCENARIO(
    actors={
        "id": API_ACTOR("id", int, JSON_ROLE, MODEL_ROLE, JSON_ROLE),
        "name": API_ACTOR("name", str, JSON_ROLE, MODEL_ROLE, JSON_ROLE),
        "age": API_ACTOR("age", int, JSON_ROLE, MODEL_ROLE, JSON_ROLE),
        "address": API_ACTOR("address", str, JSON_ROLE, MODEL_ROLE, JSON_ROLE),
        "deleted": API_ACTOR("is_deleted", bool, JSON_ROLE, MODEL_ROLE, JSON_ROLE),
    },
    scenes={
        "summary": SummaryScene(Cast({"id", "name"})),
        "create": CreateScene(Cast({"name", "age", "address"})),
        "detail": DetailScene(Cast({"id", "name", "age", "address"})),
        "update": UpdateScene(Cast(None, "*", {"id", "deleted"}, )),
        "delete": DeleteScene(Cast({"deleted"})),
    })

chapter = chapter.APIChapter(
    "test",
    DB_HELPER(sample.User),
    scenarios=[foo]
)

app.include_router(chapter.route)
