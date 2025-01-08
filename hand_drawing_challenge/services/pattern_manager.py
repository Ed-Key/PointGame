# hand_drawing_challenge/services/pattern_manager.py

from typing import List, Optional, Tuple
from .patterns.models import Pattern, Point
from .patterns.generator import PatternGenerator
from .patterns.renderer import PatternRenderer
from ..events.bus import EventBus
from ..events.types import GameEventType
from ..events.events import PatternGeneratedEvent, PatternCompletedEvent

class PatternManager:
    """Service class that manages pattern generation, validation, and scoring."""
    
    def __init__(self, event_bus: EventBus):
        """Initialize the pattern manager.
        
        Args:
            event_bus: Event bus for communication
        """
        self._event_bus = event_bus
        self._generator = PatternGenerator()
        self._renderer = PatternRenderer()
        self._current_pattern: Optional[Pattern] = None
        self._current_difficulty = 1
    
    def initialize(self) -> None:
        """Initialize the pattern manager."""
        self._generator._initialize_basic_patterns()
    
    def get_next_pattern(self) -> Pattern:
        """Get the next pattern based on current difficulty."""
        patterns = self._generator.get_patterns_by_difficulty(self._current_difficulty)
        self._current_pattern = patterns[0] if patterns else self._generator.get_pattern("square")
        
        # Create and publish event
        event = PatternGeneratedEvent(pattern=self._current_pattern)
        self._event_bus.publish(GameEventType.PATTERN_GENERATED, event)
        
        return self._current_pattern
    
    def get_guide_points(self) -> List[Tuple[float, float]]:
        """Get guide points for the current pattern."""
        if self._current_pattern:
            return self._renderer.get_guide_points(self._current_pattern)
        return []
    
    def get_expected_path(self) -> List[Tuple[float, float]]:
        """Get expected path points for the current pattern."""
        if self._current_pattern:
            return self._renderer.get_expected_path(self._current_pattern)
        return []
    
    def validate_drawing(self, drawing_points: List[Tuple[float, float]]) -> float:
        """Validate a drawing against the current pattern.
        
        Args:
            drawing_points: List of points from user's drawing
            
        Returns:
            float: Score between 0 and 1
        """
        if not self._current_pattern or not drawing_points:
            return 0.0
            
        # TODO: Implement drawing validation logic
        # This would compare the drawing_points against the pattern's expected_path
        # and return a score based on how well they match
        
        score = 0.5  # Placeholder score
        
        # Create and publish event
        event = PatternCompletedEvent(
            pattern=self._current_pattern,
            score=score
        )
        self._event_bus.publish(GameEventType.PATTERN_COMPLETED, event)
        
        return score
    
    def increase_difficulty(self) -> None:
        """Increase the pattern difficulty."""
        self._current_difficulty = min(self._current_difficulty + 1, 3)
    
    def reset_difficulty(self) -> None:
        """Reset pattern difficulty to default."""
        self._current_difficulty = 1