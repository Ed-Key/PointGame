# hand_drawing_challenge/ui/components/pattern_display.py

import pygame
from typing import List, Optional, Tuple
from ..base import UIComponent
from ..utils.colors import Colors
from ...events.bus import EventBus
from ...events.events import PatternGeneratedEvent
from ...services.patterns.models import Pattern

class PatternDisplay(UIComponent):
    """Component for displaying the current pattern to be drawn."""
    
    def __init__(self, event_bus: EventBus, rect: pygame.Rect):
        """Initialize pattern display component.
        
        Args:
            event_bus: Event bus for component communication
            rect: Position and size of the display
        """
        super().__init__(event_bus, rect)
        self.current_pattern: Optional[Pattern] = None
        self.font = pygame.font.Font(None, 36)
        
        # Subscribe to pattern events
        self._event_bus.subscribe(PatternGeneratedEvent, self._on_pattern_generated)
    
    def _scale_pattern_points(self, points: List[Tuple[float, float]], padding: int = 40) -> List[Tuple[float, float]]:
        """Scale pattern points to fit within display area.
        
        Args:
            points: List of (x, y) coordinates to scale
            padding: Padding around the pattern in pixels
            
        Returns:
            List of scaled (x, y) coordinates
        """
        if not points:
            return []
            
        # Find pattern bounds
        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)
        
        # Calculate scaling
        pattern_width = max_x - min_x
        pattern_height = max_y - min_y
        
        available_width = self.rect.width - (2 * padding)
        available_height = self.rect.height - (2 * padding)
        scale_x = available_width / pattern_width if pattern_width > 0 else 1
        scale_y = available_height / pattern_height if pattern_height > 0 else 1
        scale = min(scale_x, scale_y)
        
        # Center the pattern
        center_x = self.rect.width / 2
        center_y = self.rect.height / 2
        pattern_center_x = (min_x + max_x) / 2
        pattern_center_y = (min_y + max_y) / 2
        
        # Scale and center all points
        scaled_points = []
        for x, y in points:
            new_x = center_x + (x - pattern_center_x) * scale
            new_y = center_y + (y - pattern_center_y) * scale
            scaled_points.append((new_x, new_y))
            
        return scaled_points

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the pattern display.
        
        Args:
            screen: Surface to draw on
        """
        if not self.visible:
            return
            
        # Draw background
        pygame.draw.rect(screen, Colors.COMPONENT_BG, self.rect)
        pygame.draw.rect(screen, Colors.BORDER, self.rect, 2)
        
        if self.current_pattern:
            # Draw pattern name
            name_text = self.font.render(f"Pattern: {self.current_pattern.name}", True, Colors.TEXT)
            name_rect = name_text.get_rect(midtop=(self.rect.x + self.rect.width // 2, self.rect.y + 10))
            screen.blit(name_text, name_rect)
            
            # Get and scale guide points
            # Convert Point objects to tuples for scaling
            guide_points = [(p.x, p.y) for p in self.current_pattern.guide_points]
            scaled_points = self._scale_pattern_points(guide_points)
            
            if scaled_points:
                # Draw guide lines
                pygame.draw.lines(screen, Colors.PATTERN, True, 
                               [(int(self.rect.x + p[0]), int(self.rect.y + p[1])) 
                                for p in scaled_points])
                
                # Draw guide points
                for point in scaled_points:
                    pygame.draw.circle(screen, Colors.TEXT,
                                    (int(self.rect.x + point[0]), 
                                     int(self.rect.y + point[1])), 5)
        else:
            # Draw "No Pattern" text
            text = self.font.render("No Pattern", True, Colors.TEXT)
            text_rect = text.get_rect(center=(self.rect.centerx, self.rect.centery))
            screen.blit(text, text_rect)

    def _on_pattern_generated(self, event: PatternGeneratedEvent) -> None:
        """Handle pattern generated events.
        
        Args:
            event: Pattern generated event containing new pattern
        """
        self.current_pattern = event.pattern

    def update(self, delta_time: float) -> None:
        """Update component state.
        
        Args:
            delta_time: Time elapsed since last update
        """
        # Pattern display currently has no time-based updates
        pass
