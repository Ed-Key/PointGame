# hand_drawing_challenge/input/interfaces.py
from abc import ABC, abstractmethod
from typing import Any, Optional
import numpy as np

class InputProcessor(ABC):
    """Abstract base class for input processors."""
    
    @abstractmethod
    def process(self, *args: Any, **kwargs: Any) -> Optional[np.ndarray]:
        """Process input and emit relevant events.
        
        Args:
            *args: Variable positional arguments
            **kwargs: Variable keyword arguments
        """
        pass
    
    @abstractmethod
    def is_active(self) -> bool:
        """Check if processor is active and ready to process input.
        
        Returns:
            bool: True if processor is active, False otherwise
        """
        pass
        
    @abstractmethod
    def start(self) -> None:
        """Start the processor and initialize resources."""
        pass
        
    @abstractmethod
    def stop(self) -> None:
        """Stop the processor and release resources."""
        pass
        
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up processor resources."""
        pass
