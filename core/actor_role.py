from typing import Callable, Type, Optional

from pydantic import Field as PydanticField

STRING = "string"
HEADER = "header"
COOKIE = "cookie"


def get_value_from_obj(obj: any, attr: str) -> any:
    if isinstance(obj, dict):
        return obj.get(attr)
    else:
        return getattr(obj, attr)


def create_open_api_param_spec(
        name,
        typ,
        position,
        *,
        required: bool = False,
        default: any = None,
        description: str = None,
        enum: list[str] = None,
):
    param_spec = {
        "name": name,
        "in": position,
    }
    if required:
        param_spec["required"] = True
    if description:
        param_spec["description"] = description

    param_schema = {
        "type": typ,
    }
    if default is not None:
        param_schema["default"] = default
    if enum:
        param_spec["enum"] = enum

    param_spec["schema"] = param_schema

    return param_spec


class BaseActorRole:
    def __init__(
            self,
            name: str,
            *,
            translator: Callable[[str, any], any] = None,
            validator: Callable[[any], Exception | None] = None,
            **kwargs
    ):
        self.name = name
        self.translators = [translator] if translator else []
        self.validator = validator

    def get_value(self, obj) -> any:
        return get_value_from_obj(obj, self.name)

    def translate(self, value) -> any:
        if self.translators:
            k, v = self.name, value
            for t in self.translators:
                k, v = t(k, v)
            return k, v
        else:
            return self.name, value

    def validate(self, value) -> Exception | None:
        if self.validator:
            return self.validator(value)

    def get_field_spec(self, **kwargs):
        raise NotImplementedError


class BaseFieldRole(BaseActorRole):
    def __init__(
            self,
            name: str,
            *,
            typ: Type[any] = str,
            translator: Callable[[str, any], any] = None,
            validator: Callable[[any], Exception | None] = None,
            **kwargs
    ):
        super().__init__(name, translator=translator, validator=validator)
        self.type = typ
        self.field_args = kwargs

    def get_field_spec(self, required: bool = False, default: any = None, **kwargs):
        if required:
            typ = self.type
            default = ... if default is None else default
        else:
            typ = Optional[self.type]
        return self.name, (typ, PydanticField(default, **self.field_args))


class QueryFieldRole(BaseFieldRole):
    pass


class JsonFieldRole(BaseFieldRole):
    pass


class HeaderFieldRole(BaseActorRole):
    def __init__(
            self,
            name: str,
            translator: Callable[[str, any], any] = None,
            validator: Callable[[any], Exception | None] = None,
            **kwargs
    ):
        super().__init__(
            name,
            translator=translator,
            validator=validator,
            **kwargs
        )

    def get_field_spec(self, *, default: any = None, required: bool = False, description: str = None, **kwargs):
        return create_open_api_param_spec(
            self.name,
            STRING,
            HEADER,
            default=default,
            required=required,
            description=description,
        )


class CookieFieldRole(BaseActorRole):
    def __init__(
            self,
            name: str,
            translator: Callable[[str, any], any] = None,
            validator: Callable[[any], Exception | None] = None,
            **kwargs
    ):
        super().__init__(
            name,
            translator=translator,
            validator=validator,
            **kwargs
        )

    def get_field_spec(self, default: any = None, required: bool = False, description: str = None, **kwargs):
        return create_open_api_param_spec(
            self.name,
            STRING,
            COOKIE,
            required=required,
            default=default,
            description=description,
        )


class ModelFieldRole(BaseActorRole):
    def __init__(
            self,
            name: str,
            translator: Callable[[str, any], any] = None,
    ):
        super().__init__(
            name,
            translator=translator,
        )

    def get_field_spec(self, **kwargs):
        return None
