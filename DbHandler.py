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
        r = requests.get(url = get_query_url(), data = PARAMS)
        d = r.json()
        print(d)
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

def get_apartment_ids_without_building(limit: int) -> list[int]:
    query = """
            PREFIX kbe:<http://www.my-kbe.com/building.owl#>
            SELECT ?apartments
            WHERE {{
                ?apartments a kbe:Apartment.
                ?apartments kbe:hasArea ?area.
                #?apartments kbe:hasBuilding ?built.
                #FILTER (?built = false).
            }}
            ORDER BY DESC(?area)
            LIMIT {limit}
            """.format(limit=limit)

    try:
        response = requests.get(url = get_query_url(), params = {"query": query}) 
        data = response.json()
        return [int(d["apartments"]["value"][-1]) for d in data["results"]['bindings']]
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
    #print(test_connection())
    #add_apartment_ids_to_building([3, 4])
    #print(get_apartment_ids_without_building(10))
    pass
    #q = """
    #PREFIX kbe:<http://www.my-kbe.com/building.owl#>
    #INSERT {
	#kbe:apartment5 a kbe:Apartment.
	#kbe:apartment5 kbe:hasArea "30"^^<http://www.w3.org/2001/XMLSchema#float>.
	#kbe:apartment5 kbe:hasBalcony "true"^^<http://www.w3.org/2001/XMLSchema#boolean>.
	#kbe:apartment5 kbe:hasRooms "2"^^<http://www.w3.org/2001/XMLSchema#int>.
  	#kbe:apartment5 kbe:hasBuilding "true"^^<http://www.w3.org/2001/XMLSchema#boolean>.
    #}
    #WHERE {}
    #"""
    #PARAMS = {"query": q}

    #r = requests.post(url=get_update_url(), params=PARAMS)
    #print(r)
