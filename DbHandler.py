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
    PREFIX kbe:<http://www.my-kbe.com/building.owl#>
    SELECT ?subject ?predicate ?object
    WHERE {{
        ?subject a kbe:{zone}.
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
            PREFIX kbe:<http://www.my-kbe.com/building.owl#>
            SELECT ?apartments ?area ?balcony ?rooms
            WHERE {{
                ?apartments a kbe:Apartment.
                ?apartments kbe:hasArea ?area.
                ?apartments kbe:hasBalcony ?balcony.
                ?apartments kbe:hasRooms ?rooms.
                ?apartments kbe:hasBuilding ?built.
                FILTER (?built = false).
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

    subjects = "\n".join(["(kbe:apartment" + str(id) + ")" for id in ids])

    query = """
    PREFIX kbe:<http://www.my-kbe.com/building.owl#>
    DELETE {{
        ?a kbe:hasBuilding false.
    }}
    INSERT {{
        ?a kbe:hasBuilding true.
    }}
    WHERE {{
        ?a kbe:hasBuilding false.
        VALUES (?a) {{
            {subjects}
        }}
    }}
    """.format(subjects=subjects)

    try:
        apartments = requests.post(url = get_update_url(), data = query )
    except:
        pass

if __name__ == '__main__':
    pass
