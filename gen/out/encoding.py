from os import path, getcwd

def get(door_name: str) -> dict:
    door_meta_path = path.join(getcwd(), "door_meta", door_name)
    with open(path.join(door_meta_path,"key.txt"), "r") as f:
        key_raw = f.read()
    return {y[0]:int(y[1]) for y in [x.split()[::-1] for x in key_raw.split("\n") if len(x.split()) == 2 and x.split()[1] != ""]}
