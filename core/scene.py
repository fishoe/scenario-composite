from fastapi import APIRouter
from core import actor
from core import actor_role as role


class Cast:
    def __init__(
            self,
            required: set[str] = None,
            optional: set[str] = None,
            excluded: set[str] = None,
    ):
        required = required or set()
        optional = optional or set()
        excluded = excluded or set()
        if required & optional:
            raise ValueError("required and optional can't have common elements")
        if (required | optional) & excluded:
            raise ValueError("required and optional can't have common elements with excluded")
        self.required_actors = required or set()
        self.optional_actors = optional or set()
        self.excluded_actors = excluded or set()

    def cast_required(self, actors: dict[str, any]) -> dict[str, any]:
        return {k: v for k, v in actors.items() if k in self.required_actors}

    def cast_optional(self, actors: dict[str, any]) -> dict[str, any]:
        return {k: v for k, v in actors.items() if k in self.optional_actors}

    def cast_excluded(self, actors: dict[str, any]) -> dict[str, any]:
        return {k: v for k, v in actors.items() if k not in self.excluded_actors}


class Scene:
    def __init__(self, cast, func):
        self.func = func
        self.cast = cast

    def get_scene_actors(self, actors):
        return self.cast.required_actors(actors)

    def __call__(self, actors, data, req):
        actors = self.get_scene_actors(actors)
        return [func(actors, data, req) for func in actors]


class BaseScene:
    def __init__(self, cast, func):
        self.func = func
        self.cast = cast

    def get_scene_actors(self, actors):
        return [v for k, v in actors.items() if k in self.cast.required_actors]

    def __call__(self, actors, data, req):
        raise NotImplementedError


class ReadScene(BaseScene):
    def __init__(self, cast, func):
        super().__init__(cast, func)

    def __call__(self, actors, data, req):
        actors = self.get_scene_actors(actors)
        roles = [a.get_model_role for a in actors]
        return self.func(roles, data, req)


class CreateScene(BaseScene):
    def __init__(self, cast, func):
        super().__init__(cast, func)

    def __call__(self, actors, data, req):
        actors = self.get_scene_actors(actors)
        roles = [a.get_request_role for a in actors]
        return self.func(roles, data, req)


def read_item(fields: list[role.BaseActorRole], model, req):
    item = {}
    for field in fields:
        value = field.get_value(model)
        k, v = field.translate(value)
        item[k] = v
    return item


def create_item(actors, obj, data):
    for field in actors:
        value = field.get_value(data)
        k, v = field.translate(value)
        obj[k] = v
    return obj


def update_item(actors, obj, data):
    for field in actors:
        value = field.get_value(data)
        k, v = field.translate(value)
        obj[k] = v
    return obj


class Scenario:
    def __init__(self, scenes: dict, actors: dict[str, any] = None):
        self.scenes = scenes or {}
        self.actors = actors or {}

    def __call__(self, scene_name, data, req):
        scene = self.scenes.get(scene_name, None)
        if scene:
            return scene(self.actors, data, req)
        return

    def get_scene_actors(self, scene_name):
        scene = self.scenes.get(scene_name, None)
        if scene:
            return scene.get_scene_actors(self.actors)
        return


db = [
    {"id": 1, "name": "John", "age": 20, "address": "123 Main St"},
    {"id": 2, "name": "Jane", "age": 21, "address": "456 Main St"},
    {"id": 3, "name": "Jack", "age": 22, "address": "789 Main St"},
    {"id": 4, "name": "Jill", "age": 23, "address": "101 Main St"},
    {"id": 5, "name": "Jenny", "age": 24, "address": "102 Main St"},
    {"id": 6, "name": "Penny", "age": 25, "address": "103 Main St"},
]

db_seq = 7

scenario = Scenario(
    scenes={
        "create": CreateScene(Cast({"name", "age"}), create_item),
        "read": ReadScene(Cast({"id", "name", "age"}), read_item),
        "update": CreateScene(Cast({"name", "age"}), update_item),
        "delete": Scene(Cast(), lambda d, r: "Hello World!")
    },
    actors={
        "id": actor.APIActor("id", int, role.JsonFieldRole, role.ModelFieldRole, role.JsonFieldRole),
        "name": actor.APIActor("name", str, role.JsonFieldRole, role.ModelFieldRole, role.JsonFieldRole),
        "age": actor.APIActor("age", int, role.JsonFieldRole, role.ModelFieldRole, role.JsonFieldRole),
    }
)

a = scenario("read", db[0], {})

print(a)

item = scenario("create", {}, {
    "name": "Jully",
    "age": 30
})
item["id"] = db_seq
db_seq += 1
db.append(item)

scenario("update", db[0], {
    "name": "Jake",
    "age": 37
})

for i in db:
    print(i)
