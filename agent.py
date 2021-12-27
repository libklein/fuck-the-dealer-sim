from abc import ABC
from random import Random
from collections import Counter, defaultdict
from typing import Dict, Optional

from card import Card, CardFace
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
        return True

    def notify_round_end(self, state: Observation, drawn_card: Card, looser: 'Agent', drinks: int):
        pass

class GreedyAgent(RandomizingAgent):
    def __init__(self, id: int, risk_aversity: float):
        super().__init__(id)
        self.last_card = None
        self.risk_aversity = risk_aversity

    def _get_cards_counts_by_face(self, card_counts: Dict[Card, int]) -> Dict[CardFace, int]:
        cards_by_face = defaultdict(int)
        for card, count in card_counts.items():
            cards_by_face[card.face] += count
        return dict(cards_by_face)

    def _get_card_probability(self, card_counts: Dict[CardFace, int]) -> Dict[CardFace, float]:
        total_cards = sum(card_counts.values())
        return {
            face: 0 if count == 0 else count / total_cards for face, count in card_counts.items()
        }

    def _compute_expected_drinks(self, face_probabilities: Dict[CardFace, float], drinks_for_face: Dict[CardFace, int]) -> Dict[CardFace, float]:
        return {
            face: face_probabilities[face] * drinks_for_face[face] for face in face_probabilities
        }

    def _expected_drinks(self, counts: Dict[CardFace, int], pick: CardFace, first_pick: bool = False) -> float:
        probabilities = self._get_card_probability(counts)
        if first_pick:
            expected_drinks = 0
            for actual_face, p in probabilities.items():
                if actual_face == pick:
                    continue
                comp = gt if (actual_face.value > pick.value) else lt
                second_level_counts = {face: count for face, count in counts.items() if comp(face, actual_face)}
                expected_drinks += sum(self._expected_drinks(second_level_counts,
                                                             pick=second_level_pick,
                                                             first_pick=False)
                                       for second_level_pick in second_level_counts)
            return expected_drinks
        else:
            return sum(p * abs(pick.value - face.value) for face, p in probabilities.items())

    def ask_first_time(self, state: Observation) -> Card:
        card_counts_by_face = self._get_cards_counts_by_face(state.cards_remaining)
        face_probabilities = self._get_card_probability(card_counts_by_face)
        expected_drinks_for_self = self._compute_expected_drinks(face_probabilities, {
            face: self._expected_drinks(card_counts_by_face, face, first_pick=True) for face in face_probabilities
        })
        expected_drinks_for_dealer = self._compute_expected_drinks(face_probabilities, {face: 5 for face in face_probabilities})
        # Compute estimated schlucke according to "risk awareness", which is in [0, 1] and
        # gives the desire to fuck the dealer
        self.last_card = self._pick_from_weights(expected_drinks_for_self, expected_drinks_for_dealer, state.cards_remaining.keys())
        return self.last_card

    def _pick_from_weights(self, expected_drinks_for_self, expected_drinks_for_dealer, cards):
        weighted_probability = {
            face: self.risk_aversity * expected_drinks_for_self[face] +
                  (1.0 - self.risk_aversity) * expected_drinks_for_dealer[face] for face in expected_drinks_for_self
        }
        picked_face = self.generator.choices(population=list(weighted_probability.keys()),
                                             weights=list(weighted_probability.values()))[0]
        return next(x for x in cards if x.face is picked_face)

    def ask_second_time(self, state: Observation, is_higher: bool) -> Card:
        comp = gt if is_higher else lt
        card_counts_by_face = {face: count for face, count in self._get_cards_counts_by_face(state.cards_remaining).items() if comp(face, self.last_card.face)}
        face_probabilities = self._get_card_probability(card_counts_by_face)

        expected_drinks_for_self = self._compute_expected_drinks(face_probabilities, {
            face: self._expected_drinks(card_counts_by_face, face, first_pick=False) for face in face_probabilities
        })

        expected_drinks_for_dealer = self._compute_expected_drinks(face_probabilities, {face: 3 for face in face_probabilities})

        self.last_card = None
        return self._pick_from_weights(expected_drinks_for_self, expected_drinks_for_dealer, state.cards_remaining.keys())

    def wants_to_switch(self, state: Observation) -> bool:
        return True

    def notify_round_end(self, state: Observation, drawn_card: Card, looser: 'Agent', drinks: int):
        pass
