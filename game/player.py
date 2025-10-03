# maze_explorer/game/player.py
from dataclasses import dataclass

@dataclass
class Player: 
    gx: int
    gy: int
    direction: str = "down"  # "up", "down", "left", "right"
