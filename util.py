from typing import Optional, Tuple
from random import Random
import random

def generate_random_string(length: int = 8, generator: Optional[Random] = None) -> str:
    generator = generator if generator is not None else random
    return "".join([chr(generator.randint(ord('A'), ord('Z'))) for _ in range(8)])

def get_generator(generator: Optional[Random] = None, seed: Optional[str] = None) -> Tuple[Random, str]:
    if generator is not None:
        assert seed is None
    else:
        if seed is None:
            seed = generate_random_string()
        generator = Random(seed)
    return generator, seed