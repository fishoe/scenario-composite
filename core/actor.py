from typing import Type

from core import actor_role

RoleType = actor_role.BaseActorRole


class BaseActor:
    def __init__(self, roles: dict[str, RoleType] | None = None):
        self.roles = roles or {}

    def set_role(self, role_name, role: RoleType) -> None:
        self.roles[role_name] = role

    def get_role(self, role_name: str) -> RoleType | None:
        role = self.roles.get(role_name, None)
        if role is None:
            raise ValueError(f"role '{role_name}' not found")
        return role

    def has_role(self, role_name: str) -> bool:
        return role_name in self.roles


class APIActor(BaseActor):
    def __init__(
            self,
            name: str = None,
            typ: Type[any] = None,
            request_role: Type[RoleType] | None = None,
            model_role: Type[RoleType] | None = None,
            response_role: Type[RoleType] | None = None,
            *,
            request_name: str = None,
            model_name: str = None,
            response_name: str = None,
            request_typ: Type[any] = None,
            model_typ: Type[any] = None,
            response_typ: Type[any] = None
    ):
        super().__init__()
        if name is None and (request_role and model_role):
            raise ValueError("name is required if you use actor")
        self.name = {
            "request": request_name or name,
            "model": model_name or name,
            "response": response_name or request_name or name,
        }

        if typ is None and (request_role and model_role):
            raise ValueError("typ is required if you use actor")
        self.typ = {
            "request": request_typ or typ,
            "model": model_typ or typ,
            "response": response_typ or request_typ or typ,
        }

        if request_role is None:
            request_role = actor_role.JsonFieldRole
        request_role_inst = request_role(self.name.get("request"), typ=self.typ.get("request"))
        model_role_inst = model_role(self.name.get("model"))
        response_role_inst = response_role(self.name.get("response"), typ=self.typ.get("response")) if response_role \
            else request_role(self.name.get("response"), typ=self.typ.get("response"))
        if self.name.get("request") != self.name.get("model"):
            request_role_inst.translators.append(lambda k, v: (self.name.get("model"), v))
        if self.name.get("model") != self.name.get("response"):
            model_role_inst.translators.append(lambda k, v: (self.name.get("response"), v))
        self.set_role("request", request_role_inst)
        self.set_role("model", model_role_inst)
        self.set_role("response", response_role_inst)

    def get_role(self, role_name: str) -> RoleType | None:
        if role_name not in ("request", "model", "response"):
            raise ValueError("role_name must be one of 'request', 'model', 'response'")
        return self.roles.get(role_name, None)
