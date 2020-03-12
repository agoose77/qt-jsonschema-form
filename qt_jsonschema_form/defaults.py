from .numeric_defaults import numeric_defaults


def enum_defaults(schema):
    try:
        return schema["enum"][0]
    except IndexError:
        return None


def object_defaults(schema):
    return {k: compute_defaults(s) for k, s in schema["properties"].items()}


def list_defaults(schema):
    # todo: respect unicity constraint.
    # todo: deal with intersection of schema, in case there is contains and items
    # e.g. add elements at end of tuple
    if "contains" in schema:
        return list_defaults_contains(schema)
    else:
        return list_defaults_no_contains(schema)


def list_defaults_contains(schema):
    minContains = schema.get("minContains", 1)
    if minContains <= 0:
        return []
    default = compute_defaults(schema["contains"])
    return [default] * minContains


def list_defaults_no_contains(schema):
    minItems = schema.get("minItems", 0)
    if minItems <= 0:
        return []
    default = compute_defaults(schema["items"])
    return [default] * minItems


def tuple_defaults(schema):
    return [compute_defaults(s) for s in schema["items"]]


def array_defaults(schema):
    if isinstance(schema['items'], dict):
        return list_defaults(schema)
    else:
        return tuple_defaults(schema)


def boolean_defaults(schema):
    return True


def string_defaults(schema):
    # todo: deal with pattern
    minLength = schema.get("minLength", 0)
    return " " * minLength


defaults = {
    "array": array_defaults,
    "object": object_defaults,
    "numeric": numeric_defaults,
    "integer": numeric_defaults,
    "boolean": boolean_defaults,
    "string": string_defaults,
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
