from views import landing, builder, inhabitant

def route(path: str, **kwargs: dict[str, any]) -> str:
    if (path[0] == '/'):
        path = path[1:]

    match path:
        case "builder":
            return builder(**kwargs)
        case "inhabitant":
            return inhabitant(**kwargs)
        case _:
            return landing(**kwargs)