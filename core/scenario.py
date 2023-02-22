from core import scene, actor, actor_role

ACTOR_TYPE = actor.BaseActor
ROLE_TYPE = actor_role.BaseActorRole
SCENE_TYPE = scene.BaseScene
API_SCENE_TYPE = scene.BaseAPIScene


def get_attribute(obj, field_name):
    if isinstance(obj, dict):
        return obj.get(field_name, None)
    return getattr(obj, field_name, None)


def set_attribute(obj, field_name, value):
    if isinstance(obj, dict):
        obj[field_name] = value
    else:
        setattr(obj, field_name, value)
    return obj


class Scenario:
    def __init__(
            self,
            scenes: dict[str, SCENE_TYPE],
            actors: dict[str, ACTOR_TYPE],
    ):
        self.scenes = scenes
        self.actors = actors

    def _extract_data(self, position, data):
        raise NotImplementedError

    def _inject_data(self, position, obj, data):
        raise NotImplementedError

    def __call__(self, scene_name, data, req):
        _scene = self.scenes.get(scene_name, None)
        if _scene:
            return _scene(self.actors, data, req, {})
        return


class APIScenario(Scenario):

    def __init__(
            self,
            scenes: dict[str, API_SCENE_TYPE],
            actors: dict[str, ACTOR_TYPE],
            *,
            request_path: str | None = None,
            model_path: str | None = None,
            response_path: str | None = None
    ):
        super().__init__(scenes, actors)
        self.scenes = scenes
        self.path = {
            'request': request_path,
            'model': model_path,
            'response': response_path or request_path,
        }

    def _extract_data(self, position, data):
        path = self.path.get(position, None)
        if path:
            return get_attribute(data, path)
        return data

    def _inject_data(self, position, obj, data):
        path = getattr(self, position, None)
        if path:
            return set_attribute(obj, path, data)
        return data

    def extract_from_request(self, data):
        return self._extract_data('request', data)

    def extract_from_model(self, data):
        return self._extract_data('model', data)

    def inject_to_response(self, response, data):
        return self._inject_data('response', response, data)

    def inject_to_model(self, model, data):
        return self._inject_data('model', model, data)

    def get_api_spec(self, scene_name):
        try:
            _scene = self.scenes[scene_name]
        except KeyError:
            raise ValueError(f"'{scene_name}' is not in scenario scenes")
        return _scene.get_api_spec(self.actors)
