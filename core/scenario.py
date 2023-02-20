from typing import Type, Callable

from core import field as field_types


class BaseScenario:
    def __init__(self, actors: list[field_types.BaseField], scenes: list, effects: list):
        self.actors = actors
        self.scenes = scenes
        self.effects = effects


class Scenario:
    REQUIRED = field_types.UseInScenario.REQUIRED
    OPTIONAL = field_types.UseInScenario.OPTIONAL
    DISABLED = field_types.UseInScenario.DISABLED

    def __init__(self, fields: list[field_types.BaseField], ):
        self.fields = fields

    def summary(self, items):
        return [
            dict([field.response_translate(item) for field in self._common_scenario_filter("use_in_summary")])
            for item in items
        ]

    def detail(self, item):
        return dict([field.response_translate(item) for field in self._common_scenario_filter("use_in_detail")])

    def modify(self, obj, request):
        modify_fields = self._common_scenario_filter("use_in_modify")
        return self._common_logic_for_create_and_modify(obj, request, modify_fields)

    def create(self, obj, request):
        create_fields = self._common_scenario_filter("use_in_create")
        return self._common_logic_for_create_and_modify(obj, request, create_fields)

    @staticmethod
    def _common_logic_for_create_and_modify(obj, request, fields):
        translated_map = dict([field.request_translate(request) for field in fields
                               if field.get_value_from_request(request) is not None])
        exceptions = [field.validate(translated_map) for field in fields if field.validator]
        if exceptions:
            raise Exception  # TODO: make modify exception
        for field in fields:
            obj = field.apply(obj, translated_map)
        return obj

    def delete(self, obj):
        raise NotImplementedError

    def summary_response(self):
        return dict(self._common_scenario_request("use_in_summary"))

    def detail_response(self):
        return dict(self._common_scenario_request("use_in_detail"))

    def modify_request(self):
        return dict(self._common_scenario_request("use_in_modify"))

    def create_request(self):
        return dict(self._common_scenario_request("use_in_create"))

    def _common_scenario_filter(self, scenario: str) -> list[field_types.BaseField]:
        return [field for field in self.fields if getattr(field, scenario) is not Scenario.DISABLED]

    def _common_scenario_request(self, scenario: str):
        return [field.request_field(getattr(field, scenario)) for field in self._common_scenario_filter(scenario)]
