from typing import Dict, List
import math
from .models import Point, Pattern

class PatternGenerator:
    def __init__(self):
        self.patterns: Dict[str, Pattern] = {}
        self._initialize_basic_patterns()
    
    def _initialize_basic_patterns(self):
        # Add square pattern
        self._add_square_pattern()
        # Add circle pattern
        self._add_circle_pattern()
        # Add triangle pattern
        self._add_triangle_pattern()
        # Add line pattern
        self._add_line_pattern()
    
    def _add_square_pattern(self):
        size = 100
        guide_points = [
            Point(0, 0),
            Point(size, 0),
            Point(size, size),
            Point(0, size)
        ]
        
        # Create more detailed path points for smooth drawing
        expected_path = []
        steps = 20  # Number of points per side
        for i in range(4):
            start = guide_points[i]
            end = guide_points[(i + 1) % 4]
            for step in range(steps):
                t = step / steps
                x = start.x + (end.x - start.x) * t
                y = start.y + (end.y - start.y) * t
                expected_path.append(Point(x, y))
        
        self.patterns["square"] = Pattern(
            name="square",
            difficulty=1,
            guide_points=guide_points,
            expected_path=expected_path
        )
    
    def _add_circle_pattern(self):
        radius = 50
        center = Point(50, 50)
        guide_points = []
        expected_path = []
        
        # Create circle points
        steps = 36  # Number of points around the circle
        for i in range(steps):
            angle = 2 * math.pi * i / steps
            x = center.x + radius * math.cos(angle)
            y = center.y + radius * math.sin(angle)
            point = Point(x, y)
            expected_path.append(point)
            if i % 9 == 0:  # Add guide points every 90 degrees
                guide_points.append(point)
        
        self.patterns["circle"] = Pattern(
            name="circle",
            difficulty=1,
            guide_points=guide_points,
            expected_path=expected_path
        )
    
    def _add_triangle_pattern(self):
        size = 100
        height = size * math.sqrt(3) / 2
        
        guide_points = [
            Point(size/2, 0),
            Point(size, height),
            Point(0, height)
        ]
        
        expected_path = []
        steps = 20
        for i in range(3):
            start = guide_points[i]
            end = guide_points[(i + 1) % 3]
            for step in range(steps):
                t = step / steps
                x = start.x + (end.x - start.x) * t
                y = start.y + (end.y - start.y) * t
                expected_path.append(Point(x, y))
        
        self.patterns["triangle"] = Pattern(
            name="triangle",
            difficulty=1,
            guide_points=guide_points,
            expected_path=expected_path
        )
    
    def _add_line_pattern(self):
        length = 100
        guide_points = [
            Point(0, 0),
            Point(length, 0)
        ]
        
        expected_path = []
        steps = 20
        for step in range(steps):
            t = step / steps
            x = t * length
            expected_path.append(Point(x, 0))
        
        self.patterns["line"] = Pattern(
            name="line",
            difficulty=1,
            guide_points=guide_points,
            expected_path=expected_path
        )
    
    def get_pattern(self, name: str) -> Pattern:
        return self.patterns.get(name)
    
    def get_patterns_by_difficulty(self, difficulty: int) -> List[Pattern]:
        return [p for p in self.patterns.values() if p.difficulty == difficulty]
