# ui/utils/colors.py

class Colors:
    """Color constants used throughout the UI."""
    
    # Basic colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    
    # UI specific colors
    BACKGROUND = BLACK
    BORDER = WHITE
    TEXT = WHITE
    COMPONENT_BG = (40, 40, 40)  # Dark gray for component backgrounds
    SUCCESS = GREEN
    PATTERN = (100, 100, 255)  # Light blue for pattern display
    
    # Drawing colors
    DRAWING_ACTIVE = GREEN  # Color when actively drawing
    DRAWING_INACTIVE = BLUE  # Color when hand detected but not drawing
    TRAIL_COLOR = WHITE  # Color of the drawing trail
