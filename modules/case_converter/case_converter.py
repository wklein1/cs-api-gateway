def snake_to_camel_case(string:str)->str:
    if not isinstance(string, str):
        raise ValueError("Argument must be a string")

    words = string.split("_")
    title_case = "".join(word.title() for word in words if word)
    camel_case = title_case[0].lower() + title_case[1:]
    return camel_case