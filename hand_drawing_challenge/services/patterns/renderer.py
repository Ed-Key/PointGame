from typing import List, Tuple
from .models import Pattern

class PatternRenderer:
    @staticmethod
    def get_guide_points(pattern: Pattern) -> List[Tuple[float, float]]:
        """Returns guide points for display"""
        return [(p.x, p.y) for p in pattern.guide_points]
    
    @staticmethod
    def get_expected_path(pattern: Pattern) -> List[Tuple[float, float]]:
        """Returns expected path points for display or comparison"""
        return [(p.x, p.y) for p in pattern.expected_path]