from dataclasses import dataclass, field
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

    def get_class_string_attributes(self) -> dict[str, str]:
        return {k: v for k, v in self.__dict__.items() if isinstance(v, str)}

    def to_knowledge_fusion(self) -> str:
        dfa = get_dfa_as_string(self.__class__.__name__)
        params = self.get_class_string_attributes()
        return insert_parameters(dfa, params)

    def to_knowledge_fusion_child(self, childNumber: int) -> str:
        params = [k + "; " + v + ";\n" for k, v in self.get_class_string_attributes().items()]
        child = "(Child) " + self.__class__.__name__ + str(childNumber) \
            + ": {\nclass; " + self.__class__.__name__ + ";\n" \
            + "".join(params) \
            + "};\n\n"
        return child

    @abstractmethod
    def to_sparql_insert(self, id: int) -> str:
        pass


@dataclass
class Room(Zone):

    def __post_init__(self) -> None:
        self.add_dfa_parameters_as_class_attributes()

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
        dfa = super().to_knowledge_fusion()
        for i, room in enumerate(self.rooms):
            dfa += room.to_knowledge_fusion_child(i + 1)
        return dfa

    def to_sparql_insert(self, id: int) -> str:
        area = "{:.2f}".format(float(self.apartmentLength) * float(self.apartmentWidth))
        hasBalcony, numberOfRooms = str(self.hasBalcony).lower(), str(self.numberOfRooms)
        query = """
                PREFIX bot:<https://w3id.org/bot#>
                INSERT {{
                    bot:apartment{id} a bot:Apartment.
                    bot:apartment{id} bot:hasArea "{area}"^^<http://www.w3.org/2001/XMLSchema#float>.
                    bot:apartment{id} bot:hasBalcony "{hasBalcony}"^^<http://www.w3.org/2001/XMLSchema#boolean>.
                    bot:apartment{id} bot:hasRooms "{numberOfRooms}"^^<http://www.w3.org/2001/XMLSchema#int>.
                    bot:apartment{id} bot:hasBuilding "0"^^<http://www.w3.org/2001/XMLSchema#int>.
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
        for i, apartment in enumerate(apartments[:4]):
            setattr(self, "ap" + str(i + 1) + "Length", apartment.apartmentLength)
            setattr(self, "ap" + str(i + 1) + "Width", apartment.apartmentWidth)
            setattr(self, "ap" + str(i + 1) + "HasNumberOfRooms", apartment.numberOfRooms)
            setattr(self, "ap" + str(i + 1) + "HasBalcony", apartment.hasBalcony)

        self.apartments = apartments[:4]

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
    storeys: list = field(default_factory=list)

    def __post_init__(self) -> None:
        self.add_dfa_parameters_as_class_attributes()

    def add_storeys(self, storeys: list[Storey]) -> None:
        self.storeys = storeys

    def get_elevator_height(self) -> str:
        height = 0
        for storey in self.storeys:
            storeyHeight, floorThickness, roofThickness = float(storey.storeyHeight), float(storey.floorThickness), float(storey.roofThickness)
            height += (storeyHeight + floorThickness + roofThickness)
        return str(height)

    def to_knowledge_fusion(self) -> str:
        self.elevatorHeight = self.get_elevator_height()
        dfa = super().to_knowledge_fusion()
        for i, storey in enumerate(self.storeys):
            dfa += storey.to_knowledge_fusion_child(i + 1)
        return dfa    

    def to_sparql_insert(self, id: int) -> str:
        pass

if __name__ == '__main__':
    pass