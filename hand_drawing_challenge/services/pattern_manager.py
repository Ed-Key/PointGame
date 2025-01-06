# services/pattern_manager.py
from typing import List, Optional, Tuple
from .patterns.models import Pattern, Point
from .patterns.generator import PatternGenerator
from .patterns.renderer import PatternRenderer
from ..events.bus import EventBus
from ..events.events import PatternGeneratedEvent, PatternCompletedEvent
from ..events.types import GameEventType

class PatternManager:
    """
    Service class that manages pattern generation, validation, and scoring.
    Integrates with the event system to communicate pattern states.
    """
    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus
        self._generator = PatternGenerator()
        self._renderer = PatternRenderer()
        self._current_pattern: Optional[Pattern] = None
        self._current_difficulty = 1
    
    def initialize(self) -> None:
        """Initialize the pattern manager"""
        # Any initial setup, like loading patterns from files if needed
        pass
    
    def get_next_pattern(self) -> Pattern:
        """Get the next pattern based on current difficulty"""
        # Get patterns for current difficulty
        patterns = self._generator.get_patterns_by_difficulty(self._current_difficulty)
        if not patterns:
            # If no patterns found for difficulty, use square as fallback
            self._current_pattern = self._generator.get_pattern("square")
        else:
            # Use first pattern from the list
            self._current_pattern = patterns[0]
        
        # Notify system that a new pattern is ready
        self._event_bus.publish(PatternGeneratedEvent(type=GameEventType.PATTERN_GENERATED, pattern=self._current_pattern))
        return self._current_pattern
    
    def get_guide_points(self) -> List[Tuple[float, float]]:
        """Get guide points for the current pattern"""
        if self._current_pattern:
            return self._renderer.get_guide_points(self._current_pattern)
        return []
    
    def get_expected_path(self) -> List[Tuple[float, float]]:
        """Get expected path points for the current pattern"""
        if self._current_pattern:
            return self._renderer.get_expected_path(self._current_pattern)
        return []
    
    def validate_drawing(self, drawing_points: List[Tuple[float, float]]) -> float:
        """
        Validate a drawing against the current pattern
        Returns a score between 0 and 1
        """
        if not self._current_pattern or not drawing_points:
            return 0.0
            
        # TODO: Implement drawing validation logic
        # This would compare the drawing_points against the pattern's expected_path
        # and return a score based on how well they match
        
        score = 0.5  # Placeholder score
        
        # Notify system about pattern completion
        self._event_bus.publish(PatternCompletedEvent(self._current_pattern, score))
        return score
    
    def increase_difficulty(self) -> None:
        """Increase the pattern difficulty"""
        self._current_difficulty = min(self._current_difficulty + 1, 3)
    
    def reset_difficulty(self) -> None:
        """Reset pattern difficulty to default"""
        self._current_difficulty = 1
