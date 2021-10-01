from dataclasses import dataclass
from typing import List, Dict

from card import Card


@dataclass
class Observation:
    players: List['Agent']
    dealer: 'Agent'
    cards_remaining: Dict[Card, int]