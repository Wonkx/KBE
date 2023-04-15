from dataclasses import dataclass, fields, field
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

    def to_knowledge_fusion_child(self, childNumber: int) -> str:
        child = "(Child) " + self.__class__.__name__ + str(childNumber) \
            + ": {\nclass; " + self.__class__.__name__ + ";\n" \
            + "".join([(field.name + ": " + str(getattr(self, field.name)) + ";\n") for field in fields(self)]) \
            + "};\n\n"
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
    hasBalcony: bool | str = False
    apartmentOrigin: str = "point(0,0,floorThickness:)"
    rooms: list = field(default_factory=list)

    def add_rooms(self) -> None:
        rooms = [Room() for i in range(self.numberOfRooms)]
        for i, room in enumerate(rooms):
            room.roomHeight = "apartmentHeight:"
            appendage = "room" + str(i) if i > 0 else "child:room1"
            room.roomOrigin = \
                 "apartmentOrigin: + vector(apartmentLength: -%a:roomLength:, 0, 0)" % appendage
        self.rooms = rooms

    def to_knowledge_fusion(self) -> str:
        dfa = get_dfa_as_string(self.__class__.__name__)
        params = dict((field.name, getattr(self, field.name)) for field in fields(self) if field.name != "rooms")
        params["hasBalcony"] = "TRUE" if params["hasBalcony"] else "FALSE"
        dfa = insert_parameters(dfa, params)
        for i, room in enumerate(self.rooms):
            appendage = room.to_knowledge_fusion_child(i + 1)
            dfa += appendage
        return dfa    

    def to_sparql_insert(self, id: int) -> str:
        area = "{:.2f}".format(self.apartmentLength * self.apartmentWidth)
        hasBalcony, numberOfRooms = str(self.hasBalcony).lower(), str(self.numberOfRooms)
        query = """
                PREFIX kbe:<http://www.my-kbe.com/building.owl#>
                INSERT {{
                    kbe:apartment{id} a kbe:Apartment.
                    kbe:apartment{id} kbe:hasArea "{area}"^^<http://www.w3.org/2001/XMLSchema#float>.
                    kbe:apartment{id} kbe:hasBalcony "{hasBalcony}"^^<http://www.w3.org/2001/XMLSchema#boolean>.
                    kbe:apartment{id} kbe:hasRooms "{numberOfRooms}"^^<http://www.w3.org/2001/XMLSchema#int>.
                    kbe:apartment{id} kbe:hasBuilding "false"^^<http://www.w3.org/2001/XMLSchema#boolean>.
                }}
                WHERE {{
                }}
                """.format(id=id, area=area, hasBalcony=hasBalcony, numberOfRooms=numberOfRooms)

        return query

@dataclass
class Storey:
    apartments: list = field(default_factory=list)

    def __post_init__(self):
        dfa = get_dfa_as_string(self.__class__.__name__)
        lines = [line for line in dfa.split("\n") if line.find(" Parameter) ") >= 0]
        attributes = [line[line.find(") ") + 2:line.rfind(": ")] for line in lines]
        values = [line[line.rfind(": ") + 2:-1] for line in lines]
        for attribute, value in zip(attributes, values):
            setattr(self, attribute, value)

    def add_apartments(self, apartments: list[Apartment]) -> None:
        for i, apartment in enumerate(apartments):
            if i < 4:
                setattr(self, "ap" + str(i + 1) + "Length", apartment.apartmentLength)
                setattr(self, "ap" + str(i + 1) + "Width", apartment.apartmentWidth)
        self.apartments = apartments[:4]

    def to_knowledge_fusion(self) -> str:
        dfa = get_dfa_as_string(self.__class__.__name__)
        params = dict((field, getattr(self, field)) for field in self.__dict__.keys() if field != "apartments")
        return insert_parameters(dfa, params)

    def to_knowledge_fusion_child(self, childNumber: int) -> str:
        self.storeyOrigin = self.storeyOrigin[:self.storeyOrigin.rfind(',') + 1] \
            + str((childNumber - 1) * (self.storeyHeight + self.floorThickness + self.roofThickness)) + ")"

        ignore = ["apartments"]
        childize_attr = lambda attr: attr if attr[-1] != ':' else "Child:" + self.__class__.__name__ + str(childNumber) + ":" + attr 
        parameters = "".join([(field + "; " + childize_attr(str(getattr(self, field))) + ";\n") for field in self.__dict__.keys() if field not in ignore])

        child = "(Child) " + self.__class__.__name__ + str(childNumber) \
            + ": {\nclass; " + self.__class__.__name__ + ";\n" \
            + parameters \
            + "};\n\n"
        return child


@dataclass
class Building(Zone):
    storeys: int = 10
    buildingOrigin: str = "point(0,0,0)"
    storeys: list = field(default_factory=list)

    def add_storeys(self, storeys: list[Storey]) -> None:
        self.storeys = storeys

    def to_knowledge_fusion(self) -> str:
        dfa = get_dfa_as_string(self.__class__.__name__)
        params = dict((field.name, getattr(self, field.name)) for field in fields(self) if field.name != "storeys")
        dfa = insert_parameters(dfa, params)
        for i, storey in enumerate(self.storeys):
            appendage = storey.to_knowledge_fusion_child(i + 1)
            dfa += appendage
        return dfa    

    def to_sparql_insert(self, id: int) -> str:
        pass

if __name__ == '__main__':
    pass