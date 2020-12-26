from dataclasses import dataclass
from enum import Enum
from typing import Dict, List

class Kind(Enum):
    NAME = 1  # client telling server its name
    END = 2   # client ending the connection
    INPUT = 3 # client giving an input
    GAME_STATE = 4 # server telling clients the game state


@dataclass
class GameState:
    players : Dict # (Name, (Loc, Color, Flag))
    game_map : List[List[int]] # Matrix representing the map 

@dataclass
class Packet:
    kind : Kind
    message : str=""
    state : GameState=None
    
