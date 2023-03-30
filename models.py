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
    def to_sparql_insert(self, id: int) -> str:
        pass

@dataclass
class Room:
    roomLength: float | str = 10
    roomWidth: float | str = 10
    roomHeight: float | str = 2.4
    wallThickness: float | str = 0.3
    doorHeight: float | str = 1.9
    roomOrigin: str = "point(0,0,0)"
    
    def to_knowledge_fusion(self) -> str:
        dfa = get_dfa_as_string(self.__class__.__name__)
        params = dict((field.name, getattr(self, field.name)) for field in fields(self))
        return insert_parameters(dfa, params)

@dataclass
class Room:
    roomLength: float | str = 10
    roomWidth: float | str = 10
    roomHeight: float | str = 2.4
    wallThickness: float | str = 0.3
    doorHeight: float | str = 1.9
    roomOrigin: str = "point(0,0,0)"
    
    def to_knowledge_fusion(self) -> str:
        dfa = get_dfa_as_string(self.__class__.__name__)
        params = dict((field.name, getattr(self, field.name)) for field in fields(self))
        return insert_parameters(dfa, params)

    def to_knowledge_fusion_child(self, childNumber: int) -> str:
        child = "(Child) " + self.__class__.__name__ + str(childNumber) \
            + ": {\nclass; " + self.__class__.__name__ + ";\n" \
            + "".join([(field.name + ": " + str(getattr(self, field.name)) + ";\n") for field in fields(self)]) \
            + "};"
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
    hasBalcony: bool = False
    apartmentOrigin: str = "point(0,0,floorThickness:)"
    rooms: list[Room] = []

    def add_rooms(self) -> None:
        rooms = [Room() for i in range(self.numberOfRooms)]
        for i, room in enumerate(rooms):
            room.roomHeight = "apartmentHeight:"
            appendage = "room" + str(i) if i > 0 else "child:room1"
            room.roomOrigin = \
                 "apartmentOrigin: + vector(apartmentLength: -%a:roomLength:, 0, 0)" % appendage
        self.rooms = rooms

    def to_knowledge_fusion(self) -> str:
        #rooms = "".join(["\n" + room.to_child(i+1) for i in range(min(self.numberOfRooms, 3))])
        pass

    def to_sparql_insert(self, id: int) -> str:
        area = "{:.2f}".format(self.apartmentLength * self.apartmentWidth)
        hasBalcony, numberOfRooms = str(self.hasBalcony).lower(), str(self.numberOfRooms)
        query = """
                PREFIX kbe:<http://www.my-kbe.com/building.owl#>
                INSERT {
                    kbe:apartment{id} a kbe:Apartment.
                    kbe:apartment{id} kbe:hasArea "{area}"^^<http://www.w3.org/2001/XMLSchema#float>.
                    kbe:apartment{id} kbe:hasBalcony "{hasBalcony}"^^<http://www.w3.org/2001/XMLSchema#boolean>.
                    kbe:apartment{id} kbe:hasRooms "{numberOfRooms}"^^<http://www.w3.org/2001/XMLSchema#int>.
                }
                WHERE {
                }
                """.format(id=id, area=area, hasBalcony=hasBalcony, numberOfRooms=numberOfRooms)

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
class Building(Zone):
    storeys: int = 10
    buildingOrigen: str = "point(0,0,0)"

    def to_knowledge_fusion(self) -> str:
        pass

    def to_sparql_insert(self, id: int) -> str:
        pass

if __name__ == '__main__':
    pass