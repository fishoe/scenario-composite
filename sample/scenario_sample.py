from typing import Callable

from core import actor_role, actor, scene

JSON_ROLE = actor_role.JsonFieldRole
MODEL_ROLE = actor_role.ModelFieldRole
Cast = scene.Cast

ReadScene = scene.DetailScene
CreateScene = scene.CreateScene
UpdateScene = scene.UpdateScene
DeleteScene = scene.DeleteScene


class Scenario:
    def __init__(self, scenes: dict, actors: dict[str, any] = None):
        self.scenes = scenes or {}
        self.actors = actors or {}

    def __call__(self, scene_name, data, req):
        _scene = self.scenes.get(scene_name, None)
        if _scene:
            return _scene(self.actors, data, req, {})
        return


db = [
    {"id": 1, "name": "John", "age": 20, "address": "123 Main St", "is_deleted": False},
    {"id": 2, "name": "Jane", "age": 21, "address": "456 Main St", "is_deleted": False},
    {"id": 3, "name": "Jack", "age": 22, "address": "789 Main St", "is_deleted": False},
    {"id": 4, "name": "Jill", "age": 23, "address": "101 Main St", "is_deleted": False},
    {"id": 5, "name": "Jenny", "age": 24, "address": "102 Main St", "is_deleted": False},
    {"id": 6, "name": "Penny", "age": 25, "address": "103 Main St", "is_deleted": False},
]
db_seq = 7
scenario = Scenario(
    actors={
        "id": actor.APIActor("id", int, JSON_ROLE, MODEL_ROLE, JSON_ROLE),
        "name": actor.APIActor("name", str, JSON_ROLE, MODEL_ROLE, JSON_ROLE),
        "age": actor.APIActor("age", int, JSON_ROLE, MODEL_ROLE, JSON_ROLE),
        "address": actor.APIActor("address", str, JSON_ROLE, MODEL_ROLE, JSON_ROLE),
        "deleted": actor.APIActor("is_deleted", bool, JSON_ROLE, MODEL_ROLE, JSON_ROLE),
    },
    scenes={
        "create": CreateScene(Cast({"name", "age", "address"})),
        "read": ReadScene(Cast({"id", "name", "age", "address"})),
        "update": UpdateScene(Cast({"name", "age", "address"})),
        "delete": DeleteScene(Cast({"deleted"})),
    },
)

a = scenario("read", db[0], {})
item = scenario("create", {}, {
    "name": "Jully",
    "age": 30
})
# scenario calls read scene
print(a)

item["id"] = db_seq
db_seq += 1
db.append(item)

scenario("update", db[0], {
    "name": "Jake",
    "age": 37
})

b = scenario("delete", db[4], {})
db[4] = b


for i in db:
    if not i.get("is_deleted"):
        print(i)
