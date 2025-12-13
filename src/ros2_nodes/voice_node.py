"""
ROS 2 Voice Node for the VLA system.
This module provides a ROS 2 node that interfaces with the voice processing components
to handle voice commands in a ROS 2 environment.
"""
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSDurabilityPolicy
from std_msgs.msg import String, Header
from sensor_msgs.msg import AudioData
from geometry_msgs.msg import Point
import threading
import asyncio
import time
from typing import Optional
import numpy as np

from ..shared.utils.logging import get_logger
from ..shared.models.data_models import VoiceCommand
from ..vla.voice_interface.transcription_service import get_default_transcription_service
from ..vla.voice_interface.microphone_handler import get_microphone_input_handler, ContinuousVoiceCommandDetector
from ..config.config import get_config

# Set up logging
logger = get_logger(__name__)


class VoiceNode(Node):
    """
    ROS 2 node for handling voice commands and integration with the VLA system.
    """
    
    def __init__(self, node_name: str = 'vla_voice_node'):
        """
        Initialize the voice node.
        """
        super().__init__(node_name)
        
        # Get configuration
        self.config = get_config()
        self.sample_rate = self.config.get('VOICE.SAMPLE_RATE')
        
        # Initialize voice components
        self.transcription_service = get_default_transcription_service()
        self.microphone_handler = get_microphone_input_handler()
        self.voice_command_detector = ContinuousVoiceCommandDetector(self.microphone_handler)
        
        # Set up ROS 2 publishers
        qos_profile = QoSProfile(depth=10)
        self.voice_command_pub = self.create_publisher(String, 'voice_command', qos_profile)
        self.transcription_pub = self.create_publisher(String, 'transcription', qos_profile)
        self.audio_pub = self.create_publisher(AudioData, 'audio_raw', qos_profile)
        
        # Set up ROS 2 subscribers
        self.audio_sub = self.create_subscription(
            AudioData,
            'audio_input',
            self.audio_callback,
            qos_profile
        )
        
        # Set up voice command callback
        self.voice_command_detector.add_voice_command_callback(self.on_voice_command_detected)
        
        # State variables
        self.is_listening = False
        self.listening_thread = None
        
        logger.info("VoiceNode initialized")
    
    def start_voice_detection(self):
        """
        Start the continuous voice command detection.
        """
        if not self.is_listening:
            self.voice_command_detector.start_detection()
            self.is_listening = True
            logger.info("Started voice command detection")
    
    def stop_voice_detection(self):
        """
        Stop the continuous voice command detection.
        """
        if self.is_listening:
            self.voice_command_detector.stop_detection()
            self.is_listening = False
            logger.info("Stopped voice command detection")
    
    def audio_callback(self, msg: AudioData):
        """
        Callback for audio input from ROS 2 topic.
        
        Args:
            msg: AudioData message from ROS topic
        """
        try:
            # Convert ROS AudioData to numpy array
            # Assuming the audio data is in int16 format
            audio_np = np.frombuffer(msg.data, dtype=np.int16).astype(np.float32) / 32767.0
            
            # Convert to bytes for processing
            audio_bytes = audio_np.astype(np.float32).tobytes()
            
            # Process the audio for voice commands
            asyncio.create_task(self.process_audio_async(audio_bytes))
            
        except Exception as e:
            logger.error(f"Error in audio callback: {str(e)}")
    
    async def process_audio_async(self, audio_bytes: bytes):
        """
        Process audio asynchronously using the transcription service.
        
        Args:
            audio_bytes: Audio data in bytes
        """
        try:
            # Transcribe the audio
            result = await self.transcription_service.transcribe_audio_bytes(audio_bytes)
            
            if result.success and result.voice_command:
                # Publish transcription result
                transcription_msg = String()
                transcription_msg.data = result.voice_command.transcription
                self.transcription_pub.publish(transcription_msg)
                
                # Publish voice command with more details
                command_msg = String()
                command_msg.data = f"CMD_ID:{result.voice_command.id}|TEXT:{result.voice_command.transcription}|CONF:{result.voice_command.confidence}"
                self.voice_command_pub.publish(command_msg)
                
                logger.info(f"Published transcription: {result.voice_command.transcription}")
        except Exception as e:
            logger.error(f"Error processing audio asynchronously: {str(e)}")
    
    def on_voice_command_detected(self, audio_bytes: bytes):
        """
        Callback when a voice command is detected by the microphone handler.
        
        Args:
            audio_bytes: Audio data in bytes
        """
        try:
            # Publish raw audio
            audio_msg = AudioData()
            audio_msg.data = audio_bytes
            audio_msg.header = Header()
            audio_msg.header.stamp = self.get_clock().now().to_msg()
            self.audio_pub.publish(audio_msg)
            
            # Process the audio asynchronously
            asyncio.create_task(self.process_audio_async(audio_bytes))
            
        except Exception as e:
            logger.error(f"Error in voice command detected callback: {str(e)}")
    
    def transcribe_audio_file(self, filepath: str) -> Optional[str]:
        """
        Transcribe an audio file and return the text.
        
        Args:
            filepath: Path to the audio file
            
        Returns:
            Transcribed text or None if transcription failed
        """
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                self.transcription_service.transcribe_audio_file(filepath)
            )
            
            loop.close()
            
            if result.success and result.voice_command:
                return result.voice_command.transcription
            else:
                logger.error(f"Transcription failed: {result.error_message}")
                return None
        except Exception as e:
            logger.error(f"Error transcribing audio file: {str(e)}")
            return None


class VoiceNodeManager:
    """
    Manager for handling the ROS 2 voice node lifecycle.
    """
    
    def __init__(self):
        """
        Initialize the voice node manager.
        """
        self.node: Optional[VoiceNode] = None
        self.executor = None
        self.node_thread = None
        self.is_running = False
    
    def start_node(self, node_name: str = 'vla_voice_node'):
        """
        Start the voice node in a separate thread.
        
        Args:
            node_name: Name for the ROS 2 node
        """
        if self.is_running:
            logger.warning("Voice node is already running")
            return
        
        def run_ros_node():
            """
            Function to run the ROS 2 node in a separate thread.
            """
            try:
                # Initialize ROS 2
                rclpy.init()
                
                # Create the voice node
                self.node = VoiceNode(node_name)
                
                # Start voice detection
                self.node.start_voice_detection()
                
                # Create executor and add node
                self.executor = rclpy.executors.SingleThreadedExecutor()
                self.executor.add_node(self.node)
                
                logger.info(f"Voice node '{node_name}' started")
                
                # Spin the node
                while self.is_running:
                    self.executor.spin_once(timeout_sec=0.1)
                
                # Cleanup
                self.node.destroy_node()
                rclpy.shutdown()
                
            except Exception as e:
                logger.error(f"Error in ROS node thread: {str(e)}")
            finally:
                self.is_running = False
                logger.info("Voice node stopped")
        
        self.is_running = True
        self.node_thread = threading.Thread(target=run_ros_node, daemon=True)
        self.node_thread.start()
    
    def stop_node(self):
        """
        Stop the voice node.
        """
        if not self.is_running:
            logger.warning("Voice node is not running")
            return
        
        logger.info("Stopping voice node...")
        self.is_running = False
        
        if self.node_thread:
            self.node_thread.join(timeout=5.0)  # Wait up to 5 seconds for thread to finish
        
        logger.info("Voice node stopped")
    
    def is_node_active(self) -> bool:
        """
        Check if the voice node is currently active.
        
        Returns:
            True if the node is active, False otherwise
        """
        return self.is_running and self.node_thread and self.node_thread.is_alive()


def main(args=None):
    """
    Main function to run the voice node.
    This is the entry point for the ROS 2 voice node.
    """
    # Initialize ROS 2
    rclpy.init(args=args)
    
    # Create the voice node
    voice_node = VoiceNode()
    
    # Start voice detection
    voice_node.start_voice_detection()
    
    try:
        # Run the node
        rclpy.spin(voice_node)
    except KeyboardInterrupt:
        logger.info("Interrupt received, shutting down")
    finally:
        # Stop voice detection
        voice_node.stop_voice_detection()
        
        # Destroy the node
        voice_node.destroy_node()
        rclpy.shutdown()


# Global voice node manager instance
_voice_node_manager = None


def get_voice_node_manager() -> VoiceNodeManager:
    """
    Get the global voice node manager instance.
    
    Returns:
        VoiceNodeManager instance
    """
    global _voice_node_manager
    if _voice_node_manager is None:
        _voice_node_manager = VoiceNodeManager()
    return _voice_node_manager


def start_voice_node(node_name: str = 'vla_voice_node'):
    """
    Start the voice node using the global manager.
    
    Args:
        node_name: Name for the ROS 2 node
    """
    manager = get_voice_node_manager()
    manager.start_node(node_name)


def stop_voice_node():
    """
    Stop the voice node using the global manager.
    """
    manager = get_voice_node_manager()
    manager.stop_node()


if __name__ == '__main__':
    main()