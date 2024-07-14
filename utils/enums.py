from enum import IntEnum

class Position(IntEnum):
    LONG = 1
    SHORT = -1
    NEUTRAL = 0

class TradeAction(IntEnum):
    ENTER_LONG = 1
    ENTER_SHORT = 2
    EXIT = 3