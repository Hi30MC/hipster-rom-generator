from os import path, getcwd
from ast import literal_eval

def shulker():
    with open(path.join(getcwd(), "gen", "conversions", "shulker.txt"), 'r') as f:
        shulker_data = f.read()
    shulker_conversion = literal_eval(shulker_data)
    return shulker_conversion

def chest():
    return shulker()

def disc():
    with open(path.join(getcwd(), "gen", "conversions", "shulker.txt"), "r") as f:
        disc_data = f.read()
    disc_conversion = literal_eval(disc_data)
    return disc_conversion