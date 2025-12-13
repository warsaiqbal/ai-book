"""
Main entry point for the Vision-Language-Action (VLA) system.
This module initializes and coordinates all components of the VLA system.
"""
import asyncio
import logging
import signal
import sys
from typing import Optional
import threading

from ..shared.utils.logging import setup_logging, get_logger
from ..shared.config.config import get_config
from .voice_interface.transcription_service import get_transcription_service_manager
from .voice_interface.microphone_handler import get_microphone_input_handler
from .voice_interface.speech_recognition import get_speech_recognition_interface
from ..shared.utils.state_manager import get_global_state_manager
from ..shared.utils.llm_client import get_llm_client
from ..shared.utils.audio_utils import get_audio_processor
from ..shared.utils.math_utils import (
    normalize_vector, quaternion_multiply, quaternion_to_euler,
    euler_to_quaternion, quaternion_rotate_vector, calculate_distance_3d,
    pose_to_transform_matrix, transform_pose, interpolate_poses, skew_symmetric_matrix
)


# Set up logging
logger = get_logger(__name__)


class VLASystem:
    """
    Main class for the Vision-Language-Action system.
    Orchestrates all components of the VLA system.
    """
    
    def __init__(self):
        """
        Initialize the VLA system.
        """
        logger.info("Initializing VLA System")
        
        # Get all system components
        self.config = get_config()
        self.state_manager = get_global_state_manager()
        self.llm_client = get_llm_client()
        self.audio_processor = get_audio_processor()
        self.transcription_service_manager = get_transcription_service_manager()
        self.microphone_input_handler = get_microphone_input_handler()
        self.speech_recognition_interface = get_speech_recognition_interface()
        
        # System state
        self.is_running = False
        self.main_loop = None
        self.shutdown_event = threading.Event()
        
        logger.info("VLA System initialized successfully")
    
    def start(self):
        """
        Start the VLA system.
        """
        logger.info("Starting VLA System")
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.is_running = True
        
        # Start audio input
        self.microphone_input_handler.start_listening()
        
        # Start speech recognition
        self.speech_recognition_interface.start_continuous_listening(
            self._on_voice_command_recognized
        )
        
        logger.info("VLA System started")
    
    def stop(self):
        """
        Stop the VLA system.
        """
        logger.info("Stopping VLA System")
        
        self.is_running = False
        self.shutdown_event.set()
        
        # Stop speech recognition
        self.speech_recognition_interface.stop_continuous_listening()
        
        # Stop audio input
        self.microphone_input_handler.stop_listening()
        
        logger.info("VLA System stopped")
    
    def _signal_handler(self, signum, frame):
        """
        Handle shutdown signals gracefully.
        """
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def _on_voice_command_recognized(self, voice_command):
        """
        Callback when a voice command is recognized.
        
        Args:
            voice_command: The recognized voice command
        """
        logger.info(f"Voice command recognized: {voice_command.transcription}")
        
        # Here we would typically pass the command to the cognitive planning module
        # For now, just log the command
        pass
    
    async def run(self):
        """
        Main run loop for the VLA system.
        """
        self.start()
        
        try:
            # Wait for shutdown event
            while self.is_running:
                await asyncio.sleep(0.1)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, shutting down...")
        finally:
            self.stop()


# Additional utility functions that could be part of the system


def run_vla_system():
    """
    Run the VLA system with all components initialized.
    """
    # Set up logging
    setup_logging("vla_system", level=logging.INFO)
    
    # Create and run the VLA system
    vla_system = VLASystem()
    
    # Run the system
    try:
        asyncio.run(vla_system.run())
    except Exception as e:
        logger.error(f"Error running VLA system: {str(e)}")
        return 1
    
    return 0


def test_math_utilities():
    """
    Test the math utilities to ensure they're working correctly.
    """
    import numpy as np
    
    logger.info("Testing math utilities...")
    
    # Test normalize_vector
    vec = [3, 4, 0]
    normalized = normalize_vector(vec)
    expected_magnitude = np.sqrt(normalized[0]**2 + normalized[1]**2 + normalized[2]**2)
    assert abs(expected_magnitude - 1.0) < 1e-6, f"Vector not normalized: {normalized}"
    
    # Test quaternion operations
    q1 = [0, 0, 0, 1]  # Identity quaternion
    q2 = [0, 0, 0, 1]
    result = quaternion_multiply(q1, q2)
    assert result == [0, 0, 0, 1], f"Quaternion multiplication failed: {result}"
    
    # Test euler to quaternion and back
    euler_angles = (0.1, 0.2, 0.3)
    quat = euler_to_quaternion(*euler_angles)
    euler_back = quaternion_to_euler(quat)
    
    # The conversion back should be close to the original (with some tolerance)
    assert abs(euler_angles[0] - euler_back[0]) < 0.001, "Euler to quaternion conversion issue"
    assert abs(euler_angles[1] - euler_back[1]) < 0.001, "Euler to quaternion conversion issue"
    assert abs(euler_angles[2] - euler_back[2]) < 0.001, "Euler to quaternion conversion issue"
    
    logger.info("Math utilities tests passed!")


if __name__ == "__main__":
    # If we want to run tests, we can call it here
    test_math_utilities()
    
    # Then run the main system
    exit_code = run_vla_system()
    sys.exit(exit_code)