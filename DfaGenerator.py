from models import Building

def create_dfas(building: Building, path: str):
    building_dfa = building.to_knowledge_fusion()

    with open(path + r"\building.dfa", 'w') as f:
        f.write(building_dfa)