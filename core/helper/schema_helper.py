from pydantic import create_model


class APISchemaHelperBase:
    def add_field(self, docs_field):
        raise NotImplementedError

    def add_fields(self, docs_fields):
        raise NotImplementedError

    def get_schemas(self, model_name):
        raise NotImplementedError


class HeaderAndCookieSchemaHelper(APISchemaHelperBase):
    def __init__(self):
        self.fields = []

    def add_field(self, docs_field):
        self.fields.append(docs_field)

    def add_fields(self, docs_fields):
        self.fields.extend(docs_fields)

    def get_schemas(self, model_name):
        return self.fields


class QuerySchemaHelper(APISchemaHelperBase):

    def __init__(self):
        self.fields = {}

    def add_field(self, docs_field):
        name, field = docs_field
        self.fields[name] = field

    def add_fields(self, docs_fields):
        for i in docs_fields:
            self.add_field(i)

    def get_schemas(self, model_name):
        return create_model(model_name, **self.fields)


class JsonSchemaHelper(APISchemaHelperBase):

    def __init__(self):
        self.fields = {}
        self.nested_field = {}
        self.nested_list_field = {}

    def add_field(self, field):
        name, field = field
        self.fields[name] = field

    def add_fields(self, fields):
        for i in fields:
            self.add_field(i)

    def add_nested_schema(self, name, fields):
        if name in self.nested_field:
            schema_helper = self.nested_field[name]
        else:
            schema_helper = JsonSchemaHelper()
        schema_helper.add_fields(fields)
        self.nested_field[name] = schema_helper

    def add_nested_list_schema(self, name, fields):
        if name in self.nested_list_field:
            schema_helper = self.nested_list_field[name]
        else:
            schema_helper = JsonSchemaHelper()
        schema_helper.add_field(fields)
        self.nested_list_field[name] = schema_helper

    def get_schemas(self, model_name):
        for name, schema_helper in self.nested_field.items():
            self.fields[name] = (schema_helper.get_schemas(name), ...)
        for name, schema_helper in self.nested_list_field.items():
            self.fields[name] = (list[schema_helper.get_schemas(f"{model_name}_{name}")], ...)
        return create_model(model_name, **self.fields)


class NestedJsonListSchemaHelper(JsonSchemaHelper):
    pass
