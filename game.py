from random import Random
from typing import Optional, List, Tuple
from events import Events

from agent import Agent
from card import Card
from card_pool import CardPool
from observation import Observation
from util import get_generator


class Game(Events):
    __events__ = ('on_round_end', 'on_switch_dealer', )

    def __init__(self, players: List[Agent], generator: Optional[Random] = None, seed: Optional[str] = None):
        super().__init__()
        self.generator, self.seed = get_generator(generator=generator, seed=seed)
        self.card_pool = CardPool(seed=self.seed)
        self.players: List[Agent] = players

        self.dealer: Agent = self.players[0]
        self.last_player: Agent = self.dealer
        self.turns_since_last_success: int = 0

    def get_next_player(self) -> Agent:
        next_player = self.last_player
        while (next_player := self._get_player(after=next_player)) is self.dealer:
            pass
        return next_player

    def get_game_state(self) -> Observation:
        return Observation(players=self.players, dealer=self.dealer, cards_remaining=self.card_pool.remaining_card_counts)

    def _get_player(self, after: Agent) -> Agent:
        return self.players[(self.players.index(after) + 1) % len(self.players)]

    @property
    def _can_switch_dealer(self) -> bool:
        return self.turns_since_last_success >= 3

    @property
    def is_game_over(self) -> bool:
        return len(self.card_pool.remaining_cards) == 0

    def _end_round(self, player: Agent, looser: Agent):
        self.turns_since_last_success += 1
        if looser is self.dealer:
            self.turns_since_last_success = 0
        self.last_player = player

    def _switch_dealer(self):
        self.dealer = self._get_player(after=self.dealer)
        self.turns_since_last_success = 0

    def next_turn(self):
        # Ask dealer
        if self._can_switch_dealer and self.dealer.wants_to_switch(state=self.get_game_state()):
            state = self.get_game_state()
            self._switch_dealer()
            self.on_switch_dealer(state, self.dealer)
            return self.next_turn()

        # Draw card and ask player
        current_state = self.get_game_state()
        card = self.card_pool.draw_card(replace=True)
        player = self.get_next_player()

        looser, drinks = self.ask_player(card, current_state, player)

        for p in self.players:
            p.notify_round_end(current_state, card, looser, drinks)

        self._end_round(player=player, looser=looser)
        self.on_round_end(looser=looser, drinks=drinks, card=card, state=current_state)
        return looser, drinks, card

    def play(self):
        while not self.is_game_over:
            yield self.next_turn()

    def ask_player(self, card: Card, current_state: Observation, player: Agent) -> Tuple[Agent, int]:
        answer = player.ask_first_time(state=current_state)
        if answer == card.face:
            return self.dealer, 5

        is_higher = answer < card

        answer = player.ask_second_time(state=current_state, is_higher=is_higher)
        if answer == card.face:
            return self.dealer, 3
        # Dealer drinks
        return player, abs(card.face - answer.face)
