import requests
from models import Zone

HOST_NAME = '127.0.0.1' 
PORT_NUMBER = 3030
DATASET = "kbe"

def get_query_url() -> str:
    return "http://" + HOST_NAME + ":" + str(PORT_NUMBER) + "/" + DATASET + "/query"

def get_update_url() -> str:
    return "http://" + HOST_NAME + ":" + str(PORT_NUMBER) + "/" + DATASET + "/update"

def test_connection() -> bool:
    test_query = """
                SELECT ?subject ?predicate ?object
                WHERE {
                    ?subject ?predicate ?object.
                }
                LIMIT 1
                """
    
    PARAMS = {'query': test_query, 'format': "json"} 
    
    try:
        r = requests.get(url = get_query_url(), params = PARAMS)
        d = r.json()
        return True
    except:
        return False

def insert(zone: Zone) -> bool:
    id = count(zone) + 1
    query = zone.to_sparql_insert(id)
    
    try:
        r = requests.post(url = get_update_url(), data = query)
        return True
    except:
        return False

def count(zone: Zone) -> int:
    query = """
    PREFIX bot:<https://w3id.org/bot#>
    SELECT ?subject ?predicate ?object
    WHERE {{
        ?subject a bot:{zone}.
    }}
    """.format(zone=zone.__class__.__name__)

    try:
        response = requests.get(url = get_query_url(), params = {'query': query})
        data = response.json()
        count = len(data["results"]['bindings'])
        return count
    except:
        return -1

def get_apartments_without_building(limit: int) -> list[dict]:
    query = """
            PREFIX bot:<https://w3id.org/bot#>
            SELECT ?apartments ?area ?balcony ?rooms
            WHERE {{
                ?apartments a bot:Apartment.
                ?apartments bot:hasArea ?area.
                ?apartments bot:hasBalcony ?balcony.
                ?apartments bot:hasRooms ?rooms.
                ?apartments bot:hasBuilding ?buildingId.
                FILTER (?buildingId = 0).
            }}
            ORDER BY DESC(?area)
            LIMIT {limit}
            """.format(limit=limit)

    if (limit < 1):
        query = "\n".join(query.split("\n")[:-2])

    try:
        response = requests.get(url = get_query_url(), params = {"query": query}) 
        data = response.json()
        return [d for d in data["results"]['bindings']]
    except:
        return []

def add_apartment_ids_to_building(ids: list[int]) -> None:

    subjects = "\n".join(["(bot:apartment" + str(id) + ")" for id in ids])
    maxBuildingId = get_max_building_id()

    query = """
    PREFIX bot:<https://w3id.org/bot#>
    DELETE {{
        ?a bot:hasBuilding "0"^^<http://www.w3.org/2001/XMLSchema#int>.
    }}
    INSERT {{
        ?a bot:hasBuilding "{id}"^^<http://www.w3.org/2001/XMLSchema#int>.
    }}
    WHERE {{
        ?a bot:hasBuilding "0"^^<http://www.w3.org/2001/XMLSchema#int>.
        VALUES (?a) {{
            {subjects}
        }}
    }}
    """.format(subjects=subjects, id=maxBuildingId + 1)

    try:
        apartments = requests.post(url = get_update_url(), data = query )
    except:
        pass


def get_max_building_id() -> int:
    query = """
    PREFIX bot:<https://w3id.org/bot#>
    SELECT (MAX(?buildingId) AS ?Id)
    WHERE {{
        ?apartments a bot:Apartment.
        ?apartments bot:hasBuilding ?buildingId.
    }}
    """

    try:
        response = requests.get(url = get_query_url(), params = {"query": query}) 
        data = response.json()
        return int(data["results"]['bindings'][0]['Id']['value'])
    except:
        return 0

if __name__ == '__main__':
    pass
