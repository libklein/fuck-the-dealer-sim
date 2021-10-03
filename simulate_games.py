from functools import partialmethod
from typing import Optional, Tuple
import pandas as pd
import argparse
from pathlib import Path

from card import Card
from game import Game
from agent import RandomizingAgent, Agent
from observation import Observation


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
        rounds_df = pd.DataFrame([
            dict(looser_id=round['looser'].id, dealer_id=round['dealer'].id,
                 num_drinks=round['drinks'], card_face=round['card'].face)
            for round in self.rounds
        ])
        rounds_df['round_id'] = rounds_df.index
        rounds_df['game_id'] = self.game_id
        return game_df, rounds_df


def simulate_games(num_games: int = 1000) -> Tuple[pd.DataFrame, pd.DataFrame]:
    games_df = pd.DataFrame()
    rounds_df = pd.DataFrame()

    for game_id in range(num_games):
        game = Game(players=[RandomizingAgent(x) for x in range(4)], seed=str(game_id))

        game_logger = PandasLogger(game=game, game_id=game_id)

        for _ in game.play():
            pass

        game_df, round_df = game_logger.to_df()
        games_df = games_df.append(game_df, ignore_index=True)
        rounds_df = rounds_df.append(round_df, ignore_index=True)

    return games_df.reset_index(drop=True), rounds_df.reset_index(drop=True)


def record_simulations(num_games: int = 10000, output_directory: Path = Path('.')):
    games_df, rounds_df = simulate_games(num_games=num_games)
    games_df.to_csv(output_directory / 'games.csv', index=False)
    rounds_df.to_csv(output_directory / 'rounds.csv', index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--games', type=int, default=1000, dest='num_games',
                        help='Number of games to simulate')
    parser.add_argument('-o', '--output-directory', type=Path, default=Path('.'), dest='output_directory',
                        help='Output directory for game log')

    args = vars(parser.parse_args())

    if not isinstance(args['output_directory'], Path):
        args['output_directory'] = Path(args['output_directory'])
    if args['num_games'] < 0:
        raise argparse.ArgumentError(message='Cannot simulate negative number of games!')

    record_simulations(num_games=args['num_games'], output_directory=args['output_directory'])