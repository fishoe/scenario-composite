from typing import Callable

from core import actor_role as role
from core import actor as actor_type

ACTOR_TYPE = actor_type.BaseActor
ROLE_TYPE = role.BaseActorRole
SCENE_LAMBDA = Callable[[list[ROLE_TYPE], list[ROLE_TYPE], any, dict[str, any], dict[str, any]], any]


def apply_update_to_obj(obj, field_name, update):
    if isinstance(obj, dict):
        obj[field_name] = update
    else:
        setattr(obj, field_name, update)
    return obj


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

    def __call__(
            self, actors: dict[str, ACTOR_TYPE]
    ) -> tuple[list[ACTOR_TYPE], list[ACTOR_TYPE]]:
        actors = self._exclude_actors(actors)
        if self.required == '*':
            optional, required = self._get_cast_actors('optional', actors)
        elif self.optional == '*':
            required, optional = self._get_cast_actors('required', actors)
        else:
            required, _ = self._get_cast_actors('required', actors)
            optional, _ = self._get_cast_actors('optional', actors)
        return list(required.values()), list(optional.values())

    def _get_cast_actors(
            self, position: str, actors: dict[str, ACTOR_TYPE]
    ) -> tuple[dict[str, ACTOR_TYPE], dict[str, ACTOR_TYPE]]:
        position_actor_names = getattr(self, position)
        selected, not_selected = {}, {}
        for actor_name, actor in actors.items():
            if actor_name in position_actor_names:
                selected[actor_name] = actor
            else:
                not_selected[actor_name] = actor
        return selected, not_selected

    def _exclude_actors(self, actors: dict[str, ACTOR_TYPE]) -> dict[str, ACTOR_TYPE]:
        if self.excluded:
            return {k: v for k, v in actors.items() if k not in self.excluded}
        else:
            return actors


class BaseScene:
    def __init__(self, role_name: str, cast: Cast, func: SCENE_LAMBDA = None):
        self.role_name = role_name
        self.cast = cast
        self.func = func

    def on_stage(self, actors):
        return self.cast(actors)

    def get_actor_role(self, actors: list[ACTOR_TYPE]):
        role_name = self.role_name
        return [actor.get_role(role_name) for actor in actors if actor.has_role(role_name)]

    def __call__(self, actors, data, req, extra):
        if self.func is None:
            raise NotImplementedError("func must be implemented")
        main_actors, sub_actors = self.on_stage(actors)
        main_roles = self.get_actor_role(main_actors)
        sub_roles = self.get_actor_role(sub_actors)
        return self.func(main_roles, sub_roles, data, req, extra)


class SummaryScene(BaseScene):
    def __init__(self, cast: Cast):
        super().__init__("model", cast)

        def summary(main_roles: list[ROLE_TYPE], sub_roles: list[ROLE_TYPE], data: any, req: dict, extra: dict):
            result = {}
            for actor_role in main_roles:
                value = actor_role.get_value(data)
                k, v = actor_role.translate(value)
                result[k] = v
            return result

        self.func = summary


class DetailScene(BaseScene):
    def __init__(self, cast: Cast):
        super().__init__("model", cast)

        def detail(main_roles: list[ROLE_TYPE], sub_roles: list[ROLE_TYPE], data: any, req: dict, extra: dict):
            result = {}
            for actor_role in main_roles + sub_roles:
                value = actor_role.get_value(data)
                k, v = actor_role.translate(value)
                result[k] = v
            return result

        self.func = detail


class CreateScene(BaseScene):
    def __init__(self, cast: Cast):
        super().__init__("request", cast)

        def create(main_roles: list[ROLE_TYPE], sub_roles: list[ROLE_TYPE], data: any, req: dict, extra: dict):
            create_content = {}
            exceptions = []

            for actor_role in main_roles + sub_roles:
                if actor_role.name not in req:
                    continue
                value = actor_role.get_value(req)
                k, v = actor_role.translate(value)
                exception = actor_role.validate(v)
                if exception:
                    exceptions.append(exception)
                create_content[k] = v

            if exceptions:
                raise ValueError()
            for k, v in create_content.items():
                apply_update_to_obj(data, k, v)
            return data

        self.func = create


class UpdateScene(BaseScene):
    def __init__(self, cast: Cast):
        super().__init__("request", cast)

        def update(main_roles: list[ROLE_TYPE], sub_roles: list[ROLE_TYPE], data: any, req: dict, extra: dict):
            update_content = {}
            exceptions = []

            for actor_role in main_roles + sub_roles:
                if actor_role.name not in req:
                    continue
                value = actor_role.get_value(req)
                k, v = actor_role.translate(value)
                exception = actor_role.validate(v)
                if exception:
                    exceptions.append(exception)
                update_content[k] = v

            if exceptions:
                raise ValueError()

            for k, v in update_content.items():
                apply_update_to_obj(data, k, v)
            return data

        self.func = update


class DeleteScene(BaseScene):
    def __init__(self, cast: Cast):
        super().__init__("model", cast)

        def delete(main_roles: list[ROLE_TYPE], sub_roles: list[ROLE_TYPE], data: any, req: dict, extra: dict):
            if len(main_roles) != 1:
                raise ValueError("main_roles must be one in delete scene")
            main_role = main_roles[0]
            apply_update_to_obj(data, main_role.name, True)
            return data

        self.func = delete
