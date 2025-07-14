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
    # generate sequence
    sequence = gen_ss_sequence(door_name)
    
    # get rom metadata
    door_meta_path = f"door_meta/{door_name}"
    with open(f"{door_meta_path}/rom_params.txt", "r") as f:
        rom_params = literal_eval(f.read())
    
    # create pos of carts if not specified
    if "pos" not in rom_params.keys():
        rom_params.update({"pos": [0.5, 0, 0.5]})
    
    meta = SimpleNamespace(**rom_params)
    
    # get encoding table
    ss_encode = get_ss_encode(door_name)
    
    # Ensure a couple base params are declared
    try:
        _ = meta.density
    except:
        raise Exception(f"No value 'density' defined in '{door_meta_path}/rom_params.txt'.")
    try:
        _ = meta.min_carts
    except:
        raise Exception(f"No value 'min_carts' defined in '{door_meta_path}/rom_params.txt'.")        

    if meta.density == 1: # 1 cart per move-type ROM
        
        # pad sequence for minimum move count        
        if len(sequence) < meta.min_carts:
            # assign wait move if not already
            if "wait" not in ss_encode.keys():
                wait_backups = [x for x in range(1,16) if x not in ss_encode.values()]
                if len(wait_backups) == 0:
                    raise Exception(f"No wait move availible to pad moves. Please create manually.")
                ss_encode.update({"wait": wait_backups[0]})
            # pad to minimum
            if sequence[-1] == 0: # pad waits before the STOP command
                sequence = sequence[:-1] + [ss_encode["wait"]] * (meta.min_carts - len(sequence)) + [0]
            else:
                sequence += [ss_encode["wait"]] * (meta.min_carts - len(sequence))
        
        # convert sequence into cartstack, return
        return [gen_ss_cart(x, pos=meta.pos) for x in sequence]
    elif meta.density == 27:
        # Ensure "medium" and "min_items_per_cart" keys are defined
        try:
            _ = meta.medium
        except:
            raise Exception(f"No value 'medium' defined in '{door_meta_path}/rom_params.txt'.")
        try:
            _ = meta.min_items_per_cart
        except:
            raise Exception(f"No value 'min_items_per_cart' defined in '{door_meta_path}/rom_params.txt'.")
        
        min_items = meta.min_carts * meta.min_items_per_cart
        
        # pad sequence for minimum move count
        if len(sequence) < min_items:
            # assign wait move if not already
            if "wait" not in ss_encode.keys():
                wait_backups = [x for x in range(1,16) if x not in ss_encode.values()]
                if len(wait_backups) == 0:
                    raise Exception(f"No wait move availible to pad moves. Please create manually.")
                ss_encode.update({"wait": wait_backups[0]})
            # pad to minimum
            if sequence[-1] == 0: # pad waits before the STOP command
                sequence = sequence[:-1] + [ss_encode["wait"]] * (min_items - len(sequence)) + [0]
            else:
                sequence += [ss_encode["wait"]] * (min_items - len(sequence))
        
        
        cart_list = [gen_cart(pos=meta.pos)]
        min_items -= meta.min_items_per_cart
        slot = 0
        while len(sequence) > 0:
            if len(cart_list[-1]["Items"]) > 26:
                cart_list.append(gen_cart(pos=meta.pos))
                min_items -= meta.min_items_per_cart
                slot = 0
            elif len(sequence) > min_items:
                ss = sequence.pop(0)
                if meta.medium == "shulker":
                    item = gen_ss_sb(slot, ss)
                elif meta.medium == "disc":
                    item = gen_ss_disc(slot, ss)
                else:
                    raise Exception(f"Invalid 'medium' type in {door_meta_path}/rom_params.txt")
                add_item_to_cart(cart_list[-1], item)
                slot += 1
            else:
                cart_list.append(gen_cart(pos=meta.pos))
                min_items -= meta.min_items_per_cart
                slot = 0
        return cart_list
        
        
        
    elif meta.density == 729:
        print(729)
    else:
        return []

    return -1

def gen_file(door_name: String, file_name: String):
    door_meta_path = f"door_meta/{door_name}"
    door_gen_path = f"gen/{door_name}"
    
    out = gen_base()
    
    # get list of carts
    
    cart_list = gen_ROM(door_name)
    
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