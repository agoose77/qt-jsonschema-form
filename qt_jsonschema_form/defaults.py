from .numeric_defaults import numeric_defaults

def enum_defaults(schema):
    try:
        return schema["enum"][0]
    except IndexError:
        return None


def object_defaults(schema):
    return {k: compute_defaults(s) for k, s in schema["properties"].items()}


def array_defaults(schema):
    items_schema = schema['items']
    if isinstance(items_schema, dict):
        # in this case, it should be a list of items_schema
        return []

    # in this case, it's a tuple.
    return [compute_defaults(s) for s in schema["items"]]


defaults = {
    "array": array_defaults,
    "object": object_defaults,
    "numeric": numeric_defaults,
    "integer": numeric_defaults,
}


def compute_defaults(schema):
    if "default" in schema:
        return schema["default"]

    # Enum
    if "enum" in schema:
        return enum_defaults(schema)

    # Const
    if "const" in schema:
        return schema["const"]

    schema_type = schema["type"]

    if schema_type in defaults:
        return defaults[schema_type](schema)

    return None
