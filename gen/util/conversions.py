import os
from ast import literal_eval

def get_shulker_conversion():
    with open(os.path.join(os.getcwd(), "gen", "conversions", "shulker.txt"), 'r') as f:
        shulker_data = f.read()
    shulker_conversion = literal_eval(shulker_data)
    return shulker_conversion

def get_disc_conversion():
    with open(os.path.join(os.getcwd(), "gen", "conversions", "shulker.txt"), "r") as f:
        disc_data = f.read()
    disc_conversion = literal_eval(disc_data)
    return disc_conversion