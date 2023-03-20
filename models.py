from dataclasses import dataclass

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

    path = "new_DFA/" + path
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



@dataclass
class Apartment:
    apartmentLength: int = 50
    apartmentWidth: int = 30
    apartmentHeight: float = 2.4
    wallThickness: float = 0.3
    bedrooms: int = 2
    bathrooms: int = 2
    balcony: float = 0.3
    apartmentOrigin: str = "point(0,0,0)"

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