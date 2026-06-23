def validate_type_name(type_name: str) -> str:
    if type_name == "int":
        return "integer"
    elif type_name == "str":
        return "string"
    elif type_name == "float":
        return "number"
    elif type_name == "bool":
        return "boolean"
    elif type_name == "list":
        return "array"
    elif type_name == "dict":
        return "object"
    else:
        return type_name
