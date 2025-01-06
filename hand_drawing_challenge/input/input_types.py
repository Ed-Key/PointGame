# hand_drawing_challenge/input/input_types.py
from dataclasses import dataclass

@dataclass
class HandPoint:
    """Represents a point tracked by hand detection.
    
    Attributes:
        x: x-coordinate (0-1, normalized)
        y: y-coordinate (0-1, normalized)
        z: z-coordinate for depth (normalized)
    """
    x: float
    y: float
    z: float