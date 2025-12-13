"""
Microphone Input Handler for the VLA system.
This module handles low-level microphone input operations,
including audio capture, buffering, and real-time processing.
"""
import asyncio
import logging
import threading
import queue
from typing import Optional, Callable, Dict, Any
from datetime import datetime

from ...shared.utils.audio_utils import get_audio_processor
from ...shared.utils.logging import get_logger
from ...config.config import get_config

# Set up logging
logger = get_logger(__name__)


class MicrophoneInputHandler:
    """
    Handles microphone input operations including real-time capture,
    buffering, and event handling for voice commands.
    """
    
    def __init__(self):
        """
        Initialize the microphone input handler.
        """
        self.config = get_config()
        self.audio_processor = get_audio_processor()
        self.sample_rate = self.config.get('VOICE.SAMPLE_RATE')
        self.chunk_size = self.config.get('VOICE.CHUNK_SIZE')
        self.device_index = self.config.get('VOICE.AUDIO_DEVICE_INDEX')
        
        # Audio buffering
        self.audio_buffer = queue.Queue()
        self.is_recording = False
        self.recording_thread = None
        
        # Event callbacks
        self.on_audio_chunk_callbacks = []
        self.on_voice_detected_callbacks = []
        self.on_silence_detected_callbacks = []
        
        # Voice activity detection parameters
        self.energy_threshold = 0.01
        self.silence_duration_threshold = 1.0  # seconds
        self.last_voice_time = None
        
        logger.info("Microphone input handler initialized")
    
    def start_listening(self):
        """
        Start listening to the microphone input.
        """
        if self.is_recording:
            logger.warning("Microphone input is already being recorded")
            return
        
        def recording_loop():
            """Internal function to handle continuous recording."""
            try:
                # Open the audio stream
                stream = self.audio_processor.pyaudio_instance.open(
                    format=8,  # pyaudio.paInt16
                    channels=1,
                    rate=self.sample_rate,
                    input=True,
                    frames_per_buffer=self.chunk_size,
                    input_device_index=self.device_index
                )
                
                self.is_recording = True
                logger.info("Started microphone listening")
                
                while self.is_recording:
                    try:
                        # Read audio chunk
                        audio_chunk = stream.read(self.chunk_size, exception_on_overflow=False)
                        
                        # Add to internal buffer
                        self.audio_buffer.put(audio_chunk)
                        
                        # Process the audio chunk
                        self._process_audio_chunk(audio_chunk)
                        
                    except Exception as e:
                        logger.error(f"Error reading audio chunk: {str(e)}")
                        break
                
                # Close the stream
                stream.stop_stream()
                stream.close()
                
            except Exception as e:
                logger.error(f"Error in recording loop: {str(e)}")
            finally:
                self.is_recording = False
                logger.info("Microphone listening stopped")
        
        # Start the recording loop in a separate thread
        self.recording_thread = threading.Thread(target=recording_loop, daemon=True)
        self.recording_thread.start()
    
    def stop_listening(self):
        """
        Stop listening to the microphone input.
        """
        if not self.is_recording:
            logger.warning("Microphone input is not currently being recorded")
            return
        
        logger.info("Stopping microphone listening")
        self.is_recording = False
        
        if self.recording_thread:
            self.recording_thread.join(timeout=2.0)  # Wait up to 2 seconds for thread to finish
    
    def add_audio_chunk_callback(self, callback: Callable[[bytes], None]):
        """
        Add a callback function to be called when an audio chunk is received.
        
        Args:
            callback: Function to call with audio chunk data
        """
        if callback not in self.on_audio_chunk_callbacks:
            self.on_audio_chunk_callbacks.append(callback)
    
    def remove_audio_chunk_callback(self, callback: Callable[[bytes], None]):
        """
        Remove a callback function from the audio chunk callbacks.
        
        Args:
            callback: Function to remove
        """
        if callback in self.on_audio_chunk_callbacks:
            self.on_audio_chunk_callbacks.remove(callback)
    
    def add_voice_detected_callback(self, callback: Callable[[], None]):
        """
        Add a callback function to be called when voice is detected.
        
        Args:
            callback: Function to call when voice is detected
        """
        if callback not in self.on_voice_detected_callbacks:
            self.on_voice_detected_callbacks.append(callback)
    
    def add_silence_detected_callback(self, callback: Callable[[], None]):
        """
        Add a callback function to be called when silence is detected.
        
        Args:
            callback: Function to call when silence is detected
        """
        if callback not in self.on_silence_detected_callbacks:
            self.on_silence_detected_callbacks.append(callback)
    
    def _process_audio_chunk(self, audio_chunk: bytes):
        """
        Process an audio chunk for voice activity detection and trigger callbacks.
        
        Args:
            audio_chunk: Raw audio data in bytes
        """
        try:
            import numpy as np
            import soundfile as sf
            import io
            
            # Convert bytes to numpy array for processing
            audio_np, _ = sf.read(io.BytesIO(audio_chunk))
            
            # Calculate energy of the audio chunk
            energy = np.mean(audio_np ** 2)
            
            # Check for voice activity
            is_voice = energy > self.energy_threshold
            
            # Trigger audio chunk callbacks
            for callback in self.on_audio_chunk_callbacks:
                try:
                    callback(audio_chunk)
                except Exception as e:
                    logger.error(f"Error in audio chunk callback: {str(e)}")
            
            if is_voice:
                # Voice detected
                self.last_voice_time = datetime.now()
                
                # Trigger voice detected callbacks
                for callback in self.on_voice_detected_callbacks:
                    try:
                        callback()
                    except Exception as e:
                        logger.error(f"Error in voice detected callback: {str(e)}")
            else:
                # Check if it's been silent for longer than threshold
                if self.last_voice_time is not None:
                    silence_duration = (datetime.now() - self.last_voice_time).total_seconds()
                    
                    if silence_duration > self.silence_duration_threshold:
                        # Trigger silence detected callbacks
                        for callback in self.on_silence_detected_callbacks:
                            try:
                                callback()
                            except Exception as e:
                                logger.error(f"Error in silence detected callback: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error processing audio chunk: {str(e)}")
    
    def get_audio_chunk(self, timeout: float = 0.1) -> Optional[bytes]:
        """
        Get the next audio chunk from the buffer.
        
        Args:
            timeout: Maximum time to wait for an audio chunk (in seconds)
            
        Returns:
            Audio chunk in bytes, or None if timeout occurs
        """
        try:
            return self.audio_buffer.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_audio_chunks(self, max_chunks: int = 10, timeout: float = 0.1) -> list[bytes]:
        """
        Get multiple audio chunks from the buffer.
        
        Args:
            max_chunks: Maximum number of chunks to retrieve
            timeout: Maximum time to wait for each chunk (in seconds)
            
        Returns:
            List of audio chunks in bytes
        """
        chunks = []
        for _ in range(max_chunks):
            chunk = self.get_audio_chunk(timeout)
            if chunk is not None:
                chunks.append(chunk)
            else:
                break  # No more chunks available
        return chunks
    
    def is_speaking(self, lookback_duration: float = 0.5) -> bool:
        """
        Check if someone is currently speaking based on recent audio activity.
        
        Args:
            lookback_duration: How far back to look for voice activity (in seconds)
            
        Returns:
            True if voice activity was detected within the lookback duration
        """
        if self.last_voice_time is None:
            return False
        
        time_since_voice = (datetime.now() - self.last_voice_time).total_seconds()
        return time_since_voice < lookback_duration
    
    def calibrate_noise_level(self, duration: float = 2.0) -> float:
        """
        Calibrate the noise level by measuring ambient audio for a duration.
        
        Args:
            duration: Duration to measure ambient audio (in seconds)
            
        Returns:
            Estimated noise level (average energy)
        """
        logger.info(f"Calibrating noise level for {duration} seconds")
        
        import numpy as np
        import soundfile as sf
        import io
        
        # Record for the specified duration
        total_chunks = int(duration * self.sample_rate / self.chunk_size)
        energies = []
        
        for _ in range(total_chunks):
            try:
                audio_chunk = self.audio_processor.pyaudio_instance.read(
                    self.chunk_size, exception_on_overflow=False
                )
                
                # Convert to numpy array to calculate energy
                audio_np, _ = sf.read(io.BytesIO(audio_chunk))
                energy = np.mean(audio_np ** 2)
                energies.append(energy)
            except Exception as e:
                logger.error(f"Error during noise calibration: {str(e)}")
                break
        
        if energies:
            avg_noise_level = sum(energies) / len(energies)
            self.energy_threshold = avg_noise_level * 2  # Set threshold to twice the noise level
            logger.info(f"Noise calibration completed. Set energy threshold to {self.energy_threshold}")
            return avg_noise_level
        else:
            logger.warning("Noise calibration failed, no audio data collected")
            return self.energy_threshold / 2  # Default value
    
    def get_audio_level(self) -> float:
        """
        Get the current audio level (energy) from the microphone.
        
        Returns:
            Current audio energy level
        """
        try:
            import numpy as np
            import soundfile as sf
            import io
            
            # Get a single chunk to measure current level
            audio_chunk = self.audio_processor.pyaudio_instance.read(
                self.chunk_size, exception_on_overflow=False
            )
            
            # Convert to numpy array to calculate energy
            audio_np, _ = sf.read(io.BytesIO(audio_chunk))
            energy = np.mean(audio_np ** 2)
            
            return energy
        except Exception as e:
            logger.error(f"Error getting audio level: {str(e)}")
            return 0.0
    
    def get_device_info(self) -> Dict[str, Any]:
        """
        Get information about the current audio input device.
        
        Returns:
            Dictionary with device information
        """
        try:
            if self.device_index is not None:
                device_info = self.audio_processor.pyaudio_instance.get_device_info_by_index(self.device_index)
                return {
                    "index": self.device_index,
                    "name": device_info.get("name", "Unknown"),
                    "max_input_channels": device_info.get("maxInputChannels", 0),
                    "default_sample_rate": device_info.get("defaultSampleRate", 0),
                    "host_api": device_info.get("hostApi", 0)
                }
            else:
                return {"error": "No input device selected"}
        except Exception as e:
            logger.error(f"Error getting device info: {str(e)}")
            return {"error": str(e)}


class ContinuousVoiceCommandDetector:
    """
    A higher-level class that uses the MicrophoneInputHandler to detect
    and capture complete voice commands.
    """
    
    def __init__(self, input_handler: MicrophoneInputHandler):
        """
        Initialize the voice command detector.
        
        Args:
            input_handler: Instance of MicrophoneInputHandler
        """
        self.input_handler = input_handler
        self.is_detecting = False
        self.audio_capture_buffer = b""
        self.capture_in_progress = False
        self.on_voice_command_callbacks = []
        
        # Parameters for voice command detection
        self.silence_threshold = 1.0  # seconds of silence to consider command complete
        self.max_command_duration = 10.0  # maximum command duration
        self.min_command_duration = 0.5   # minimum command duration to be valid
        self.silence_start_time = None
    
    def start_detection(self):
        """
        Start detecting voice commands from the microphone input.
        """
        if self.is_detecting:
            logger.warning("Voice command detection is already active")
            return
        
        # Add callbacks to the input handler
        self.input_handler.add_voice_detected_callback(self._on_voice_detected)
        self.input_handler.add_silence_detected_callback(self._on_silence_detected)
        
        # Start the input handler
        self.input_handler.start_listening()
        self.is_detecting = True
        
        logger.info("Started voice command detection")
    
    def stop_detection(self):
        """
        Stop detecting voice commands.
        """
        if not self.is_detecting:
            logger.warning("Voice command detection is not active")
            return
        
        # Remove callbacks
        self.input_handler.remove_audio_chunk_callback(self._capture_audio_chunk)
        self.input_handler.add_voice_detected_callback(self._on_voice_detected)
        self.input_handler.add_silence_detected_callback(self._on_silence_detected)
        
        # Stop the input handler
        self.input_handler.stop_listening()
        self.is_detecting = False
        
        logger.info("Stopped voice command detection")
    
    def add_voice_command_callback(self, callback: Callable[[bytes], None]):
        """
        Add a callback function to be called when a complete voice command is detected.
        
        Args:
            callback: Function to call with the complete voice command audio data
        """
        if callback not in self.on_voice_command_callbacks:
            self.on_voice_command_callbacks.append(callback)
    
    def _on_voice_detected(self):
        """
        Callback when voice is detected.
        """
        if not self.capture_in_progress:
            # Start capturing a new voice command
            self._start_capture()
        else:
            # Reset the silence timer since we detected more voice
            self.silence_start_time = None
    
    def _on_silence_detected(self):
        """
        Callback when silence is detected.
        """
        if self.capture_in_progress:
            # Check if we just started timing silence
            if self.silence_start_time is None:
                self.silence_start_time = datetime.now()
            else:
                # Check if enough silence has passed to consider the command complete
                silence_duration = (datetime.now() - self.silence_start_time).total_seconds()
                if silence_duration >= self.silence_threshold:
                    self._complete_capture()
    
    def _start_capture(self):
        """
        Start capturing audio for a potential voice command.
        """
        self.capture_in_progress = True
        self.audio_capture_buffer = b""
        self.silence_start_time = None
        
        # Add chunk callback to capture audio
        self.input_handler.add_audio_chunk_callback(self._capture_audio_chunk)
        
        logger.debug("Started capturing voice command")
    
    def _capture_audio_chunk(self, audio_chunk: bytes):
        """
        Capture an audio chunk as part of a voice command.
        
        Args:
            audio_chunk: Audio chunk to add to the buffer
        """
        if self.capture_in_progress:
            self.audio_capture_buffer += audio_chunk
            
            # Check if command duration exceeds maximum
            current_duration = len(self.audio_capture_buffer) / (self.input_handler.sample_rate * 2)  # 2 bytes per sample for int16
            if current_duration >= self.max_command_duration:
                self._complete_capture()
    
    def _complete_capture(self):
        """
        Complete the current voice command capture and trigger callbacks.
        """
        if not self.capture_in_progress:
            return
        
        # Remove the chunk callback
        self.input_handler.remove_audio_chunk_callback(self._capture_audio_chunk)
        
        # Check if the captured audio is long enough to be a valid command
        duration = len(self.audio_capture_buffer) / (self.input_handler.sample_rate * 2)  # 2 bytes per sample for int16
        
        if duration < self.min_command_duration:
            logger.debug(f"Captured audio too short ({duration}s), discarding")
        else:
            logger.debug(f"Completed voice command capture ({duration}s)")
            
            # Trigger all voice command callbacks
            for callback in self.on_voice_command_callbacks:
                try:
                    callback(self.audio_capture_buffer)
                except Exception as e:
                    logger.error(f"Error in voice command callback: {str(e)}")
        
        # Reset for next command
        self.capture_in_progress = False
        self.audio_capture_buffer = b""
        self.silence_start_time = None


# Global microphone input handler instance
_microphone_input_handler = None


def get_microphone_input_handler() -> MicrophoneInputHandler:
    """
    Get the global microphone input handler instance.
    
    Returns:
        MicrophoneInputHandler instance
    """
    global _microphone_input_handler
    if _microphone_input_handler is None:
        _microphone_input_handler = MicrophoneInputHandler()
    return _microphone_input_handler