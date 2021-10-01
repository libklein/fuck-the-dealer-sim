from abc import ABC
from random import Random

from card import Card
from observation import Observation
from operator import lt, gt


class Agent(ABC):
    def __init__(self, id: int):
        self.id = id

    def ask_first_time(self, state: Observation) -> Card:
        pass

    def ask_second_time(self, state: Observation, is_higher: bool) -> Card:
        pass

    def wants_to_switch(self, state: Observation) -> bool:
        pass

    def notify_round_end(self, state: Observation, drawn_card: Card, looser: 'Agent', drinks: int):
        # TODO Implement some bookkeeping?
        pass

    def __str__(self):
        return f'{type(self).__name__}-{self.id}'


class RandomizingAgent(Agent):
    def __init__(self, id: int):
        super().__init__(id)
        self.generator = Random()
        self.last_card = None

    def ask_first_time(self, state: Observation) -> Card:
        self.last_card = self.generator.choice(list(state.cards_remaining.keys()))
        return self.last_card

    def ask_second_time(self, state: Observation, is_higher: bool) -> Card:
        comp = gt if is_higher else lt
        return self.generator.choice([x for x in state.cards_remaining if comp(x, self.last_card)])

    def wants_to_switch(self, state: Observation) -> bool:
        return self.generator.choice((True, False))

    def notify_round_end(self, state: Observation, drawn_card: Card, looser: 'Agent', drinks: int):
        pass