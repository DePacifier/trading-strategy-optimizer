from enum import IntEnum

class Position(IntEnum):
    LONG = 1
    SHORT = -1
    NEUTRAL = 0

class TradeAction(IntEnum):
    ENTER_LONG = 1
    ENTER_SHORT = 2
    EXIT = 3

class TradeMode(IntEnum):
    LONG_ONLY = 1
    SHORT_ONLY = -1
    BOTH = 0
