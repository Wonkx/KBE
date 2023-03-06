from views import landing, builder, inhabitant

def route(path: str) -> str:
    if (path[0] == '/'):
        path = path[1:]

    match path:
        case "builder":
            return builder()
        case "inhabitant":
            return inhabitant()
        case _:
            return landing()