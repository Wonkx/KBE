from __future__ import annotations
from views import landing, builder, inhabitant
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from server import RequestHandler

def route(request: RequestHandler, **kwargs: dict[str, any]) -> str:
    path = request.path or '/'
    if (path[0] == '/'):
        path = path[1:]

    match path:
        case "builder":
            return builder(request, **kwargs)
        case "inhabitant":
            return inhabitant(request, **kwargs)
        case _:
            return landing(request, **kwargs)