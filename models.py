from dataclasses import dataclass

@dataclass
class Room:
    roomLength: int = 10
    roomWidth: int = 10
    wallThickness: float = 0.3
    roomOrigin: str = "point(0,0,0)"

    def to_knowledge_fusion(self) -> str:
        pass

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