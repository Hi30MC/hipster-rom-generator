from enum import Enum
from typing import Literal


class Move(Enum):
    STOP = "stop"
    WAIT = "wait"
    STOAF = "stoaf"
    B = "b"
    C = "c"
    D = "d"
    E = "E"
    SSTO = "ssto"
    BOBS = "bobs"
    WORM = "worm"
    FOLD = "fold"


stop = Move.STOP
wait = Move.WAIT
stoaf = Move.STOAF
b = Move.B
c = Move.C
d = Move.D
e = Move.E
ssto = Move.SSTO
bobs = Move.BOBS
worm = Move.WORM
fold = Move.FOLD


def closing(): return [
    *[ssto, b, worm]*4,
    stoaf, ssto, c, b, stoaf, stop
]


def opening(): return [
    *row1(), b, ssto,
    * row2(), stoaf, b, ssto,
    * row3(), stoaf, ssto,
    * row4(), stoaf, ssto,
    * row5(), stoaf, ssto
]


def row1(): return [
    stoaf, b, stoaf, c, b
]


def retract2(): return [
    c, stoaf, c, b,
    e, d, d, *row1()
]


def row2(): return [
    e, b,  # maybe d
    bobs,
    b, b, ssto, ssto,
    *retract2(),
]


def otherRow2(): return [
    bobs, bobs, stoaf,
    b, b, ssto, ssto, *retract2()
]


"""
It's actually
obs()
pow(0)
retract2()
"""


def row3(): return [
    e, b,
    bobs, c, stoaf, stoaf, c, b, b, ssto, ssto,
    c, b, stoaf, b, c, b, e,  # pull1()?
    *row2()
]


def pull2(): return [
    e, b,
    bobs, b, b, ssto, ssto,
    c, stoaf, c, b,
    b, e, d, d, c, b
]


def row4(): return [
    e, b, *row4High()
]


def row4High(): return [
    bobs,
    d, b, stoaf, stoaf, ssto, ssto,
    b, stoaf,
    d, c, b, b, ssto, ssto,
    fold, *pull2(),
    fold, e,
    *row3()
]


def pull3(): return [
    e, b,
    bobs, c, stoaf, stoaf, c, b, b, ssto, ssto,
    c, b, *row1(),
    b, e, d, d, c, b,
]


def cooked(): return [
    bobs, bobs, ssto, bobs, bobs, stoaf,
]


def row5(): return [
    e, fold, b, bobs,
    e, b,
    *cooked(),
    *[b]*6,
    ssto, ssto,
    bobs, *retract2(), b, ssto, ssto,
    fold, *row4High(),  # might be redundant fold, fix later
]

# todo, extract common from row4()


def pull4(): return [
    e, b, bobs,
    d, b, stoaf, stoaf, ssto, ssto,
    b, stoaf,
    d, c, b, b, ssto, ssto,
    *row2(),
]


def row6(): return [
    e, fold, b, bobs,
    e, b,  # maybe
    # *cooked(),
    bobs, bobs, stoaf,
    c, *[stoaf]*8,  # end extend6
    # tuck
    ssto, ssto, b, c, b, bobs, bobs, stoaf,
    c, stoaf, stoaf,
    b, c, b,
    bobs, bobs,
    e, d, d, c, b, b,
    ssto, ssto,
    *pull4()
]
