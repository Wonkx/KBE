from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from server import RequestHandler
from models import Apartment, Storey, Building
from DbHandler import insert, get_apartments_without_building, add_apartment_ids_to_building
from DfaGenerator import create_dfas


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

def extract_pairs_from_form(request: RequestHandler) -> list[str]:
    content_len = int(request.headers.get("Content-Length"))
    post_body = request.rfile.read(content_len)
    body = post_body.decode()
    pairs = body.split('&')

    return pairs

def landing(request: RequestHandler, **kwargs: dict[str, any]) -> str:
    html = get_html_as_string("landing")
    return html

def builder(request: RequestHandler, **kwargs: dict[str, any]) -> str:
    required_kwargs = ["HOST_NAME", "PORT_NUMBER"]
    if not confirm_kwargs(kwargs, required_kwargs):
        return landing(kwargs)

    if request.command == "POST":
        pairs = extract_pairs_from_form(request)
        try:
            numberOfStoreys = max(1, int(pairs[0].split('=')[1]))
        except:
            numberOfStoreys = 1

        apartments, ids, used_ids, storeys = [], [], [], []
        apartments_without_building = get_apartments_without_building(numberOfStoreys * 4)
        for i, dict in enumerate(apartments_without_building):
            apartment = Apartment()
            apartment.apartmentLength = float(dict["area"]["value"]) / apartment.apartmentWidth
            apartment.hasBalcony = True if dict["balcony"]["value"] == "true" else False
            apartment.numberOfRooms = int(dict["rooms"]["value"])
            apartment.add_rooms()

            apartments.append(apartment)
            ids.append(int(dict["apartments"]["value"].split("apartment")[1]))

            if (i + 1) % 4 == 0:
                storey = Storey()
                storey.add_apartments(apartments)
                storeys.append(storey)
                apartments.clear()
                used_ids += ids
                ids.clear()

        building = Building()
        building.storeys = len(used_ids) // 4
        building.add_storeys(storeys)

        add_apartment_ids_to_building(used_ids)

        #create_dfas(building)
        print("builder post end")

    html = get_html_as_string("builder")
    context = {"page_title": "builder", "url": "#"}
    return insert_parameters(html, context)

def inhabitant(request: RequestHandler, **kwargs: dict[str, any]) -> str:
    required_kwargs = ["HOST_NAME", "PORT_NUMBER"]
    if not confirm_kwargs(kwargs, required_kwargs):
        return landing(kwargs)
    
    if request.command == "POST":
        #TODO: Add form validation

        pairs = extract_pairs_from_form(request)

        try:
            balcony = True if len(pairs) == 3 else False
            numberOfRooms = max(0, int(pairs[0].split('=')[1]))
            size = min(256, float(pairs[1].split('=')[1]))
        except:
            balcony, numberOfRooms, size = False, 2, 64
        
        apartment = Apartment()
        apartment.hasBalcony = balcony
        apartment.numberOfRooms = min(4, numberOfRooms)
        apartment.apartmentLength = size / apartment.apartmentWidth
        apartment.add_rooms()
        print("Insertion: ", insert(apartment))

    
    html = get_html_as_string("inhabitant")
    url = "http://" + kwargs["HOST_NAME"] + ":" + str(kwargs["PORT_NUMBER"])
    context = {"page_title": "Inhabitant", "url": "#"}
    html = insert_parameters(html, context)

    return html

