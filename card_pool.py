from itertools import product
from random import Random
from typing import Optional, List
from collections import Counter

from util import generate_random_string, get_generator
from card import CardFace, Card, Suit


def _count_cards(cards: List[Card]) -> Counter:
    return Counter(cards)


class NoCardsRemainingError(Exception):
    pass


class CardPool:
    def __init__(self, generator: Optional[Random] = None, seed: Optional[str] = None):
        self.remaining_cards = [
            Card(suit=suit, face=face) for suit, face in product(Suit, CardFace)
        ]
        self.drawn_cards = []
        self.generator, self.seed = get_generator(seed=seed, generator=generator)

    @property
    def remaining_card_counts(self):
        return _count_cards(self.remaining_cards)

    @property
    def drawn_card_counts(self):
        return _count_cards(self.drawn_cards)

    def draw_card(self, replace=False) -> Card:
        if len(self.remaining_cards) == 0:
            raise NoCardsRemainingError

        card = self.generator.choice(self.remaining_cards)

        if replace:
            self.remaining_cards.remove(card)
        self.drawn_cards.append(card)

        return card