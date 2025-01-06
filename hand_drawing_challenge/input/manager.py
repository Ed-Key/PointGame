# hand_drawing_challenge/input/manager.py
from typing import Dict, Optional
import numpy as np
from ..events.bus import EventBus
from ..events.types import GameEventType
from .interfaces import InputProcessor

class InputManager:
    """Manages and coordinates multiple input processors."""
    
    def __init__(self, event_bus: EventBus, camera_id: int = 0):
        """Initialize input manager.
        
        Args:
            event_bus: Event bus for publishing events
        """
        self.event_bus = event_bus
        self.processors: Dict[str, InputProcessor] = {}
        self.is_processing = False
        self.camera_id = camera_id
        self.current_frame = None
        
        # Subscribe to game events
        self.event_bus.subscribe(GameEventType.GAME_ENDED, self._handle_game_end)
    
    def register_processor(self, name: str, processor: InputProcessor) -> None:
        """Register an input processor.
        
        Args:
            name: Unique identifier for the processor
            processor: Input processor instance
        """
        if name in self.processors:
            # Clean up existing processor if being replaced
            self.unregister_processor(name)
            
        self.processors[name] = processor
        
    def unregister_processor(self, name: str) -> None:
        """Remove an input processor.
        
        Args:
            name: Name of processor to remove
        """
        if name in self.processors:
            processor = self.processors[name]
            processor.cleanup()
            del self.processors[name]
    
    def get_processor(self, name: str) -> Optional[InputProcessor]:
        """Get a registered processor by name.
        
        Args:
            name: Name of processor to retrieve
            
        Returns:
            InputProcessor if found, None otherwise
        """
        return self.processors.get(name)
    
    def start(self) -> None:
        """Start all registered processors."""
        for processor in self.processors.values():
            processor.start()

    def stop(self) -> None:
        """Stop all registered processors."""
        for processor in self.processors.values():
            processor.stop()
        self.cleanup()

    def get_frame(self) -> Optional[np.ndarray]:
        """Get the most recent camera frame.
        
        Returns:
            np.ndarray or None: Current camera frame if available
        """
        return self.current_frame

    def process_input(self) -> None:
        """Process input from all active processors."""
        if self.is_processing:
            return  # Prevent recursive processing
            
        try:
            self.is_processing = True
            for processor in self.processors.values():
                if processor.is_active():
                    try:
                        result = processor.process()
                        if result is not None:
                            self.current_frame = result
                    except Exception as e:
                        print(f"Error in processor: {e}")
                        # Optionally emit error event
                        self.event_bus.publish(
                            GameEventType.INPUT_ERROR,
                            {"error": str(e)}
                        )
        finally:
            self.is_processing = False
    
    def cleanup(self) -> None:
        """Clean up all processors."""
        for name in list(self.processors.keys()):
            self.unregister_processor(name)
    
    def _handle_game_end(self, event_type: GameEventType, data: Optional[dict] = None) -> None:
        """Handle game end event by cleaning up processors."""
        self.cleanup()
