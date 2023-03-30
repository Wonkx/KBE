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
    
    PARAMS = {'query': test_query} 
    
    try:
        r = requests.post(url = get_query_url(), data = PARAMS)
        return True
    except:
        return False

def insert(zone: Zone) -> bool:
    id = count(zone)
    query = zone.to_sparql_insert(id)
    PARAMS = {'query': query} 

    try:
        r = requests.post(url = get_update_url(), data = PARAMS)
        return True
    except:
        return False

def count(zone: Zone) -> int:
    query = """
    PREFIX kbe:<http://www.my-kbe.com/building.owl#>
    SELECT ?subject ?predicate ?object
    WHERE {
        ?subject a kbe:{zone}.
    }
    """.format(zone=zone.__class__.__name__)

    PARAMS = {'query': query} 

    try:
        count = requests.get(url = get_query_url(), data = PARAMS)
        print(count)
        return count
    except:
        return -1

def get_apartment_ids_without_building(limit: int) -> list[int]:
    query = """
    PREFIX kbe:<http://www.my-kbe.com/building.owl#>
    SELECT ?apartments
    WHERE {
        ?apartments a kbe:Apartment.
        ?apartments kbe:hasArea ?area.
        ?apartments kbe:hasBuilding ?built.
        FILTER (?built = false).
    }
    ORDER BY DESC(?area)
    LIMIT {limit}
    """.format(limit=limit)

    PARAMS = {'query': query} 

    try:
        apartments = requests.get(url = get_query_url(), data = PARAMS)
        print(apartments)
        return [1, 2, 3]
    except:
        return []

def add_apartment_ids_to_building(ids: list[int]) -> None:

    subjects = "\n".join(["(kbe:apartment" + str(id) + ")" for id in ids])

    query = """
    PREFIX kbe:<http://www.my-kbe.com/building.owl#>
    DELETE {{
        a kbe:hasBuilding false.
    }}
    INSERT {{
        a kbe:hasBuilding true.
    }}
    WHERE {{
        a kbe:hasBuilding false.
        VALUES (a) {{
            {subjects}
        }}
    }}
    """.format(subjects=subjects)

    PARAMS = {'query': query} 

    try:
        partments = requests.get(url = get_update_url(), data = PARAMS)
    except:
        pass

if __name__ == '__main__':
    print(test_connection())
    add_apartment_ids_to_building([3, 4])