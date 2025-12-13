"""
Audio processing utilities for the VLA system.
This module provides functions for audio input/output, preprocessing, 
and interfacing with Whisper for voice recognition.
"""
import asyncio
import logging
import threading
import time
from typing import Optional, Tuple, Callable
import queue
import wave
import tempfile
import os

import numpy as np
import pyaudio
import librosa
import soundfile as sf
from pydub import AudioSegment
from scipy import signal

from ..config.config import get_config

# Set up logging
logger = logging.getLogger(__name__)


class AudioProcessor:
    """
    Audio processing class for handling microphone input, audio preprocessing,
    and integration with the Whisper ASR system.
    """
    
    def __init__(self):
        """
        Initialize the audio processor with configuration from the system config.
        """
        config = get_config()
        self.sample_rate = config.get('VOICE.SAMPLE_RATE')
        self.chunk_size = config.get('VOICE.CHUNK_SIZE')
        self.device_index = config.get('VOICE.AUDIO_DEVICE_INDEX')
        
        # Initialize PyAudio
        self.pyaudio_instance = pyaudio.PyAudio()
        
        # Audio input stream
        self.stream = None
        self.is_recording = False
        self.audio_queue = queue.Queue()
        
        # Setup audio input parameters
        self.setup_audio_input()
    
    def setup_audio_input(self):
        """
        Setup the audio input stream based on configuration.
        """
        try:
            # Check if the specified device index is valid
            if self.device_index is not None:
                device_info = self.pyaudio_instance.get_device_info_by_index(self.device_index)
                if device_info['maxInputChannels'] == 0:
                    logger.warning(f"Device at index {self.device_index} has no input channels, using default")
                    self.device_index = None
            
            # If no valid device index, find a suitable input device
            if self.device_index is None:
                for i in range(self.pyaudio_instance.get_device_count()):
                    device_info = self.pyaudio_instance.get_device_info_by_index(i)
                    if device_info['maxInputChannels'] > 0:
                        self.device_index = i
                        logger.info(f"Using audio input device: {device_info['name']}")
                        break
            
            if self.device_index is None:
                raise RuntimeError("No audio input devices found")
            
            logger.info(f"Audio input configured: sample_rate={self.sample_rate}, chunk_size={self.chunk_size}, device_index={self.device_index}")
            
        except Exception as e:
            logger.error(f"Error setting up audio input: {str(e)}")
            raise
    
    def start_recording(self, callback: Optional[Callable[[bytes], None]] = None):
        """
        Start recording audio from the microphone in a separate thread.
        
        Args:
            callback: Optional callback to process audio chunks
        """
        if self.is_recording:
            logger.warning("Recording is already in progress")
            return
        
        def recording_thread():
            """Internal function to handle audio recording."""
            try:
                self.stream = self.pyaudio_instance.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=self.sample_rate,
                    input=True,
                    frames_per_buffer=self.chunk_size,
                    input_device_index=self.device_index
                )
                
                self.is_recording = True
                logger.info("Started audio recording")
                
                while self.is_recording:
                    audio_data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                    
                    # Add to internal queue
                    self.audio_queue.put(audio_data)
                    
                    # Call external callback if provided
                    if callback:
                        try:
                            callback(audio_data)
                        except Exception as e:
                            logger.error(f"Error in recording callback: {str(e)}")
                
                logger.info("Audio recording stopped")
                
            except Exception as e:
                logger.error(f"Error in recording thread: {str(e)}")
                self.is_recording = False
            finally:
                if self.stream:
                    self.stream.stop_stream()
                    self.stream.close()
                    self.stream = None
        
        # Start recording in a separate thread
        self.recording_thread = threading.Thread(target=recording_thread, daemon=True)
        self.recording_thread.start()
    
    def stop_recording(self):
        """
        Stop the audio recording.
        """
        if not self.is_recording:
            logger.warning("Recording is not in progress")
            return
        
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
    
    def get_audio_chunk(self, timeout: float = 1.0) -> Optional[bytes]:
        """
        Get the next audio chunk from the queue.
        
        Args:
            timeout: Timeout in seconds to wait for audio data
            
        Returns:
            Audio data as bytes, or None if timeout occurs
        """
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def record_audio(self, duration: float) -> bytes:
        """
        Record audio for a specified duration.
        
        Args:
            duration: Duration in seconds to record
            
        Returns:
            Audio data as bytes
        """
        frames = []
        
        # Open stream directly for this recording
        stream = self.pyaudio_instance.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            input_device_index=self.device_index
        )
        
        logger.info(f"Recording audio for {duration} seconds")
        
        # Calculate number of chunks to record
        num_chunks = int(duration * self.sample_rate / self.chunk_size)
        
        for _ in range(num_chunks):
            data = stream.read(self.chunk_size, exception_on_overflow=False)
            frames.append(data)
        
        # Close the stream
        stream.stop_stream()
        stream.close()
        
        logger.info("Audio recording completed")
        
        # Combine all frames into a single byte string
        audio_data = b''.join(frames)
        return audio_data
    
    def save_audio_to_wav(self, audio_data: bytes, filepath: str):
        """
        Save audio data to a WAV file.
        
        Args:
            audio_data: Audio data in bytes
            filepath: Path to save the WAV file
        """
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Save as WAV file
            sf.write(filepath, audio_array, self.sample_rate)
            
            logger.info(f"Audio saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving audio to WAV: {str(e)}")
            raise
    
    def load_audio_from_wav(self, filepath: str) -> np.ndarray:
        """
        Load audio from a WAV file.
        
        Args:
            filepath: Path to the WAV file
            
        Returns:
            Audio data as numpy array
        """
        try:
            audio_data, _ = librosa.load(filepath, sr=self.sample_rate)
            logger.info(f"Audio loaded from {filepath}")
            return audio_data
        except Exception as e:
            logger.error(f"Error loading audio from WAV: {str(e)}")
            raise
    
    def preprocess_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Apply preprocessing to the audio data to improve ASR performance.
        
        Args:
            audio_data: Input audio data as numpy array
            
        Returns:
            Preprocessed audio data as numpy array
        """
        # Normalize audio to prevent clipping
        audio_data = audio_data / np.max(np.abs(audio_data)) if np.max(np.abs(audio_data)) != 0 else audio_data
        
        # Apply pre-emphasis filter (high-pass filter)
        # This amplifies higher frequencies which is helpful for speech recognition
        pre_emphasis = 0.97
        audio_data = np.append(audio_data[0], audio_data[1:] - pre_emphasis * audio_data[:-1])
        
        # Denoise using spectral gating
        # Compute STFT
        stft = librosa.stft(audio_data)
        magnitude = np.abs(stft)
        phase = np.angle(stft)
        
        # Estimate noise during silent periods (first and last 10% of audio)
        noise_start = magnitude[:, :int(0.1 * magnitude.shape[1])]
        noise_end = magnitude[:, -int(0.1 * magnitude.shape[1]):]
        noise_profile = np.mean(np.concatenate([noise_start, noise_end], axis=1), axis=1)
        
        # Apply spectral gating
        enhanced_magnitude = np.maximum(magnitude - noise_profile[:, np.newaxis], 0)
        
        # Reconstruct audio
        enhanced_stft = enhanced_magnitude * np.exp(1j * phase)
        audio_data = librosa.istft(enhanced_stft, length=len(audio_data))
        
        # Apply a final normalization
        audio_data = audio_data / np.max(np.abs(audio_data)) if np.max(np.abs(audio_data)) != 0 else audio_data
        
        logger.debug("Audio preprocessing completed")
        return audio_data
    
    def audio_to_wav_bytes(self, audio_data: np.ndarray) -> bytes:
        """
        Convert numpy audio array to WAV format bytes.
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Audio data in WAV format as bytes
        """
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_filename = temp_file.name
            
            # Save the audio to the temporary file
            sf.write(temp_filename, audio_data, self.sample_rate)
            
            # Read the file back as bytes
            with open(temp_filename, 'rb') as f:
                wav_bytes = f.read()
            
            # Clean up the temporary file
            os.unlink(temp_filename)
            
            return wav_bytes
        except Exception as e:
            logger.error(f"Error converting audio to WAV bytes: {str(e)}")
            raise
    
    def detect_silence(self, audio_data: np.ndarray, threshold: float = 0.01, 
                      min_silence_duration: float = 0.5) -> bool:
        """
        Detect if the audio contains significant silence.
        
        Args:
            audio_data: Audio data as numpy array
            threshold: Amplitude threshold below which is considered silence
            min_silence_duration: Minimum duration in seconds to consider it silence
            
        Returns:
            True if silence is detected, False otherwise
        """
        # Calculate the duration of the audio
        audio_duration = len(audio_data) / self.sample_rate
        
        # If audio is shorter than min_silence_duration, don't apply this check
        if audio_duration < min_silence_duration:
            # Just check if the average amplitude is below the threshold
            avg_amplitude = np.mean(np.abs(audio_data))
            return avg_amplitude < threshold
        
        # Calculate the number of samples that correspond to min_silence_duration
        min_samples = int(min_silence_duration * self.sample_rate)
        
        # Calculate amplitude for each chunk of min_samples size
        num_chunks = len(audio_data) // min_samples
        chunk_size = min_samples
        
        for i in range(num_chunks):
            start_idx = i * chunk_size
            end_idx = start_idx + chunk_size
            chunk = audio_data[start_idx:end_idx]
            
            avg_amplitude = np.mean(np.abs(chunk))
            if avg_amplitude > threshold:
                # Found a non-silent chunk
                return False
        
        # All chunks were below the threshold
        return True

    def apply_noise_reduction(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Apply noise reduction to the audio data.
        
        Args:
            audio_data: Input audio data as numpy array
            
        Returns:
            Noise-reduced audio data as numpy array
        """
        try:
            import noisereduce as nr
            
            # Apply noise reduction
            reduced_noise = nr.reduce_noise(y=audio_data, sr=self.sample_rate)
            logger.debug("Noise reduction applied")
            return reduced_noise
        except ImportError:
            logger.warning("noisereduce library not installed, skipping noise reduction")
            return audio_data
        except Exception as e:
            logger.warning(f"Error during noise reduction: {str(e)}, returning original audio")
            return audio_data
    
    def convert_audio_format(self, input_path: str, output_path: str, 
                           target_sample_rate: int = 16000, 
                           target_channels: int = 1) -> bool:
        """
        Convert audio file to a standard format suitable for Whisper.
        
        Args:
            input_path: Path to the input audio file
            output_path: Path to save the converted audio file
            target_sample_rate: Target sample rate
            target_channels: Target number of channels
            
        Returns:
            True if conversion was successful, False otherwise
        """
        try:
            # Load the audio file with librosa
            audio_data, original_sr = librosa.load(
                input_path, 
                sr=target_sample_rate, 
                mono=target_channels == 1
            )
            
            # Save the converted audio
            sf.write(output_path, audio_data, target_sample_rate)
            
            logger.info(f"Audio converted: {input_path} -> {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error converting audio format: {str(e)}")
            return False
    
    def __del__(self):
        """
        Cleanup PyAudio resources when the object is destroyed.
        """
        if hasattr(self, 'pyaudio_instance'):
            self.pyaudio_instance.terminate()


class AudioVAD:
    """
    Voice Activity Detection (VAD) class to detect when speech is occurring.
    """
    
    def __init__(self, sample_rate: int = 16000):
        """
        Initialize the VAD detector.
        
        Args:
            sample_rate: Sample rate of the audio
        """
        self.sample_rate = sample_rate
        self.energy_threshold = 0.01  # Adjust based on your environment
        self.frame_duration = 0.03  # 30ms frames
        self.frame_size = int(self.sample_rate * self.frame_duration)
    
    def is_speech(self, audio_data: np.ndarray, threshold_ratio: float = 1.5) -> bool:
        """
        Detect if speech is present in the audio data.
        
        Args:
            audio_data: Audio data as numpy array
            threshold_ratio: Multiplier for the energy threshold (higher = more sensitive)
            
        Returns:
            True if speech is detected, False otherwise
        """
        # Calculate energy of the audio
        energy = np.mean(audio_data ** 2)
        
        # Compare to threshold
        is_speech = energy > (self.energy_threshold * threshold_ratio)
        
        return is_speech


# Global audio processor instance
_audio_processor = None


def get_audio_processor() -> AudioProcessor:
    """
    Get the global audio processor instance.
    
    Returns:
        AudioProcessor instance
    """
    global _audio_processor
    if _audio_processor is None:
        _audio_processor = AudioProcessor()
    return _audio_processor