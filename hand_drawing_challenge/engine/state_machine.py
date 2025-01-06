# hand_drawing_challenge/engine/state_machine.py
from enum import Enum, auto
from typing import Dict, Optional
from abc import ABC, abstractmethod

class GameState(Enum):
    """Available game states."""
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    RESULTS = auto()

class State(ABC):
    """Abstract base class for game states."""
    
    def __init__(self):
        """Initialize the state."""
        self.state_machine: Optional['GameStateMachine'] = None
    
    @abstractmethod
    def enter(self) -> None:
        """Called when entering this state."""
        pass
    
    @abstractmethod
    def exit(self) -> None:
        """Called when exiting this state."""
        pass
    
    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Update the state.
        
        Args:
            delta_time: Time elapsed since last update
        """
        pass

class GameStateMachine:
    """Manages game state transitions and updates."""
    
    def __init__(self):
        """Initialize the state machine."""
        self.states: Dict[GameState, State] = {}
        self.current_state: Optional[State] = None
        self.previous_state: Optional[State] = None
    
    def add_state(self, state_id: GameState, state: State) -> None:
        """Add a state to the machine.
        
        Args:
            state_id: Identifier for the state
            state: State instance to add
        """
        state.state_machine = self
        self.states[state_id] = state
    
    def change_state(self, new_state: GameState) -> None:
        """Change to a new state.
        
        Args:
            new_state: State to transition to
        """
        if new_state not in self.states:
            return
            
        if self.current_state:
            self.current_state.exit()
            self.previous_state = self.current_state
            
        self.current_state = self.states[new_state]
        self.current_state.enter()
    
    def update(self, delta_time: float) -> None:
        """Update the current state.
        
        Args:
            delta_time: Time elapsed since last update
        """
        if self.current_state:
            self.current_state.update(delta_time)