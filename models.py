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

    def add_dfa_parameters_as_class_attributes(self) -> None:
        dfa = get_dfa_as_string(self.__class__.__name__)
        lines = [line for line in dfa.split("\n") if line.find(" Parameter) ") >= 0]
        attributes = [line[line.find(") ") + 2:line.rfind(": ")] for line in lines]
        values = [line[line.rfind(": ") + 2:-1] for line in lines]
        for attribute, value in zip(attributes, values):
            setattr(self, attribute, value)

    def to_knowledge_fusion(self) -> str:
        dfa = get_dfa_as_string(self.__class__.__name__)
        params = self.get_class_string_attributes()
        return insert_parameters(dfa, params)

    def get_class_string_attributes(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if isinstance(v, str)}

    def to_knowledge_fusion_child(self) -> str:
        pass

    @abstractmethod
    def to_sparql_insert(self, id: int) -> str:
        pass


@dataclass
class Room(Zone):

    def __post_init__(self) -> None:
        self.add_dfa_parameters_as_class_attributes()

    def to_knowledge_fusion_child(self, childNumber: int) -> str:
        child = "(Child) " + self.__class__.__name__ + str(childNumber) \
            + ": {\nclass; " + self.__class__.__name__ + ";\n" \
            + "".join([(field.name + ": " + str(getattr(self, field.name)) + ";\n") for field in fields(self)]) \
            + "};\n\n"
        return child

    def to_sparql_insert(self, id: int) -> str:
        pass

@dataclass
class Apartment(Zone):
    rooms: list = field(default_factory=list)

    def __post_init__(self) -> None:
        self.add_dfa_parameters_as_class_attributes()

    def add_rooms(self) -> None:
        rooms = [Room() for i in range(int(self.numberOfRooms))]
        for i, room in enumerate(rooms):
            room.roomHeight = "apartmentHeight:"
            appendage = "room" + str(i) if i > 0 else "child:room1"
            room.roomOrigin = \
                 "apartmentOrigin: + vector(apartmentLength: -%a:roomLength:, 0, 0)" % appendage
        self.rooms = rooms

    def to_knowledge_fusion(self) -> str:
        ignore = ["rooms"]
        dfa = get_dfa_as_string(self.__class__.__name__)
        params = dict((field, getattr(self, field)) for field in self.__dict__.keys() if field not in ignore)
        params["hasBalcony"] = "TRUE" if params["hasBalcony"] else "FALSE"
        dfa = insert_parameters(dfa, params)
        for i, room in enumerate(self.rooms):
            appendage = room.to_knowledge_fusion_child(i + 1)
            dfa += appendage
        return dfa    

    def to_sparql_insert(self, id: int) -> str:
        area = "{:.2f}".format(float(self.apartmentLength) * float(self.apartmentWidth))
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
class Storey(Zone):
    apartments: list = field(default_factory=list)

    def __post_init__(self) -> None:
        self.add_dfa_parameters_as_class_attributes()

    def add_apartments(self, apartments: list[Apartment]) -> None:
        for i, apartment in enumerate(apartments):
            if i < 4:
                setattr(self, "ap" + str(i + 1) + "Length", apartment.apartmentLength)
                setattr(self, "ap" + str(i + 1) + "Width", apartment.apartmentWidth)
                setattr(self, "ap" + str(i + 1) + "HasNumberOfRooms", apartment.numberOfRooms)
                setattr(self, "ap" + str(i + 1) + "HasBalcony", apartment.hasBalcony)

        self.apartments = apartments[:4]

    def to_knowledge_fusion(self) -> str:
        dfa = get_dfa_as_string(self.__class__.__name__)
        params = dict((field, getattr(self, field)) for field in self.__dict__.keys() if field != "apartments")
        return insert_parameters(dfa, params)

    def to_knowledge_fusion_child(self, childNumber: int) -> str:
        storeyHeight, floorThickness, roofThickness = float(self.storeyHeight), float(self.floorThickness), float(self.roofThickness)
        self.storeyOrigin = self.storeyOrigin[:self.storeyOrigin.rfind(',') + 1] \
            + str((childNumber - 1) * (storeyHeight + floorThickness + roofThickness)) + ")"

        ignore = ["apartments"]
        childize_attr = lambda attr: attr if attr[-1] != ':' else "Child:" + self.__class__.__name__ + str(childNumber) + ":" + attr 
        parameters = "".join([(field + "; " + childize_attr(str(getattr(self, field))) + ";\n") for field in self.__dict__.keys() if field not in ignore])

        child = "(Child) " + self.__class__.__name__ + str(childNumber) \
            + ": {\nclass; " + self.__class__.__name__ + ";\n" \
            + parameters \
            + "};\n\n"
        return child

    def to_sparql_insert(self, id: int) -> str:
        pass


@dataclass
class Building(Zone):
    buildingOrigin: str = "point(0,0,0)"
    storeys: list = field(default_factory=list)

    def add_storeys(self, storeys: list[Storey]) -> None:
        self.storeys = storeys

    def get_elevator_height(self) -> str:
        height = 0
        for storey in self.storeys:
            storeyHeight, floorThickness, roofThickness = float(storey.storeyHeight), float(storey.floorThickness), float(storey.roofThickness)
            height += (storeyHeight + floorThickness + roofThickness)

        return str(height)

    def to_knowledge_fusion(self) -> str:
        dfa = get_dfa_as_string(self.__class__.__name__)
        params = dict((field.name, getattr(self, field.name)) for field in fields(self) if field.name != "storeys")
        params["elevatorHeight"] = self.get_elevator_height()
        dfa = insert_parameters(dfa, params)
        for i, storey in enumerate(self.storeys):
            appendage = storey.to_knowledge_fusion_child(i + 1)
            dfa += appendage
        return dfa    

    def to_sparql_insert(self, id: int) -> str:
        pass

if __name__ == '__main__':
    r = Room()
    print(r.to_knowledge_fusion())