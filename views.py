from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from server import RequestHandler
from models import Apartment
from DbHandler import insert

def insert_parameters(html: str, context: dict) -> str:

    # Inserting values
    for key, value in context.items():
        insert = "{% " + key + " %}"
        if html.find(insert) > -1:
            html = html.replace("{% " + key + " %}", value)
        else:
            print('Could not find "' + insert + '" in html')

    # Throw warning (print) if there are any variables left in the html string
    start_position, end_position = html.find("{% "), html.find(" %}")
    if start_position+1 and end_position+1:
        variable = html[start_position:end_position]
        print("Variable " + variable + " not inserted in html")

    # Return html string with context inserted
    return html

def get_html_as_string(path: str) -> str:

    path = "templates/" + path
    if (path[-5:].lower() != ".html"):
        path += ".html"

    html = open(path, "r")
    string = html.read()
    html.close()

    return string

def confirm_kwargs(kwargs: dict[str, any], requirements: list[str]) -> bool:
    for kwarg in requirements:
        if kwarg not in kwargs:
            return False
    return True

def landing(request: RequestHandler, **kwargs: dict[str, any]) -> str:
    html = get_html_as_string("landing")
    return html

def builder(request: RequestHandler, **kwargs: dict[str, any]) -> str:
    html = get_html_as_string("builder")
    context = {"page_title": "builder", "heading": "heading"}
    return insert_parameters(html, context)

def inhabitant(request: RequestHandler, **kwargs: dict[str, any]) -> str:
    required_kwargs = ["HOST_NAME", "PORT_NUMBER"]
    if not confirm_kwargs(kwargs, required_kwargs):
        return landing(kwargs)
    
    if request.command == "POST":
        #TODO: Add form validation

        content_len = int(request.headers.get("Content-Length"))
        post_body = request.rfile.read(content_len)
        body = post_body.decode()
        pairs = body.split('&')

        balcony = True if len(pairs) == 3 else False
        numberOfRooms = int(pairs[0].split('=')[1])
        size = float(pairs[1].split('=')[1])
        
        apartment = Apartment()
        apartment.hasBalcony = balcony
        apartment.numberOfRooms = min(4, numberOfRooms)
        apartment.apartmentLength = size / apartment.apartmentWidth
        apartment.add_rooms()
        insert(apartment)

    
    html = get_html_as_string("inhabitant")
    url = "http://" + kwargs["HOST_NAME"] + ":" + str(kwargs["PORT_NUMBER"])
    context = {"page_title": "Inhabitant", "url": "#"}
    html = insert_parameters(html, context)

    return html

