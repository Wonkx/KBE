from dataclasses import dataclass

@dataclass
class Building:
    stories: int = 10
    buildingOrigen: str = "point(0,0,0)"

    def to_knowledge_fusion(self) -> str:
        pass