from copy import deepcopy

from jsonschema.validators import validator_for

from . import widgets
from .defaults import compute_defaults
from typing import Dict, Any

def get_widget_state(schema, state=None):
    """A JSON object. Either the state given in input if any, otherwise
    the default value satisfying the current type.

    """
    if state is None:
        return compute_defaults(schema)
    return state


def get_schema_type(schema: dict) -> str:
    return schema['type']


class WidgetBuilder:
    default_widget_map = {
        "boolean": {"checkbox": widgets.CheckboxSchemaWidget, "enum": widgets.EnumSchemaWidget},
        "object": {"object": widgets.ObjectSchemaWidget, "enum": widgets.EnumSchemaWidget},
        "number": {"spin": widgets.SpinDoubleSchemaWidget, "text": widgets.TextSchemaWidget, "enum": widgets.EnumSchemaWidget},
        "string": {"textarea": widgets.TextAreaSchemaWidget, "text": widgets.TextSchemaWidget, "password": widgets.PasswordWidget,
                   "filepath": widgets.FilepathSchemaWidget, "dirpath": widgets.DirectorypathSchemaWidget, "colour": widgets.ColorSchemaWidget, "enum": widgets.EnumSchemaWidget},
        "integer": {"spin": widgets.SpinSchemaWidget, "text": widgets.TextSchemaWidget, "range": widgets.IntegerRangeSchemaWidget,
                    "enum": widgets.EnumSchemaWidget},
        "array": {"array": widgets.ArraySchemaWidget, "enum": widgets.EnumSchemaWidget}
    }

    default_widget_variants = {
        "boolean": "checkbox",
        "object": "object",
        "array": "array",
        "number": "spin",
        "integer": "spin",
        "string": "text",
    }

    widget_variant_modifiers = {
        "string": lambda schema: schema.get("format", "text")
    }

    def __init__(self, validator_cls=None):
        """validator_cls -- A validator, as in jsonschema library. Schemas are
        supposed to be valid for it."""
        self.widget_map = deepcopy(self.default_widget_map)
        self.validator_cls = validator_cls

    def create_form(self, schema: dict, ui_schema: dict = {}, state=None, parent=None) -> widgets.SchemaWidgetMixin:
        validator_cls = self.validator_cls
        if validator_cls is None:
            validator_cls = validator_for(schema)

        validator_cls.check_schema(schema)
        validator = validator_cls(schema)
        schema_widget = self.create_widget(schema, ui_schema, state)
        form = widgets.FormWidget(schema_widget, parent)

        def validate(data):
            """Show the error widget iff there are errors, and the error messages
            in it."""
            form.clear_errors()
            errors = [*validator.iter_errors(data)]

            if errors:
                form.display_errors(errors)

            for err in errors:
                schema_widget.handle_error(err.path, err)

        schema_widget.on_changed.connect(validate)

        return form

    def create_widget(self, schema: dict, ui_schema: dict, state=None) -> widgets.SchemaWidgetMixin:
        schema_type = get_schema_type(schema)
        widget_variant = self.get_widget_variant(schema_type, schema, ui_schema)
        widget_cls = self.widget_map[schema_type][widget_variant]

        widget = widget_cls(schema, ui_schema, self)

        default_state = get_widget_state(schema, state)
        if default_state is not None:
            widget.state = default_state
        return widget

    def get_widget_variant(self, schema_type: str, schema: Dict[str, Any], ui_schema: Dict[str, Any]) -> str:
        try:
            default_variant = self.widget_variant_modifiers[schema_type](schema)
        except KeyError:
            default_variant = self.default_widget_variants[schema_type]

        if "enum" in schema:
            default_variant = "enum"

        return ui_schema.get('ui:widget', default_variant)
