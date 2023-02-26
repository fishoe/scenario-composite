from typing import Callable

from core import actor as actor_type
from core import actor_role

ACTOR_TYPE = actor_type.BaseActor
ACTOR_MAP = dict[str, ACTOR_TYPE]
ROLE_TYPE = actor_role.BaseActorRole
ROLE_MAP = dict[str, ROLE_TYPE]
SCENE_LAMBDA = Callable[[list[ROLE_TYPE], list[ROLE_TYPE], any, dict[str, any], dict[str, any]], any]

HEADER_ROLE = actor_role.HeaderFieldRole
COOKIE_ROLE = actor_role.CookieFieldRole
QUERY_ROLE = actor_role.QueryFieldRole
JSON_ROLE = actor_role.JsonFieldRole

HEADER = "header"
COOKIE = "cookie"
QUERY = "query"
JSON = "json"


def apply_update_to_obj(obj, field_name, update):
    if isinstance(obj, dict):
        obj[field_name] = update
    else:
        setattr(obj, field_name, update)
    return obj


def classify_role(role: ROLE_TYPE, **kwargs) -> tuple[str, any]:
    if isinstance(role, HEADER_ROLE):
        name, field_spec = HEADER, role.get_field_spec(**kwargs)
    elif isinstance(role, COOKIE_ROLE):
        name, field_spec = COOKIE, role.get_field_spec(**kwargs)
    elif isinstance(role, QUERY_ROLE):
        name, field_spec = QUERY, role.get_field_spec(**kwargs)
    elif isinstance(role, JSON_ROLE):
        name, field_spec = JSON, role.get_field_spec(**kwargs)
    else:
        raise ValueError(f"Unknown role type: {role}")
    return name, field_spec


class Cast:
    def __init__(
            self,
            required: set[str] | str = None,
            optional: set[str] | str = None,
            excluded: set[str] = None,
    ):
        required = required or set()
        optional = optional or set()
        excluded = excluded or set()

        if not isinstance(required, set) and not required == '*':
            raise ValueError("required must be set or '*'")
        if not isinstance(optional, set) and not optional == '*':
            raise ValueError("optional must be set or '*'")
        if required == '*' and optional == '*':
            raise ValueError("required and optional can't be '*' at the same time")
        if not isinstance(excluded, set):
            raise ValueError("excluded must be set")

        if isinstance(required, set) and isinstance(optional, set) and (required & optional):
            raise ValueError("required and optional can't have common elements")
        if isinstance(required, set) and isinstance(optional, set) and (required | optional) & excluded:
            raise ValueError("required and optional can't have common elements with excluded")

        self.required = required
        self.optional = optional
        self.excluded = excluded

    def __call__(self, actors: ACTOR_MAP) -> tuple[ACTOR_MAP, ACTOR_MAP]:
        actors = self._exclude_actors(actors)
        if self.required == '*':
            optional, required = self._get_cast_actors('optional', actors)
        elif self.optional == '*':
            required, optional = self._get_cast_actors('required', actors)
        else:
            required, _ = self._get_cast_actors('required', actors)
            optional, _ = self._get_cast_actors('optional', actors)
        return required, optional

    def _get_cast_actors(
            self, position: str, actors: ACTOR_MAP
    ) -> tuple[ACTOR_MAP, ACTOR_MAP]:
        position_actor_names = getattr(self, position)
        selected, not_selected = {}, {}
        for actor_name, actor in actors.items():
            if actor_name in position_actor_names:
                selected[actor_name] = actor
            else:
                not_selected[actor_name] = actor
        return selected, not_selected

    def _exclude_actors(self, actors: ACTOR_MAP) -> ACTOR_MAP:
        if self.excluded:
            return {k: v for k, v in actors.items() if k not in self.excluded}
        else:
            return actors


def get_actor_role_by_role_name(role_name: str, actors: ACTOR_MAP) -> ROLE_MAP:
    return {actor_name: actor.get_role(role_name) for actor_name, actor in actors.items()
            if actor.has_role(role_name)}


class BaseScene:
    def __init__(self, role_name: str, cast: Cast, func: SCENE_LAMBDA = None):
        self.role_name = role_name
        self.cast = cast
        self.func = func

    def on_stage(self, actors: ACTOR_MAP):
        return self.cast(actors)

    def get_actor_role(self, actors: ACTOR_MAP) -> ROLE_MAP:
        role_name = self.role_name
        return get_actor_role_by_role_name(role_name, actors)

    def __call__(self, actors: ACTOR_MAP, data: any, req: any, extra: any):
        if self.func is None:
            raise NotImplementedError("func must be implemented")
        main_actors, sub_actors = self.on_stage(actors)
        main_roles = self.get_actor_role(main_actors)
        sub_roles = self.get_actor_role(sub_actors)
        return self.func([*main_roles.values()], [*sub_roles.values()], data, req, extra)


class BaseAPIScene(BaseScene):
    def __init__(self, role_name: str, cast: Cast, func: SCENE_LAMBDA = None):
        super().__init__(role_name, cast, func)

    def get_api_spec(self, actors: ACTOR_MAP, **kwargs) -> dict[str, list[any]]:
        main_actors, sub_actors = self.on_stage(actors)
        if self.role_name == "models":
            main_roles = get_actor_role_by_role_name("response", main_actors)
            sub_roles = get_actor_role_by_role_name("response", sub_actors)
        else:
            main_roles = self.get_actor_role(main_actors)
            sub_roles = self.get_actor_role(sub_actors)
        api_field_specs = {
            HEADER: [],
            COOKIE: [],
            QUERY: [],
            JSON: [],
        }
        for role_name, main_role in main_roles.items():
            docs_args = kwargs.get(role_name, {})
            name, field_spec = classify_role(main_role, **docs_args)
            api_field_specs[name].append(main_role.get_field_spec(required=True, **docs_args))

        for role_name, sub_role in sub_roles.items():
            docs_args = kwargs.get(role_name, {})
            name, field_spec = classify_role(sub_role, **docs_args)
            api_field_specs[name].append(sub_role.get_field_spec(required=False, **docs_args))

        return api_field_specs


class SummaryScene(BaseAPIScene):
    def __init__(self, cast: Cast):
        super().__init__("models", cast)

        def summary(main_roles: list[ROLE_TYPE], sub_roles: list[ROLE_TYPE], data: any, req: dict, extra: dict):
            result = {}
            for role in main_roles:
                value = role.get_value(data)
                k, v = role.translate(value)
                result[k] = v
            return result

        self.func = summary


class DetailScene(BaseAPIScene):
    def __init__(self, cast: Cast):
        super().__init__("models", cast)

        def detail(main_roles: list[ROLE_TYPE], sub_roles: list[ROLE_TYPE], data: any, req: dict, extra: dict):
            result = {}
            for role in main_roles + sub_roles:
                value = role.get_value(data)
                k, v = role.translate(value)
                result[k] = v
            return result

        self.func = detail


class CreateScene(BaseAPIScene):
    def __init__(self, cast: Cast):
        super().__init__("request", cast)

        def create(main_roles: list[ROLE_TYPE], sub_roles: list[ROLE_TYPE], data: any, req: dict, extra: dict):
            create_content = {}
            exceptions = []

            for role in main_roles + sub_roles:
                if role.name not in req:
                    continue
                value = role.get_value(req)
                k, v = role.translate(value)
                exception = role.validate(v)
                if exception:
                    exceptions.append(exception)
                create_content[k] = v

            if exceptions:
                raise ValueError()
            for k, v in create_content.items():
                apply_update_to_obj(data, k, v)
            return data

        self.func = create


class UpdateScene(BaseAPIScene):
    def __init__(self, cast: Cast):
        super().__init__("request", cast)

        def update(main_roles: list[ROLE_TYPE], sub_roles: list[ROLE_TYPE], data: any, request: dict, extra: dict):
            update_content = {}
            exceptions = []

            for role in main_roles + sub_roles:
                if role.name not in request:
                    continue
                value = role.get_value(request)
                k, v = role.translate(value)
                exception = role.validate(v)
                if exception:
                    exceptions.append(exception)
                update_content[k] = v

            if exceptions:
                raise ValueError()

            for k, v in update_content.items():
                apply_update_to_obj(data, k, v)
            return data

        self.func = update


class DeleteScene(BaseAPIScene):
    def __init__(self, cast: Cast):
        super().__init__("models", cast)

        def delete(main_roles: list[ROLE_TYPE], sub_roles: list[ROLE_TYPE], data: any, req: dict, extra: dict):
            if len(main_roles) > 1:
                raise ValueError("main role must be one")
            if not main_roles:
                return data
            main_role = main_roles[0]
            apply_update_to_obj(data, main_role.name, True)
            return data

        self.func = delete
