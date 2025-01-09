# hand_drawing_challenge/input/manager.py

import logging
from typing import Dict, Optional
import numpy as np
from ..events.bus import EventBus
from ..events.types import GameEventType
from .interfaces import InputProcessor
from .processors.hand_tracking import HandTrackingProcessor, HandProcessorConfig

class InputManager:
    """Manages and coordinates multiple input processors."""
    
    def __init__(self, event_bus: EventBus, camera_id: int = 0):
        """Initialize input manager."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Creating InputManager")
        
        self.event_bus = event_bus
        self.processors: Dict[str, InputProcessor] = {}
        self.is_processing = False
        self.current_frame: Optional[np.ndarray] = None
        self._started = False  # Track if already started
        
        # Initialize hand tracking
        self._init_hand_tracking(camera_id)
    
    def _init_hand_tracking(self, camera_id: int) -> None:
        """Initialize hand tracking processor."""
        try:
            self.logger.debug("Initializing HandTrackingProcessor")
            config = HandProcessorConfig(
                camera_width=640,
                camera_height=480,
                camera_id=camera_id,
                mirror_camera=True,
                draw_debug=True
            )
            
            self.hand_tracker = HandTrackingProcessor(
                event_bus=self.event_bus,
                config=config
            )
            
            self.register_processor("hand_tracking", self.hand_tracker)
            
        except Exception as e:
            self.logger.error(f"Failed to initialize hand tracking: {e}")
            raise
    
    def register_processor(self, name: str, processor: InputProcessor) -> None:
        """Register an input processor."""
        if name in self.processors:
            self.logger.debug(f"Replacing existing processor {name}")
            self.unregister_processor(name)
        
        self.logger.debug(f"Registering processor '{name}': {processor}")
        self.processors[name] = processor
        self.logger.info(f"Successfully registered processor {name}")
    
    def unregister_processor(self, name: str) -> None:
        """Remove an input processor."""
        if name in self.processors:
            processor = self.processors[name]
            self.logger.debug(f"Unregistering processor '{name}'")
            processor.stop()
            processor.cleanup()
            del self.processors[name]
    
    def get_processor(self, name: str) -> Optional[InputProcessor]:
        """Get a registered processor by name."""
        return self.processors.get(name)
    
    def start(self) -> None:
        """Start all registered processors."""
        if self._started:
            self.logger.debug("InputManager already started, ignoring start request")
            return
            
        self.logger.info("Starting input processing")
        try:
            for name, processor in self.processors.items():
                self.logger.debug(f"Starting processor {name}")
                processor.start()
                processor.enable_processing()
            
            self.is_processing = True
            self._started = True
            
        except Exception as e:
            self.logger.error(f"Error starting input processing: {e}")
            self.stop()
            raise
    
    def stop(self) -> None:
        """Stop all registered processors."""
        self.logger.info("Stopping input processing")
        self.is_processing = False
        self._started = False
        
        for name, processor in self.processors.items():
            try:
                self.logger.debug(f"Stopping processor {name}")
                processor.disable_processing()
                processor.stop()
            except Exception as e:
                self.logger.error(f"Error stopping processor {name}: {e}")
    
    def process_input(self) -> None:
        """Process input from all active processors."""
        if not self.is_processing:
            return
            
        try:
            for name, processor in self.processors.items():
                if processor.is_active():
                    frame_result = processor.process()
                    if frame_result is not None:
                        self.current_frame = frame_result
                        
        except Exception as e:
            self.logger.error(f"Error processing input: {e}")
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Get the most recent camera frame."""
        return self.current_frame
    
    def cleanup(self) -> None:
        """Clean up all processors."""
        self.logger.info("Cleaning up input manager")
        
        # First stop processing
        self.is_processing = False
        self._started = False
        
        # Then clean up processors
        for name in list(self.processors.keys()):
            try:
                self.unregister_processor(name)
            except Exception as e:
                self.logger.error(f"Error cleaning up processor {name}: {e}")
        
        # Finally clear event bus reference
        self.event_bus = None
