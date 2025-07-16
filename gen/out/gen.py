import sys
import os
from nbtlib.tag import *
from gen.util import gen
from gen.out import rom
from ast import literal_eval
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

def gen_file(door_name: String, file_name: String):
    
    out = gen.File()
    
    # get list of carts
    
    cart_list = rom.gen_ROM_OPTIMIZED(door_name)
    
    # add entity list to file
    out.update({"Entities": List(cart_list)})
    
    # save file
    out.save(os.path.join("output_schematics",door_name, f"{file_name}.schem"))
    
    return out

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 0:
        print("Pass in door name and file name as two separate parameters. \nLeave off file name to simply use door name.")
    elif len(args) == 1:
        rom.gen_ROM_OPTIMIZED(*args) # change to gen_file once ready
    elif len(args) == 2:
        gen_file(*args)
    else:
        print("Too many arguments.")