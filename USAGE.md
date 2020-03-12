# Main usage
As shown in the example, the main use of this library is as follows:

```python3
from qt_jsonschema_form import WidgetBuilder
builder = WidgetBuilder()
form = builder.create_form(schema, ui_schema)
form.show()
form.widget.state = default_value
```
You can then apply a method `fn(json_value)` to the JSON value each time a change
is done by doing:
```python3
form.widget.on_changed.connect(fn)
```
and you can access to the current json value using
```python3
form.widget.state
```.

# Variants
JSON's type is extremely vague. For example decimal (floating point)
number and integral numbers have the same type. In order to decide
which widget the user see, this library uses "variant". A variant is a
name stating which kind of widget should be used to display a value to
the user and let them change it. A variant can only be assigned to an
element of an object, it is determined by the property name and the
parameter ui_schema. TODO: why?

Each type has the variant "enum". If this variant is used for a
schema, this schema must have an "enum" property. Each element of this
property will be displayed in a `QComboBox`. We now list the other
variants.

## Boolean
The only other variant of "boolean" is "checkbox", which is
implemented using a `QCheckBox`

## Object
The only other variant of "object" is "object", which is implemented
using a `QGroupBox`. That is: its content is displayed in the same
window, with elements grouped together.

## Number

Number has two variants:
* "spin", which uses a `QDoubleSpinBox`
* "text", which uses a `QLineEdit`

## Integer

It admits the same variants as Number, plus:
* "range", which uses a `QSlider`

## String

Strings has the following variant:
* "textarea", which uses a `QTextEdit`
* "text", which uses a `QLineEdit`
* "password", which uses a `TextSchemaWidget`
* "filepath", which adds a button which use the open file name in the computer
* "dirpath", which adds a button which use the open directory name in the computer
* "colour", which uses a `QColorButton`

# Defaults
When the UI is created, default values are inserted. Those values may
be changed by the user for a specific json value. Those values are of
the correct types; it's not guaranteed however that they satisfy all
schema constraints. (Actually, since there can be conjunction,
disjunction, negation of schema, and even if-then-else schema, finding
such value may be actually impossible).

If a schema contains a "default" value, this value is used.

If a schema is an enum, its first value is used as default value.

If the type of the schema is an object, then its default value is an object
containing the values in "properties", and its associated default
values are computed as explained in this section.

If the type of the schema is a list (array whose "items" is a schema)
then the default value is the empty list.

If the type of the schema is a tuple (array whose "items" is an array
of schema) then the default value is a tuple, whose value contains as
many element as the items. Each element's default value is computed as
explained in this section.

The default value of Boolean is True.

The default value of a string is a string containing only spaces, as
short as possible, accordin to the minimal size constraint.

The default value of a number is:
* as close as possible to the average between the maximum and the
  minimum if they are set.
* as close as possible to the maximum or to the minimum if only one is
  set
* 0 otherwise.
