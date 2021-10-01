from dataclasses import dataclass, field
from enum import IntEnum, auto, unique

@unique
class Suit(IntEnum):
    HEART = auto()
    SPADE = auto()
    DIAMOND = auto()
    CLUB = auto()

    __names__ = {
        HEART: 'H',
        SPADE: 'S',
        DIAMOND: 'D',
        CLUB: 'C'
    }

    def __str__(self):
        return Suit.__names__[self.value]

@unique
class CardFace(IntEnum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

    def __str__(self):
        if self.value <= CardFace.TEN:
            return str(self.value)
        return self.name[0]


@dataclass(order=True)
class Card:
    suit: Suit = field(compare=False)
    face: CardFace = field(compare=True)

    def __eq__(self, other) -> bool:
        if isinstance(other, Card):
            return (self.suit, self.face) == (other.suit, other.face)
        if isinstance(other, CardFace):
            return self.face == other
        raise NotImplementedError

    def __str__(self):
        return str(self.suit)+str(self.face)

    def __hash__(self):
        return id(self)