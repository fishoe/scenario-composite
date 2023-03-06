from core import actor_role, actor, scene, scenario
from core.helper.schema_helper import HeaderAndCookieSchemaHelper, QuerySchemaHelper, JsonSchemaHelper

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

db = [
    {"id": 1, "name": "John", "age": 20, "address": "123 Main St", "items": [
        {
            "id": 1,
            "name": "sword",
            "price": 100,
        }, {
            "id": 2,
            "name": "shield",
            "price": 900,
        }, {
            "id": 3,
            "name": "armor",
            "price": 3000,
        }
    ], "is_deleted": False},
    {"id": 2, "name": "Jane", "age": 21, "address": "456 Main St", "items": {}, "is_deleted": False},
    {"id": 3, "name": "Jack", "age": 22, "address": "789 Main St", "is_deleted": False},
    {"id": 4, "name": "Jill", "age": 23, "address": "101 Main St", "is_deleted": False},
    {"id": 5, "name": "Jenny", "age": 24, "address": "102 Main St", "is_deleted": False},
    {"id": 6, "name": "Penny", "age": 25, "address": "103 Main St", "is_deleted": False},
]

db_seq = 7


def db_add(data):
    global db
    global db_seq
    data["id"] = db_seq
    db.append(data)
    db_seq += 1


def db_update(idx, data):
    global db
    db[idx] = data


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
        "create": CreateScene(Cast({"name", "age"})),
        "detail": DetailScene(Cast({"id", "name", "age"})),
        "update": UpdateScene(Cast(None, "*", {"id"}, )),
        "delete": DeleteScene(Cast({"deleted"})),
    })

bar = API_SCENARIO(
    actors={
        "my_header": API_ACTOR("my_header", str, HEADER_ROLE, HEADER_ROLE, HEADER_ROLE),
        "name": API_ACTOR("name", str, JSON_ROLE, MODEL_ROLE, JSON_ROLE),
        "price": API_ACTOR("price", int, JSON_ROLE, MODEL_ROLE, JSON_ROLE),
    },
    scenes={
        "detail": DetailScene(Cast({"my_header", "id", "name", "price"})),
    },
    response_path="items",
    model_path="items"
)


# catalog = chapter1.catalog(db[:])
# print("catalog: ")
# for i in catalog:
#     print(i)
# print()
#
# detail = chapter1.detail(db[0])
# print("detail: ", detail)
# print()
#
# detail2 = chapter2.detail(db[0])
# print("detail2: ", detail2)
# print()
#
# create = chapter1.create({
#     "name": "John",
#     "age": 20,
#     "address": "kj kj",
# })
# db_add(create)
# idx = 3
# update = chapter1.update(db[idx], {
#     "id": 7,
#     "name": "pipi",
#     "age": 5,
# })
# print("update: ", update)
# db_update(idx, update)
#
# delete = chapter1.delete(db[0])
# db[0] = delete
#
# for record in db:
#     if "is_deleted" not in record or not record["is_deleted"]:
#         print(record)
#
# print()
# chapter1.docs()

