from os import path, getcwd
from nbtlib.tag import *
from gen.util import ss_gen, main_gen, item_manip
from gen.out import ss_encode as enc
from gen.out import sequence as seq
from ast import literal_eval
from types import SimpleNamespace

def gen_ROM(door_name: str):
    # generate sequence
    sequence = seq.gen_ss_sequence(door_name)
    
    # get rom metadata
    door_meta_path = path.join(getcwd(), "door_meta", door_name) 

    with open(path.join(door_meta_path,"rom_params.txt"), "r") as f:
        rom_params = literal_eval(f.read())
    
    # create pos of carts if not specified
    if "pos" not in rom_params.keys():
        rom_params.update({"pos": [0.5, 0, 0.5]})
    
    meta = SimpleNamespace(**rom_params)
    
    # get encoding table
    ss_encode = enc.get_encode(door_name)
    
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
        return [ss_gen.gen_ss_cart(x, pos=meta.pos) for x in sequence]
    
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
        
        
        cart_list = [main_gen.gen_cart(pos=meta.pos)]
        min_items -= meta.min_items_per_cart
        slot = 0
        while len(sequence) > 0:
            if len(cart_list[-1]["Items"]) > 26:
                cart_list.append(main_gen.gen_cart(pos=meta.pos))
                min_items -= meta.min_items_per_cart
                slot = 0
            elif len(sequence) > min_items:
                ss = sequence.pop(0)
                if meta.medium == "shulker":
                    item = ss_gen.gen_ss_sb(slot, ss)
                elif meta.medium == "disc":
                    item = ss_gen.gen_ss_disc(slot, ss)
                else:
                    raise Exception(f"Invalid 'medium' type in {door_meta_path}/rom_params.txt")
                item_manip.add_item_to_cart(cart_list[-1], item)
                slot += 1
            else:
                cart_list.append(main_gen.gen_cart(pos=meta.pos))
                min_items -= meta.min_items_per_cart
                slot = 0
        return cart_list
        
        
        
    elif meta.density == 729:
        # Ensure "medium", "min_items_per_cart", and "min_items_per_shulker" keys are defined
        try:
            _ = meta.medium
        except:
            raise Exception(f"No value 'medium' defined in '{door_meta_path}/rom_params.txt'.")
        try:
            _ = meta.min_items_per_cart
        except:
            raise Exception(f"No value 'min_items_per_cart' defined in '{door_meta_path}/rom_params.txt'.")
        try:
            _ = meta.min_items_per_shulker
        except:
            raise Exception(f"No value 'min_items_per_shulker' defined in '{door_meta_path}/rom_params.txt'.")

        min_items = meta.min_carts * meta.min_items_per_cart * meta.min_items_per_shulker

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

        cart_list = [main_gen.gen_cart(pos=meta.pos)]
        item_manip.add_item_to_cart(cart_list[-1], main_gen.gen_shulker_box(0))
        min_items -= meta.min_items_per_shulker
        cart_slot = 1
        box_slot = 0
        while len(sequence) > 0:
            if len(cart_list[-1]["Items"][-1]["tag"]["BlockEntityTag"]["Items"]) > 26: # add shulker if full
                if len(cart_list[-1]["Items"]) > 26: #add cart if cart full AND shulker is full, then continue to add shulker
                    cart_list.append(gen_cart(pos=meta.pos))
                    cart_slot = 0
                item_manip.add_item_to_cart(cart_list[-1], main_gen.gen_shulker_box(cart_slot))
                min_items -= meta.min_items_per_shulker
                cart_slot += 1
                box_slot = 0
            elif len(sequence) > min_items: # add if enough
                ss = sequence.pop(0)
                item = ss_gen.gen_ss_disc(box_slot, ss)
                box = cart_list[-1]["Items"][-1]
                new_box_inv = List[Compound](box["tag"]["BlockEntityTag"]["Items"] + [item])
                box["tag"]["BlockEntityTag"].update({"Items": new_box_inv})
                box_slot += 1
            else: # add new box if at minimum remaining
                if len(cart_list[-1]["Items"]) > 26: #add cart if cart full AND shulker is at min cap, then continue to add shulker
                    cart_list.append(main_gen.gen_cart(pos=meta.pos))
                    cart_slot = 0
                item_mainp.add_item_to_cart(cart_list[-1], gen_shulker_box(cart_slot))
                cart_slot += 1
                min_items -= meta.min_items_per_shulker
                box_slot = 0
        return cart_list
    else:
        print(f"Generating empty ROM, 'density' argument in '{door_meta_path}/rom_params.txt' is not equal to a valid density argument.")
        return []

    return -1

def gen_ROM_OPTIMIZED(door_name: str):
    # only for 27x for now
    # assumes you have enough moves to fill min cart count and there is no terminal wait move

    # generate sequence
    sequence = seq.gen_ss_sequence(door_name)
    
    # get rom metadata
    door_meta_path = path.join(getcwd(), "door_meta", door_name) 
    with open(path.join(door_meta_path,"rom_params.txt"), "r") as f:
        rom_params = literal_eval(f.read())
    
    # create pos of carts if not specified
    if "pos" not in rom_params.keys():
        rom_params.update({"pos": [0.5, 0, 0.5]})
    
    meta = SimpleNamespace(**rom_params)
    
    # get wait move ss from encoding table
    ss_encode = enc.get_encode(door_name)
    wait = ss_encode["wait"]

    # Ensure a couple base params are declared
    try:
        _ = meta.density
    except:
        raise Exception(f"No value 'density' defined in '{door_meta_path}/rom_params.txt'.")
    try:
        _ = meta.min_carts
    except:
        raise Exception(f"No value 'min_carts' defined in '{door_meta_path}/rom_params.txt'.")    

    # Ensure "medium" and "min_items_per_cart" keys are defined
    try:
        _ = meta.medium
    except:
        raise Exception(f"No value 'medium' defined in '{door_meta_path}/rom_params.txt'.")
    try:
        _ = meta.min_items_per_cart
    except:
        raise Exception(f"No value 'min_items_per_cart' defined in '{door_meta_path}/rom_params.txt'.")
        
    # # pad sequence for minimum move count
    # if len(sequence) < min_items:
    #     # assign wait move if not already
    #     if "wait" not in ss_encode.keys():
    #         wait_backups = [x for x in range(1,16) if x not in ss_encode.values()]
    #         if len(wait_backups) == 0:
    #             raise Exception(f"No wait move availible to pad moves. Please create manually.")
    #         ss_encode.update({"wait": wait_backups[0]})
    #     # pad to minimum
    #     if sequence[-1] == 0: # pad waits before the STOP command
    #         sequence = sequence[:-1] + [ss_encode["wait"]] * (min_items - len(sequence)) + [0]
    #     else:
    #         sequence += [ss_encode["wait"]] * (min_items - len(sequence))
    
    cart_list = []

    # shitty ass way to one-line splitting a list based on wait move    
    sequence = [[int(y) for y in x.split()] for x in " ".join([str(x) for x in sequence]).split(str(wait))]
    queue = []
    print(sequence)
    queue += sequence.pop(0)    
    while (len(queue) > 0):
        print(queue)
        print(sequence)
        if len(sequence) == 0:
            break
        if len(queue) <= 27: # entire queue can fit into one cart
            if len(queue) > meta.min_items_per_cart: # entire quene can fit into one cart and also cover the minimum
                if sequence[0] == [] and len(queue) < 27: # if next is empty, and has space, append wait and pop the next []
                    _ = sequence.pop(0)
                cart = main_gen.gen_cart() # gen empty cart
                for slot in range(len(queue)): # add entire queue to cart slots 0 ... n
                    ss = queue.pop(0)
                    if meta.medium == "shulker":
                        item = ss_gen.gen_ss_sb(slot, ss)
                    elif meta.medium == "disc":
                        item = ss_gen.gen_ss_disc(slot, ss)
                    else:
                        raise Exception(f"Invalid 'medium' type in {door_meta_path}/rom_params.txt")
                    item_manip.add_item_to_cart(cart, item)
                cart_list.append(cart) # add cart to cart list
            else: # less than minimum present
                queue.append(wait)
                queue += sequence.pop(0)
        elif len(queue) <= 27 + meta.min_items_per_cart: # in the case(s) that subtracting 27 wouldn't leave enough items in next cart to cover minimum
            cart = main_gen.gen_cart() # gen new cart
            for slot in range(len(queue // 2)): # put first floor(len(queue)/2) items in cart slots 0 ... n
                ss = queue.pop(0)
                if meta.medium == "shulker":
                    item = ss_gen.gen_ss_sb(slot, ss)
                elif meta.medium == "disc":
                    item = ss_gen.gen_ss_disc(slot, ss)
                else:
                    raise Exception(f"Invalid 'medium' type in {door_meta_path}/rom_params.txt")
                item_manip.add_item_to_cart(cart, item)
            cart_list.append(cart) # add cart to cart list
        else: # safe to pop 27 from queue and have enough to cover minimum of next
            cart = gen(cart) # gen new cart
            for slot in range(27): # put first 27 items in cart slots 0 ... 26
                ss = queue.pop(0)
                if meta.medium == "shulker":
                    item = ss_gen.gen_ss_sb(slot, ss)
                elif meta.medium == "disc":
                    item = ss_gen.gen_ss_disc(slot, ss)
                else:
                    raise Exception(f"Invalid 'medium' type in {door_meta_path}/rom_params.txt")
                item_manip.add_item_to_cart(cart, item)
            cart_list.append(cart) # add cart to cart list
        if (len(queue) == 0) and len(sequence) > 0: # if queue is empty and sequence is not done
            if sequence[0] == []:
                queue.append(wait)
            queue += sequence.pop(0)

    return cart_list
