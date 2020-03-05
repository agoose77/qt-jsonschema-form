from .numeric_defaults import numeric_defaults


def enum_defaults(schema):
    try:
        return schema["enum"][0]
    except IndexError:
        return None


def object_defaults(schema):
    return {k: compute_defaults(s) for k, s in schema["properties"].items()}


def list_defaults(schema):
    return []


def tuple_defaults(schema):
    return [compute_defaults(s) for s in schema["items"]]


def array_defaults(schema):
    if isinstance(schema['items'], dict):
        return list_defaults(schema)
    else:
        return tuple_defaults(schema)


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

    if "type" not in schema:
        # any value is valid.
        return {}

    schema_types = schema["type"]
    if not isinstance(schema_types, list):
        schema_types = [schema_types]

    for schema_type in schema_types:
        if schema_type in defaults:
            return defaults[schema_type](schema)

    return None
