# game/managers/competitive_manager.py
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional
from .event_manager import EventManager, GameEvent

@dataclass
class PlayerState:
    """Enhanced player state tracking."""
    id: str  # Unique player identifier
    name: str
    score: int = 0
    completed: bool = False
    accuracy: float = 0.0
    turn_order: int = 0

class CompetitiveGameManager:
    """Centralized game state management for competitive mode."""
    def __init__(self):
        self.players: Dict[str, PlayerState] = {}
        self.current_turn_idx: int = -1  # Start at -1 so first next_turn() goes to 0
        self._turn_order: List[str] = []
        self.event_manager = EventManager()

    def add_player(self, name: str) -> str:
        """Add a new player to the game.
        
        Args:
            name: Player's display name
            
        Returns:
            str: Unique player ID
        """
        player_id = str(uuid.uuid4())
        self.players[player_id] = PlayerState(
            id=player_id,
            name=name,
            turn_order=len(self.players)
        )
        self._turn_order.append(player_id)
        return player_id
        
    def next_turn(self) -> Optional[str]:
        """Advance to the next player's turn.
        
        Returns:
            Optional[str]: ID of the next player or None if game is over
        """
        if not self._turn_order:
            return None
        
        self.current_turn_idx = (self.current_turn_idx + 1) % len(self._turn_order)
        next_player_id = self._turn_order[self.current_turn_idx]
        
        self.event_manager.emit(
            GameEvent.TURN_CHANGED,
            next_player_id,
            self.players[next_player_id].name
        )
        
        return next_player_id
    
    def get_current_player(self) -> Optional[str]:
        """Get the current player's ID.
        
        Returns:
            Optional[str]: Current player's ID or None if no game in progress
        """
        if not self._turn_order or self.current_turn_idx < 0:
            return None
        return self._turn_order[self.current_turn_idx]

    def update_player_score(self, player_id: str, score: int) -> None:
        """Update a player's score.
        
        Args:
            player_id: Player's unique ID
            score: New score value
        """
        if player_id in self.players:
            self.players[player_id].score = score
            self.event_manager.emit(
                GameEvent.PLAYER_SCORED,
                player_id,
                score
            )
    
    def get_player_count(self) -> int:
        """Get the number of players in the game.
        
        Returns:
            int: Number of players
        """
        return len(self.players)

    def get_player_turn_order(self) -> List[str]:
        """Get the list of player IDs in turn order.
        
        Returns:
            List[str]: Player IDs in turn order
        """
        return self._turn_order.copy()

    def mark_player_completed(self, player_id: str, accuracy: float = 0.0) -> None:
        """Mark a player's turn as completed.
        
        Args:
            player_id: Player's unique ID
            accuracy: Player's drawing accuracy
        """
        if player_id in self.players:
            self.players[player_id].completed = True
            self.players[player_id].accuracy = accuracy