from dataclasses import dataclass, fields

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
class Room:
    roomLength: int = 10
    roomWidth: int = 10
    wallThickness: float = 0.3
    roomOrigin: str = "point(0,0,0)"
    
    def to_knowledge_fusion(self) -> str:
        dfa = get_dfa_as_string(self.__class__.__name__)
        params = dict((field.name, getattr(self, field.name)) for field in fields(self))
        return insert_parameters(dfa, params)

    def to_child(self, childNumber: int) -> str:
        child = "(Child) " + self.__class__.__name__ + str(childNumber) + ": {\nclass; " + self.__class__.__name__ + ";\n};"
        return child

@dataclass
class Apartment:
    apartmentLength: int = 50
    apartmentWidth: int = 30
    apartmentHeight: float = 2.4
    wallThickness: float = 0.3
    rooms: int = 2
    bathrooms: int = 2
    balcony: bool = False
    apartmentOrigin: str = "point(0,0,0)"
    apartmentNumber: int = 1

    def add_rooms(self, numberOfRooms: int) -> str:
        room = Room(roomNumber=self.apartmentNumber)
        rooms = "".join(["\n" + room.to_child(i+1) for i in range(numberOfRooms)])
        return rooms

    def to_knowledge_fusion(self) -> str:
        pass

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