from core import actor_role, actor, scene, scenario

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
    {"id": 1, "name": "John", "age": 20, "address": "123 Main St", "is_deleted": False},
    {"id": 2, "name": "Jane", "age": 21, "address": "456 Main St", "is_deleted": False},
    {"id": 3, "name": "Jack", "age": 22, "address": "789 Main St", "is_deleted": False},
    {"id": 4, "name": "Jill", "age": 23, "address": "101 Main St", "is_deleted": False},
    {"id": 5, "name": "Jenny", "age": 24, "address": "102 Main St", "is_deleted": False},
    {"id": 6, "name": "Penny", "age": 25, "address": "103 Main St", "is_deleted": False},
]

db_seq = 7

api_scenario = API_SCENARIO(
    actors={
        "id": API_ACTOR("id", int, HEADER_ROLE, MODEL_ROLE, JSON_ROLE),
        "name": API_ACTOR("name", str, JSON_ROLE, MODEL_ROLE, JSON_ROLE),
        "age": API_ACTOR("age", int, JSON_ROLE, MODEL_ROLE, JSON_ROLE),
        "address": API_ACTOR("address", str, JSON_ROLE, MODEL_ROLE, JSON_ROLE),
        "deleted": API_ACTOR("is_deleted", bool, JSON_ROLE, MODEL_ROLE, JSON_ROLE),
    },
    scenes={
        "summary": SummaryScene(Cast({"id", "name"})),
        "create": CreateScene(Cast({"name", "age", "address"})),
        "detail": DetailScene(Cast({"id", "name", "age", "address"})),
        "update": UpdateScene(Cast(None, "*", {"id"},)),
        "delete": DeleteScene(Cast({"deleted"})),
    })

summary_spec = api_scenario.get_api_spec("summary")
create_spec = api_scenario.get_api_spec("create")
detail_spec = api_scenario.get_api_spec("detail")
update_spec = api_scenario.get_api_spec("update")
delete_spec = api_scenario.get_api_spec("delete")
