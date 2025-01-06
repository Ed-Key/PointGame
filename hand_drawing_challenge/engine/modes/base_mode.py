# hand_drawing_challenge/engine/modes/base_mode.py
from abc import ABC, abstractmethod
from typing import Any, Optional
from ...events.bus import EventBus

class GameMode(ABC):
    """Base interface for game modes (single player, competitive, etc.)."""
    
    def __init__(self, event_bus: EventBus):
        """Initialize the game mode.
        
        Args:
            event_bus: Central event bus for communication
        """
        self.event_bus = event_bus
        self.is_active = False
        self.score = 0
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize mode-specific resources and state."""
        pass
    
    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Update game mode state.
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        pass
    
    @abstractmethod
    def handle_input(self, event: Any) -> None:
        """Handle input events.
        
        Args:
            event: Input event to process
        """
        pass
    
    def start(self) -> None:
        """Start the game mode."""
        self.is_active = True
        self.score = 0
    
    def stop(self) -> None:
        """Stop the game mode and cleanup resources."""
        self.is_active = False