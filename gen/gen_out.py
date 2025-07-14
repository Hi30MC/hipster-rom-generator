import nbtlib
from nbtlib import File, schema
from nbtlib.tag import *
from gen.gen_util import *
from ast import literal_eval
import sys
from types import SimpleNamespace

"""
General logic flow of the file:
- Generate sequence:
    - Generate full sequence as a list of strings of move names
    - Convert list of move names to a list of numerical signal strengths using the key
- Generate ROM as a list of carts
    - Determine structure of items based on door's meta
    - Optimize item placement based on door's meta
- Generate base file structure with gen_base()
- Add list of carts to base file and export
"""

def get_ss_encode(door_name: String) -> {String: int}:
    door_meta_path = f"door_meta/{door_name}"
    with open(f"{door_meta_path}/key.txt", "r") as f:
        key_raw = f.read()
    return {y[0]:int(y[1]) for y in [x.split()[::-1] for x in key_raw.split("\n") if len(x.split()) == 2 and x.split()[1] != ""]}

def gen_ss_sequence(door_name: String) -> list[int]:
    # open sequence file
    door_meta_path = f"door_meta/{door_name}"
    
    with open(f"{door_meta_path}/sequence.txt", "r") as f:
        sequence_raw = f.read()
            
    # generate sequence based on encoding and text file
    ss_encode = get_ss_encode(door_name)
    ss_sequence = [int(ss_encode[x]) for x in sequence_raw.split("\n")]
    
    return ss_sequence

def gen_ROM(door_name: String):
    return -1

def gen_file(door_name: String, file_name: String):
    door_meta_path = f"door_meta/{door_name}"
    door_gen_path = f"gen/{door_name}"
    
    out = gen_base()
    
    # get list of carts
    
    cart_list = []
    
    # add entity list to file
    
    out.update({"Entities": List(cart_list)})
    
    # save file
    out.save(f"output_schematics/{door_name}/{file_name}.schem")
    
    return out

# # add entity list to file
# out.update({
#     "Entities": List([
#         gen_cart(items=[
#             gen_ss_sb(0, 1),
#             gen_ss_sb(1, 9),
#             gen_ss_disc(2, 8),
#             gen_ss_disc(3, 4)
#         ])
#     ])
# })

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 0:
        print("Pass in door name and file name as two separate parameters. \nLeave off file name to simply use door name.")
    elif len(args) == 1:
        gen_ROM(*args) # change to gen_file once ready
    elif len(args) == 2:
        gen_file(*args)
    else:
        print("Too many arguments.")