from os import path, getcwd
from gen.out import ss_encode

def gen_ss_sequence(door_name: String) -> list[int]:
    # open sequence file
    door_meta_path = path.join(getcwd(), "door_meta", door_name) 
    
    with open(path.join(door_meta_path,"sequence.txt"), "r") as f:
        sequence_raw = f.read()
            
    # generate sequence based on encoding and text file
    ss_sequence = [int(ss_encode.get_encode(door_name)[x]) for x in sequence_raw.split("\n")]
    
    return ss_sequence
