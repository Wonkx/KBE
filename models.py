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
class Building:
    stories: int = 10
    buildingOrigen: str = "point(0,0,0)"

    def to_knowledge_fusion(self) -> str:
        pass