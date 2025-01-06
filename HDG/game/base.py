from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum, auto

class GameStateType(Enum):
    """Enum defining different game states."""
    MENU = auto()
    PLAYING = auto()
    RESULTS = auto()
    PAUSED = auto()

@dataclass
class GameConfig:
    """Configuration for game settings.
    
    Attributes:
        difficulty (int): Current difficulty level
        max_time (int): Maximum time per round in seconds
        pattern_complexity (int): Complexity level for patterns
        required_accuracy (float): Minimum accuracy required to pass
    """
    difficulty: int = 1
    max_time: int = 60
    pattern_complexity: int = 1
    required_accuracy: float = 0.7

class GameState(ABC):
    """Abstract base class for game states."""
    
    def __init__(self):
        """Initialize the game state."""
        self.next_state: Optional[GameStateType] = None
    
    def on_enter(self) -> None:
        """Called when entering this state. Override to provide initialization logic."""
        pass
    
    def on_exit(self) -> None:
        """Called when exiting this state. Override to provide cleanup logic."""
        pass
    
    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Update the state.
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        pass
    
    @abstractmethod
    def draw(self) -> None:
        """Draw the current state."""
        pass
    
    @abstractmethod
    def handle_input(self, event: Any) -> None:
        """Handle input events.
        
        Args:
            event: Input event to process
        """
        pass
    
    def transition_to(self, state: GameStateType) -> None:
        """Request transition to a new state.
        
        Args:
            state: State to transition to
        """
        self.next_state = state

class GameMode(ABC):
    """Abstract base class for game modes."""
    
    def __init__(self, config: GameConfig):
        """Initialize the game mode.
        
        Args:
            config: Game configuration settings
        """
        self.config = config
        self.states: Dict[GameStateType, GameState] = {}
        self.current_state: Optional[GameState] = None
        self.score = 0
        self.is_active = False
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the game mode and its states."""
        pass
    
    def update(self, delta_time: float) -> None:
        """Update the current game state.
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        if self.current_state:
            self.current_state.update(delta_time)
            
            # Check for state transition
            if self.current_state.next_state:
                self.transition_to(self.current_state.next_state)
    
    def draw(self) -> None:
        """Draw the current game state."""
        if self.current_state:
            self.current_state.draw()
    
    def handle_input(self, event: Any) -> None:
        """Handle input events.
        
        Args:
            event: Input event to process
        """
        if self.current_state:
            self.current_state.handle_input(event)
    
    def transition_to(self, state_type: GameStateType) -> None:
        """Transition to a new game state.
        
        Args:
            state_type: Type of state to transition to
        """
        if state_type in self.states:
            # Call exit on current state if it exists
            if self.current_state:
                self.current_state.on_exit()
            
            # Set new state
            self.current_state = self.states[state_type]
            self.current_state.next_state = None
            
            # Call enter on new state
            self.current_state.on_enter()
    
    def start(self) -> None:
        """Start the game mode."""
        print("GameMode.start() called")  # Debug print
        self.is_active = True
        self.score = 0
        # self.transition_to(GameStateType.MENU)
        if self.current_state:
            print("Calling on_enter for current state")  
            self.current_state.on_enter()
    
    def stop(self) -> None:
        """Stop the game mode."""
        if self.current_state:
            self.current_state.on_exit()
        self.is_active = False
        self.current_state = None

class SinglePlayerMode(GameMode):
    """Implementation of single player game mode."""
    
    def initialize(self) -> None:
        """Initialize single player mode states."""
        # Implement single player specific initialization
        pass

class CompetitiveMode(GameMode):
    """Implementation of competitive game mode."""
    
    def initialize(self) -> None:
        """Initialize competitive mode states."""
        # Implement competitive specific initialization
        pass