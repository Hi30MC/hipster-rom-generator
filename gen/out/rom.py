from os import path, getcwd
from nbtlib.tag import *
from gen.util import gen_ss, gen, manip
from gen.util.exceptions import *
from gen.out import encoding
from gen.out import sequence as seq
from ast import literal_eval
from types import SimpleNamespace

def check_params(namespace, path: str, params: list[str]) -> None:
    for p in params:
        if not hasattr(namespace, p):
            raise MissingParameterError(path, p)

def pad_sequence(meta: SimpleNamespace, ss_encode, sequence, minimum) -> List[int]:
    if len(sequence) < minimum:
        # assign wait move if not already
        if "wait" not in ss_encode.keys():
            wait_backups = [x for x in range(1,16) if x not in ss_encode.values()]
            if len(wait_backups) == 0:
                raise KeyOverloadError()
            ss_encode.update({"wait": wait_backups[0]})
        # pad to minimum
        if sequence[-1] == 0: # pad waits before the STOP command
            sequence = sequence[:-1] + [ss_encode["wait"]] * (meta.min_carts - len(sequence)) + [0]
        else:
            sequence += [ss_encode["wait"]] * (meta.min_carts - len(sequence))
    return sequence

def gen_ROM(door_name: str):
    # get rom metadata
    door_meta_path = path.join(getcwd(), "door_meta", door_name)

    with open(path.join(door_meta_path,"rom_params.txt"), "r") as f:
        rom_params = literal_eval(f.read())

    # create pos of carts if not specified
    if "pos" not in rom_params.keys():
        rom_params.update({"pos": List[Double]([0.5, 0, 0.5])})

    meta = SimpleNamespace(**rom_params)

    check_params(meta, door_meta_path, ["cut_wait_moves"])

    # check if cut_wait_move is active, if so, run optimized code
    if meta.cut_wait_moves:
        return gen_ROM_OPTIMIZED(door_name, meta)
    else:
        return gen_ROM_UNOPTIMIZED(door_name, meta)


def gen_ROM_OPTIMIZED(door_name: str, meta: SimpleNamespace):
    # only for 27x for now
    # assumes you have enough moves to fill min cart count and there is no terminal wait move

    # generate sequence
    sequence = seq.gen(door_name)

    # get wait move ss from encoding table
    ss_encode = encoding.get(door_name)
    wait = ss_encode["wait"]

    # get meta path
    door_meta_path = path.join(getcwd(), "door_meta", door_name)

    # Ensure relevant params are declared
    check_params(meta, door_meta_path, ["density", "min_carts", "medium", "min_items_per_cart"])

    cart_list = []

    # shitty ass way to one-line splitting a list based on wait move value
    sequence = [[int(y) for y in x.split()] for x in " ".join([str(x) for x in sequence]).split(str(wait))]
    queue = []
    queue += sequence.pop(0)
    while (len(queue) > 0):
        if len(sequence) == 0:
            break
        if len(queue) <= 27: # entire queue can fit into one cart
            if len(queue) > meta.min_items_per_cart: # entire quene can fit into one cart and also cover the minimum
                if sequence[0] == [] and len(queue) < 27: # if next is empty, and has space, append wait and pop the next []
                    _ = sequence.pop(0)
                cart = gen.cart(meta.pos) # gen empty cart
                for slot in range(len(queue)): # add entire queue to cart slots 0 ... n
                    ss = queue.pop(0)
                    if meta.medium == "shulker":
                        item = gen_ss.shulker(slot, ss)
                    elif meta.medium == "disc":
                        item = gen_ss.disc(slot, ss)
                    else:
                        raise ParameterValueError(door_meta_path, "medium")
                    manip.add_item_to_cart(cart, item)
                cart_list.append(cart) # add cart to cart list
            else: # less than minimum present
                queue.append(wait)
                queue += sequence.pop(0)
        elif len(queue) <= 27 + meta.min_items_per_cart: # in the case(s) that subtracting 27 wouldn't leave enough items in next cart to cover minimum
            cart = gen.cart(meta.pos) # gen new cart
            for slot in range(len(queue) // 2): # put first floor(len(queue)/2) items in cart slots 0 ... n
                ss = queue.pop(0)
                if meta.medium == "shulker":
                    item = gen_ss.shulker(slot, ss)
                elif meta.medium == "disc":
                    item = gen_ss.disc(slot, ss)
                else:
                    raise ParameterValueError(door_meta_path, "medium")
                manip.add_item_to_cart(cart, item)
            cart_list.append(cart) # add cart to cart list
        else: # safe to pop 27 from queue and have enough to cover minimum of next
            cart = gen.cart(meta.pos) # gen new cart
            for slot in range(27): # put first 27 items in cart slots 0 ... 26
                ss = queue.pop(0)
                if meta.medium == "shulker":
                    item = gen_ss.shulker(slot, ss)
                elif meta.medium == "disc":
                    item = gen_ss.disc(slot, ss)
                else:
                    raise ParameterValueError(door_meta_path, "medium")
                manip.add_item_to_cart(cart, item)
            cart_list.append(cart) # add cart to cart list
        if (len(queue) == 0) and len(sequence) > 0: # if queue is empty and sequence is not done
            if sequence[0] == []:
                queue.append(wait)
            queue += sequence.pop(0)

    return cart_list

def gen_ROM_UNOPTIMIZED(door_name: str, meta: SimpleNamespace):
    # generate sequence
    sequence = seq.gen(door_name)

    # get wait move ss from encoding table
    ss_encode = encoding.get(door_name)

    # get meta path
    door_meta_path = path.join(getcwd(), "door_meta", door_name)

    # Ensure a couple base params are declared
    check_params(meta, door_meta_path, ["density", "min_carts"])


    if meta.density == 1: # 1 cart per move-type ROM

        # pad sequence for minimum move count
        sequence = pad_sequence(meta, ss_encode, sequence, meta.min_carts)

        # convert sequence into cartstack, return
        return [gen_ss.cart(x, pos=meta.pos) for x in sequence]

    elif meta.density == 27:
        # Ensure "medium" and "min_items_per_cart" keys are defined
        check_params(meta, door_meta_path, ["medium", "min_items_per_cart"])

        min_items = meta.min_carts * meta.min_items_per_cart

        # pad sequence for minimum move count
        sequence = pad_sequence(meta, ss_encode, sequence, min_items)

        # put the items in the carts, lil' bro
        cart_list = [gen.cart(pos=meta.pos)]
        min_items -= meta.min_items_per_cart
        slot = 0
        while len(sequence) > 0:
            if len(cart_list[-1]["Items"]) > 26:
                cart_list.append(gen.cart(pos=meta.pos))
                min_items -= meta.min_items_per_cart
                slot = 0
            elif len(sequence) > min_items:
                ss = sequence.pop(0)
                if meta.medium == "shulker":
                    item = gen_ss.shulker(slot, ss)
                elif meta.medium == "disc":
                    item = gen_ss.disc(slot, ss)
                else:
                    raise ParameterValueError(door_meta_path, "medium")
                manip.add_item_to_cart(cart_list[-1], item)
                slot += 1
            else:
                cart_list.append(gen.cart(pos=meta.pos))
                min_items -= meta.min_items_per_cart
                slot = 0
        return cart_list

    elif meta.density == 729:
        """
        This code works in 95% of use cases, but fails with min_items_per_cart < 27 and less than full minimum carts (min carts * 729)
        due to crappy spaghetti logic used below. I will be reworking this algo to be less shit, but don't expect it to be in the final
        version any time soon. It works for literally everything else, so deal with it. Have you just tried making your sequence longer?
        """

        # Ensure "medium", "min_items_per_cart", and "min_items_per_shulker" keys are defined
        check_params(meta, door_meta_path, ["medium", "min_items_per_cart", "min_items_per_shulker"])

        min_items = meta.min_carts * meta.min_items_per_cart * meta.min_items_per_shulker
        min_shulkers = meta.min_carts * meta.min_items_per_cart

        # pad sequence for minimum move count
        sequence = pad_sequence(meta, ss_encode, sequence, min_items)

        # solving the sphere packing problem one disc at a time
        cart_list = [gen.cart(pos=meta.pos)] #init with one cart
        manip.add_item_to_cart(cart_list[-1], gen.shulker(0)) # init with one shulker
        # update minima
        min_items -= meta.min_items_per_shulker
        min_shulkers -= meta.min_items_per_cart
        # init holding slots
        cart_slot = 1
        box_slot = 0
        while len(sequence) > 0:
            if len(cart_list[-1]["Items"][-1]["tag"]["BlockEntityTag"]["Items"]) > 26: # add shulker if full
                if len(cart_list[-1]["Items"]) > 26: #add cart if cart full AND shulker is full, then continue to add shulker
                    cart_list.append(gen.cart(pos=meta.pos))
                    cart_slot = 0
                    min_shulkers -= meta.min_items_per_cart
                manip.add_item_to_cart(cart_list[-1], gen.shulker(cart_slot))
                min_items -= meta.min_items_per_shulker
                cart_slot += 1
                box_slot = 0
            elif len(sequence) > min_items and len(sequence) / meta.min_items_per_shulker > min_shulkers: # add if enough
                ss = sequence.pop(0)
                item = gen_ss.disc(box_slot, ss)
                box = cart_list[-1]["Items"][-1]
                new_box_inv = List[Compound](box["tag"]["BlockEntityTag"]["Items"] + [item])
                box["tag"]["BlockEntityTag"].update({"Items": new_box_inv})
                box_slot += 1
            else: # add new box if at minimum remaining
                #add cart if cart full or new cart needs to be added to make minimum carts
                if len(cart_list[-1]["Items"]) > 26 or len(sequence) // meta.min_items_per_shulker <= min_shulkers:
                    cart_list.append(gen.cart(pos=meta.pos))
                    cart_slot = 0
                    min_shulkers -= meta.min_items_per_cart
                manip.add_item_to_cart(cart_list[-1], gen.shulker(cart_slot))
                cart_slot += 1
                min_items -= meta.min_items_per_shulker
                box_slot = 0
        return cart_list
    else:
        print(f"Generating empty ROM, 'density' argument in '{door_meta_path}/rom_params.txt' is not equal to a valid density argument. (1, 27, 729)")
        return []

    return -1 # just in case <3
