# qt-jsonschema-form
A tool to generate Qt forms from JSON Schemas. 

## Features
* Error messages from JSONSchema validation ([see jsonschema](https://github.com/Julian/jsonschema)).
* Widgets for file selection, colour picking, date-time selection (and more).
* Per-field widget customisation is provided by an additional ui-schema (inspired by https://github.com/mozilla-services/react-jsonschema-form).

## Unsupported validators
Currently this tool does not support `anyOf` or `oneOf` directives. The reason for this is simply that these validators have different semantics depending upon the context in which they are found. Primitive support could be added with meta-widgets for type schemas.

Additionally, the `$ref` keyword is not supported. This will be fixed, but is waiting on some proposed upstream changes in `jsonschema`

## Detailed explanation
For more details about each options, see [](USAGE.md)

## Example
See (the test file)[test.py]
