from os import path, getcwd
from nbtlib.tag import *
from gen.util import gen_ss
from gen.out import sequence as seq
from gen.util.exceptions import KeyOverloadError
from gen.util.types import Minecart
from .gen_params import GenParams


def pad_sequence(
    sequence: list[int], wait_move: int | None, min_length: int
) -> list[int]:
    if len(sequence) >= min_length:
        return sequence
    if wait_move is None:
        raise KeyOverloadError
    return sequence + [wait_move] * (min_length - len(sequence))


def gen_ROM(ss_sequence: list[int], wait_move: int | None, params: GenParams):
    if params.cut_wait_moves:
        return gen_ROM_OPTIMIZED(ss_sequence, wait_move, params)
    else:
        return gen_ROM_UNOPTIMIZED(ss_sequence, wait_move, params)


def gen_ROM_OPTIMIZED(ss_sequence: list[int], wait_move: int | None, params: GenParams):
    raise NotImplementedError
    # only for 27x for now
    # assumes you have enough moves to fill min cart count and there is no terminal wait move

    # generate sequence
    sequence = seq.gen(door_name)

    # get wait move ss from encoding table
    ss_encode = encoding.read_encoding_from_file(door_name)
    wait = ss_encode["wait"]

    # Ensure relevant params are declared
    check_params(
        params, door_meta_path, ["density", "min_carts", "medium", "min_items_per_cart"]
    )

    cart_list = []

    # shitty ass way to one-line splitting a list based on wait move value
    sequence = [
        [int(y) for y in x.split()]
        for x in " ".join([str(x) for x in sequence]).split(str(wait))
    ]
    queue = []
    queue += sequence.pop(0)
    while len(queue) > 0:
        if len(sequence) == 0:
            break
        if len(queue) <= 27:  # entire queue can fit into one cart
            if (
                len(queue) > params.min_items_per_cart
            ):  # entire quene can fit into one cart and also cover the minimum
                if (
                    sequence[0] == [] and len(queue) < 27
                ):  # if next is empty, and has space, append wait and pop the next []
                    _ = sequence.pop(0)
                cart = gen.cart(params.pos)  # gen empty cart
                for slot in range(len(queue)):  # add entire queue to cart slots 0 ... n
                    ss = queue.pop(0)
                    if params.medium == "shulker":
                        item = gen_ss.shulker_for_ss(slot, ss)
                    elif params.medium == "disc":
                        item = gen_ss.disc_for_ss(slot, ss)
                    else:
                        raise ParameterValueError(door_meta_path, "medium")
                    manip.add_item_to_cart(cart, item)
                cart_list.append(cart)  # add cart to cart list
            else:  # less than minimum present
                queue.append(wait)
                queue += sequence.pop(0)
        elif (
            len(queue) <= 27 + params.min_items_per_cart
        ):  # in the case(s) that subtracting 27 wouldn't leave enough items in next cart to cover minimum
            cart = gen.cart(params.pos)  # gen new cart
            for slot in range(
                len(queue) // 2
            ):  # put first floor(len(queue)/2) items in cart slots 0 ... n
                ss = queue.pop(0)
                if params.medium == "shulker":
                    item = gen_ss.shulker_for_ss(slot, ss)
                elif params.medium == "disc":
                    item = gen_ss.disc_for_ss(slot, ss)
                else:
                    raise ParameterValueError(door_meta_path, "medium")
                manip.add_item_to_cart(cart, item)
            cart_list.append(cart)  # add cart to cart list
        else:  # safe to pop 27 from queue and have enough to cover minimum of next
            cart = gen.cart(params.pos)  # gen new cart
            for slot in range(27):  # put first 27 items in cart slots 0 ... 26
                ss = queue.pop(0)
                if params.medium == "shulker":
                    item = gen_ss.shulker_for_ss(slot, ss)
                elif params.medium == "disc":
                    item = gen_ss.disc_for_ss(slot, ss)
                else:
                    raise ParameterValueError(door_meta_path, "medium")
                manip.add_item_to_cart(cart, item)
            cart_list.append(cart)  # add cart to cart list
        if (len(queue) == 0) and len(
            sequence
        ) > 0:  # if queue is empty and sequence is not done
            if sequence[0] == []:
                queue.append(wait)
            queue += sequence.pop(0)

    return cart_list


def gen_ROM_UNOPTIMIZED(
    sequence: list[int],
    wait_move: int | None,
    params: GenParams,
) -> list[Minecart]:
    if params.density == 1:  # 1 cart per move-type ROM
        sequence = pad_sequence(sequence, wait_move, params.min_carts)
        return [gen_ss.cart_for_ss(x, pos=params.cart_pos) for x in sequence]

    elif params.density == 27:
        raise NotImplementedError("TODO")
        min_items = params.min_carts * params.min_items_per_cart

        # pad sequence for minimum move count
        sequence = pad_sequence(params, ss_encode, sequence, min_items)

        # put the items in the carts, lil' bro
        cart_list = [gen.cart(pos=params.pos)]
        min_items -= params.min_items_per_cart
        slot = 0
        while len(sequence) > 0:
            if len(cart_list[-1]["Items"]) > 26:
                cart_list.append(gen.cart(pos=params.pos))
                min_items -= params.min_items_per_cart
                slot = 0
            elif len(sequence) > min_items:
                ss = sequence.pop(0)
                if params.medium == "shulker":
                    item = gen_ss.shulker_for_ss(slot, ss)
                elif params.medium == "disc":
                    item = gen_ss.disc_for_ss(slot, ss)
                else:
                    raise ParameterValueError(door_meta_path, "medium")
                manip.add_item_to_cart(cart_list[-1], item)
                slot += 1
            else:
                cart_list.append(gen.cart(pos=params.pos))
                min_items -= params.min_items_per_cart
                slot = 0
        return cart_list

    elif params.density == 729:
        raise NotImplementedError("TODO")
        """
        This code works in 95% of use cases, but fails with min_items_per_cart < 27 and less than full minimum carts (min carts * 729)
        due to crappy spaghetti logic used below. I will be reworking this algo to be less shit, but don't expect it to be in the final
        version any time soon. It works for literally everything else, so deal with it. Have you just tried making your sequence longer?
        """

        # Ensure "medium", "min_items_per_cart", and "min_items_per_shulker" keys are defined
        check_params(
            params,
            door_meta_path,
            ["medium", "min_items_per_cart", "min_items_per_shulker"],
        )

        min_items = (
            params.min_carts * params.min_items_per_cart * params.min_items_per_shulker
        )
        min_shulkers = params.min_carts * params.min_items_per_cart

        # pad sequence for minimum move count
        sequence = pad_sequence(params, ss_encode, sequence, min_items)

        # solving the sphere packing problem one disc at a time
        cart_list = [gen.cart(pos=params.pos)]  # init with one cart
        manip.add_item_to_cart(cart_list[-1], gen.shulker(0))  # init with one shulker
        # update minima
        min_items -= params.min_items_per_shulker
        min_shulkers -= params.min_items_per_cart
        # init holding slots
        cart_slot = 1
        box_slot = 0
        while len(sequence) > 0:
            if (
                len(cart_list[-1]["Items"][-1]["tag"]["BlockEntityTag"]["Items"]) > 26
            ):  # add shulker if full
                if (
                    len(cart_list[-1]["Items"]) > 26
                ):  # add cart if cart full AND shulker is full, then continue to add shulker
                    cart_list.append(gen.cart(pos=params.pos))
                    cart_slot = 0
                    min_shulkers -= params.min_items_per_cart
                manip.add_item_to_cart(cart_list[-1], gen.shulker(cart_slot))
                min_items -= params.min_items_per_shulker
                cart_slot += 1
                box_slot = 0
            elif (
                len(sequence) > min_items
                and len(sequence) / params.min_items_per_shulker > min_shulkers
            ):  # add if enough
                ss = sequence.pop(0)
                item = gen_ss.disc_for_ss(box_slot, ss)
                box = cart_list[-1]["Items"][-1]
                new_box_inv = List[Compound](
                    box["tag"]["BlockEntityTag"]["Items"] + [item]
                )
                box["tag"]["BlockEntityTag"].update({"Items": new_box_inv})
                box_slot += 1
            else:  # add new box if at minimum remaining
                # add cart if cart full or new cart needs to be added to make minimum carts
                if (
                    len(cart_list[-1]["Items"]) > 26
                    or len(sequence) // params.min_items_per_shulker <= min_shulkers
                ):
                    cart_list.append(gen.cart(pos=params.pos))
                    cart_slot = 0
                    min_shulkers -= params.min_items_per_cart
                manip.add_item_to_cart(cart_list[-1], gen.shulker(cart_slot))
                cart_slot += 1
                min_items -= params.min_items_per_shulker
                box_slot = 0
        return cart_list
    else:
        print(
            f"Generating empty ROM, 'density' argument in '{door_meta_path}/rom_params.txt' is not equal to a valid density argument. (1, 27, 729)"
        )
        return []

    return -1  # just in case <3
