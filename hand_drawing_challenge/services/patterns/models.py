from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Point:
    x: float
    y: float

@dataclass
class Pattern:
    name: str
    difficulty: int
    guide_points: List[Point]
    expected_path: List[Point]
    tolerance: float = 0.2
    size: Tuple[float, float] = (100, 100)