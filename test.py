from functools import partialmethod
from typing import Optional
import pandas as pd

from card import Card
from game import Game
from agent import RandomizingAgent, Agent
from observation import Observation


def log_dealer_switch(state: Observation, new_dealer: Agent):
    print(f"Switching dealer to {new_dealer}")

def log_round_end(looser: Agent, drinks: int, card: Card, state: Observation):
    print(f"Round end! {looser} has to drink {drinks}! Picked {card}")

class PandasLogger:
    def __init__(self, game: Game, game_id: Optional[int] = None):
        self.game = game
        self.game_id = game_id

        self.first_dealer = self.game.dealer
        self.first_player = self.game.get_next_player()
        self.drinks_by_player = {player: 0 for player in self.game.players}
        self.turns = 0
        self.dealer_losses = 0
        self.rounds = []

        self.game.on_switch_dealer += lambda *args, **kwargs: self.dealer_switched(*args, **kwargs)
        self.game.on_round_end += lambda *args, **kwargs: self.round_ended(*args, **kwargs)

    def dealer_switched(self, state: Observation, new_dealer: Agent):
        pass

    def round_ended(self, looser: Agent, drinks: int, card: Card, state: Observation):
        self.rounds.append(dict(looser=looser, drinks=drinks, card=card, state=state, dealer=state.dealer))
        self.drinks_by_player[looser] += drinks

    def to_df(self):
        game_df = pd.DataFrame([dict(first_dealer=self.first_dealer, first_player=self.first_player,
                                  total_turns=self.turns, dealer_losses=self.dealer_losses)])
        game_df['game_id'] = self.game_id
        rounds_df = pd.DataFrame(self.rounds)
        rounds_df['round_id'] = rounds_df.index
        rounds_df['game_id'] = self.game_id
        return game_df, rounds_df

games_df = pd.DataFrame()
rounds_df = pd.DataFrame()

for game_id in range(100):
    game = Game(players=[RandomizingAgent(x) for x in range(4)], seed=str(game_id))

    game_logger = PandasLogger(game=game, game_id=game_id)

    for _ in game.play():
        pass

    game_df, round_df = game_logger.to_df()
    games_df = games_df.append(game_df, ignore_index=True)
    rounds_df = rounds_df.append(round_df, ignore_index=True)

games_df.reset_index(drop=True, inplace=True)
rounds_df.reset_index(drop=True, inplace=True)

games_df.to_csv('games.csv')
rounds_df.to_csv('rounds.csv')