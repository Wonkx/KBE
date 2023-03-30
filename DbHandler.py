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
                SELECT ?subject ?predicate ?object.
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
    SELECT ?subject ?predicate ?object.
    WHERE {
        ?subject a kbe:{zone}.
    }
    """.format(zone=zone.__class__.__name__)

    PARAMS = {'query': query} 

    try:
        count = requests.get(url = get_query_url(), data = PARAMS)
        return count
    except:
        return -1

if __name__ == '__main__':
    print(test_connection())