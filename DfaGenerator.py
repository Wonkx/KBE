from models import Building
from server import DFA_PATH

def create_dfas(building: Building):
    building_dfa = building.to_knowledge_fusion()

    with open(DFA_PATH + r"\building.dfa") as f:
        f.write(building_dfa)