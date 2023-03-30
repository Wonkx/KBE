from dataclasses import dataclass, fields
from abc import ABC, abstractmethod

def insert_parameters(dfa: str, parameters: dict) -> str:

    # Inserting values
    for key, value in parameters.items():
        param = "Parameter) " + key + ": "
        index = dfa.find(param)
        if index > -1:
            lend = dfa.find(";", index)
            dfa = dfa[:index] + param + str(value) + dfa[lend:]
        else:
            print('Could not find "' + key + '" in dfa')

    # Return dfa string with parameters inserted
    return dfa

def get_dfa_as_string(path: str) -> str:

    path = "dfa/" + path
    if (path[-4:].lower() != ".dfa"):
        path += ".dfa"

    dfa = open(path, "r")
    string = dfa.read()
    dfa.close()

    return string

@dataclass
class Zone(ABC):

    @abstractmethod
    def to_knowledge_fusion(self) -> str:
        pass

    @abstractmethod
    def to_sparql_insert(self) -> str:
        pass

@dataclass
class Room:
    roomLength: float = 10
    roomWidth: float = 10
    roomHeight: float = 2.4
    wallThickness: float = 0.3
    doorHeight: float = 1.9
    roomOrigin: str = "point(0,0,0)"
    
    def to_knowledge_fusion(self) -> str:
        dfa = get_dfa_as_string(self.__class__.__name__)
        params = dict((field.name, getattr(self, field.name)) for field in fields(self))
        return insert_parameters(dfa, params)

    def to_child(self, childNumber: int) -> str:
        child = "(Child) " + self.__class__.__name__ + str(childNumber) + ": {\nclass; " + self.__class__.__name__ + ";\n};"
        return child

@dataclass
class Apartment(Zone):
    apartmentLength: float = 20
    apartmentWidth: float = 20
    apartmentHeight: float = 2.4
    wallThickness: float = 0.3
    floorThickness: float = 0.5
    roofThickness: float = 0.5
    numberOfRooms: int = 2
    apartmentOrigin: str = "point(0,0,floorThickness:)"

    def add_rooms(self) -> str:
        room = Room()
        rooms = "".join(["\n" + room.to_child(i+1) for i in range(4)])
        return rooms

    def to_knowledge_fusion(self) -> str:
        pass

    def to_sparql_insert(self) -> str:
        query = """
                INSERT {

                } 
                WHERE {

                }
                """.format()

        return query

@dataclass
class Storey:
    storeyWallThickness: float = 0.3
    storeyLength: int = 50
    storeyWidth: int = 20
    storeyHeight: float = 2.0
    storeyOrigin: str = "point(0,0,0)"

    def to_knowledge_fusion(self) -> str:
        pass

@dataclass
class Building:
    stories: int = 10
    buildingOrigen: str = "point(0,0,0)"

    def to_knowledge_fusion(self) -> str:
        pass

if __name__ == '__main__':
    pass