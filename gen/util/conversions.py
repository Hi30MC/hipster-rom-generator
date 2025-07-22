from os import path, getcwd
from ast import literal_eval

def shulker():
    shulker_conversion = {
        1: 1,
        2: 2,
        3: 4,
        4: 6,
        5: 8,
        6: 10,
        7: 12,
        8: 14,
        9: 16,
        10: 18,
        11: 20,
        12: 22,
        13: 24,
        14: 26,
        15: 27 
    }
    return shulker_conversion

def chest():
    return shulker()

def disc():
    disc_conversion ={
        1: "minecraft:music_disc_13",
        2: "minecraft:music_disc_cat",
        3: "minecraft:music_disc_blocks",
        4: "minecraft:music_disc_chirp",
        5: "minecraft:music_disc_far",
        6: "minecraft:music_disc_mall",
        7: "minecraft:music_disc_mellohi",
        8: "minecraft:music_disc_stal",
        9: "minecraft:music_disc_strad",
        10: "minecraft:music_disc_ward",
        11: "minecraft:music_disc_11",
        12: "minecraft:music_disc_wait",
        13: "minecraft:music_disc_pigstep",
        14: "minecraft:music_disc_otherside",
        15: "minecraft:music_disc_5"
    }
    return disc_conversion