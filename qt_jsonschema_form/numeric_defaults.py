import math
from copy import deepcopy

import jsonschema


"""function to compute a number default value. If min and max are set,
a number near their average is chosen. Otherwise, a number as close as
possible from the only bound. Otherwise 0. """


def numeric_defaults(schema):
    value = _numeric_defaults(schema)
    try:
        jsonschema.validate(value, schema)
        return value
    except jsonschema.ValidationError:
        return None


def _numeric_defaults(schema):
    schema = deepcopy(schema)
    # Setting min and max according to exclusive min/max
    if "exclusiveMinimum" in schema:
        if "minimum" in schema:
            schema["minimum"] = max(
                schema["minimum"], schema["exclusiveMinimum"])
        else:
            schema["minimum"] = schema["exclusiveMinimum"]
    if "exclusiveMaximum" in schema:
        if "maximum" in schema:
            schema["maximum"] = max(
                schema["maximum"], schema["exclusiveMaximum"])
        else:
            schema["maximum"] = schema["exclusiveMaximum"]

    if "multipleOf" in schema:
        return _numeric_defaults_multiple_of(schema)
    else:
        return _numeric_defaults_not_multiple_of(schema)


def _numeric_defaults_not_multiple_of(schema):
    if "minimum" in schema and "maximum" in schema:
        middle = (schema["minimum"] + schema["maximum"]) / 2
        if schema["type"] == "integer":
            middle_ = math.floor(middle)
            try:
                jsonschema.validate(middle_, schema)
                return middle_
            except jsonschema.ValidationError:
                return math.ceil(middle)
        else:
            return middle
    elif "minimum" in schema:
        # no maximum
        m = schema["minimum"]
        if schema["type"] == "integer":
            m = math.ceil(m)
        if schema["exclusiveMinimum"] == m:
            m += 1
        return m
    elif "maximum" in schema:
        # no minimum
        M = schema["maximum"]
        if schema["type"] == "integer":
            M = math.ceil(M)
        if schema["exclusiveMaximum"] == M:
            M -= 1
        return M
    else:
        # neither min nor max
        return 0


def _numeric_defaults_multiple_of(schema):
    multipleOf = schema["multipleOf"]
    if schema["type"] == "integer" and multipleOf != math.floor(multipleOf):
        # todo: find an integral multiple of a float distinct from 0
        return 0
    if "minimum" in schema and "maximum" in schema:
        middle = (schema["minimum"] + schema["maximum"]) / 2
        middle_ = math.floor(middle//multipleOf) * multipleOf
        try:
            jsonschema.validate(middle_, schema)
            return middle_
        except jsonschema.ValidationError:
            return middle_ + multipleOf
    elif "minimum" in schema:
        # no maximum
        m = schema["minimum"]
        m = (math.ceil(m / multipleOf)) * multipleOf
        if schema["exclusiveMinimum"] == m:
            m += multipleOf
        return m
    elif "maximum" in schema:
        # no minimum
        M = schema["maximum"]
        M = (math.floor(M / multipleOf)) * multipleOf
        if schema["exclusiveMinimum"] == M:
            M -= multipleOf
        return M
    else:
        # neither min nor max
        return 0
