import inspect
from types import FunctionType
from typing import TypeVar, Type

from fastapi import FastAPI, Depends, Header, Cookie, Request
from pydantic import BaseModel, Field

app = FastAPI()


class Foo:
    def __init__(self, a: str, b: str):
        self.a = a
        self.b = b

    def __call__(self):
        return self.a + self.b


bar = TypeVar("bar", bound=Foo)


def delegate(typ: Type[bar], *args, **kwargs):
    inst = typ(*args, **kwargs)
    return inst()


print(delegate(Foo, 5, 6))


@app.get("/my-endpoint", openapi_extra={
    "parameters":
        [
            {"name": "X-My-Header", "in": "header", "schema": {"type": "string", "default": "d"}, "required": True},
            {"name": "X-My-Cookie", "in": "cookie", "schema": {"type": "string", "default": "e"}, "required": True},
        ]}
         )
async def my_endpoint(
        request: Request,
        coobase: str = Cookie("drive"),
):
    print(request.headers)
    print(request.cookies)
    cookie = request.cookies.get("X-My-Cookie")
    header = request.headers.get("X-My-Header")
    return {"cookie": coobase, "header": header}
