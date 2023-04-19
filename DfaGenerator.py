from models import Building
import os, shutil

def create_dfas(building: Building, path: str):
    building_dfa = building.to_knowledge_fusion()

    with open(path + r"\building.dfa", 'w') as f:
        f.write(building_dfa)

def confirm_dfa_presence(path: str):
    dfas_in_path = [fileOrFolder for fileOrFolder in os.listdir(path) if fileOrFolder[-4:] == ".dfa"]
    project_dfas = os.listdir(os.path.join(os.path.dirname(__file__), 'dfa'))

    if dfas_in_path != project_dfas:
        for project_dfa in project_dfas:
            filename = os.path.join(os.path.join(os.path.dirname(__file__), 'dfa'), project_dfa)
            if not os.path.isfile(filename):
                continue
            shutil.copy(filename, path)

if __name__ == '__main__':
    pass