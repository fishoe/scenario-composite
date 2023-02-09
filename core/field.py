from typing import Type, Callable

from enum import Enum
from pydantic import Field as PydanticField
from fastapi import Query as FastAPIQuery


class UseInScenario(Enum):
    REQUIRED = "REQUIRED"
    OPTIONAL = "OPTIONAL"
    DISABLED = "DISABLED"


class ParameterType(Enum):
    HEADER = "HEADER"
    QUERY = "QUERY"
    BODY = "BODY"
    COOKIE = "COOKIE"


class BaseField:
    def __init__(
            self,
            name: str,
            model_field: str,
            cls_type: Type[any],
            parameter_type: ParameterType = ParameterType.BODY,
            use_in: dict[str, UseInScenario] | None = None,
            request_args: dict = None,
            request_translator: Callable[[str, any], tuple[str, any]] = None,
            response_translator: Callable[[str, any], tuple[str, any]] = None,
            validator: Callable[[any], Exception | None] | None = None,
    ):
        if use_in is None:
            use_in = {}
        self.name = name
        self.model_field = model_field
        self.type = cls_type
        self.parameter_type = parameter_type
        self.request_args = request_args or {}
        self.use_in_summary = use_in.get("summary", UseInScenario.DISABLED)
        self.use_in_detail = use_in.get("detail", UseInScenario.REQUIRED)
        self.use_in_modify = use_in.get("modify", UseInScenario.OPTIONAL)
        self.use_in_create = use_in.get("create", UseInScenario.REQUIRED)
        self.request_translator: Callable[[str, cls_type], tuple[str, any]] = \
            request_translator or (lambda k, v: (self.model_field, v))
        self.response_translator: Callable[[str, any], tuple[str, cls_type]] = \
            response_translator or (lambda k, v: (self.name, v))
        self.validator: Callable[[cls_type], Exception | None] | None = validator

    def get_value_from_request(self, request) -> any:
        # TODO : collect common code
        if isinstance(request, dict):
            return request.get(self.name)
        else:
            return getattr(request, self.name)

    def get_value_from_model(self, obj) -> any:
        if isinstance(obj, dict):
            return obj.get(self.model_field)
        else:
            return getattr(obj, self.model_field)

    def request_translate(self, obj) -> (str, any):
        value = self.get_value_from_request(obj)
        return self.request_translator(self.name, value)

    def response_translate(self, obj) -> (str, any):
        value = self.get_value_from_model(obj)
        return self.response_translator(self.name, value)

    def validate(self, obj) -> Exception | None:
        value = self.get_value_from_model(obj)
        if self.validator is None:
            return
        try:
            self.validator(value)
        except Exception as e:
            return e

    def apply(self, obj, request) -> any:
        if self.name not in request:
            return obj
        value = self.get_value_from_request(request)
        if isinstance(obj, dict):
            obj[self.model_field] = value
        else:
            setattr(obj, self.model_field, value)
        return obj

    def _pydantic_field(self, optional: UseInScenario = UseInScenario.REQUIRED):
        if optional is UseInScenario.OPTIONAL:
            return self.name, (self.type | None, PydanticField(None, **self.request_args))
        else:
            return self.name, (self.type, PydanticField(**self.request_args))

    def _query_field(self, optional: UseInScenario = UseInScenario.REQUIRED):
        if optional is UseInScenario.OPTIONAL:
            return self.name, (self.type | None, FastAPIQuery(None, **self.request_args))
        else:
            return self.name, (self.type, FastAPIQuery(**self.request_args))

    def _header_field(self, optional: UseInScenario = UseInScenario.REQUIRED):
        raise NotImplementedError

    def request_field(self, use_in: UseInScenario):
        if self.parameter_type == ParameterType.BODY:
            return self._pydantic_field(use_in)
        elif self.parameter_type == ParameterType.QUERY:
            return self._query_field(use_in)
        elif self.parameter_type == ParameterType.HEADER:
            raise NotImplementedError
        else:
            raise NotImplementedError

    def response_field(self):
        return self._pydantic_field()
