"""
Audio processing utilities specifically for the voice interface module.
This module provides functions for preprocessing audio before Whisper transcription.
"""
import logging
from typing import Optional, Dict
import numpy as np

from ...shared.utils.audio_utils import AudioProcessor, get_audio_processor
from ...config.config import get_config

# Set up logging
logger = logging.getLogger(__name__)


class VoiceAudioProcessor:
    """
    Specialized audio processor for voice commands with additional preprocessing
    steps specifically for speech recognition.
    """
    
    def __init__(self):
        """
        Initialize the voice-specific audio processor.
        """
        self.config = get_config()
        self.audio_processor = get_audio_processor()
        self.sample_rate = self.config.get('VOICE.SAMPLE_RATE')
    
    def preprocess_for_transcription(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Apply voice-specific preprocessing to audio data before transcription.
        
        Args:
            audio_data: Raw audio data as numpy array
            
        Returns:
            Preprocessed audio data ready for transcription
        """
        logger.debug("Starting voice-specific audio preprocessing")
        
        # First apply general preprocessing
        processed_audio = self.audio_processor.preprocess_audio(audio_data)
        
        # Apply voice activity detection to identify speech segments
        processed_audio = self._apply_voice_activity_filter(processed_audio)
        
        # Normalize the audio to optimal levels for Whisper
        processed_audio = self._normalize_audio_levels(processed_audio)
        
        # Apply high-pass filter to remove low-frequency noise (e.g., air conditioning)
        processed_audio = self._apply_high_pass_filter(processed_audio)
        
        # Apply noise reduction specifically for voice
        processed_audio = self.audio_processor.apply_noise_reduction(processed_audio)
        
        logger.debug("Voice-specific audio preprocessing completed")
        return processed_audio
    
    def _apply_voice_activity_filter(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Apply a simple voice activity detection to potentially mask non-speech segments.
        
        Args:
            audio_data: Input audio as numpy array
            
        Returns:
            Audio with potential voice activity filtering applied
        """
        # Calculate energy for short frames to detect voice activity
        frame_length = int(0.03 * self.sample_rate)  # 30ms frames
        frames = []
        
        for i in range(0, len(audio_data), frame_length):
            frame = audio_data[i:i+frame_length]
            energy = np.mean(frame ** 2)
            
            # If frame energy is above threshold, keep it; otherwise, attenuate
            if energy > 0.0001:  # This threshold may need adjustment based on testing
                frames.append(frame)
            else:
                # Attenuate non-speech frames by reducing their amplitude
                frames.append(frame * 0.1)  # Reduce to 10% of original amplitude
                # Note: Whisper is robust to silence, so we might just want to keep the audio as is
                # and let Whisper handle the processing
        
        # Recombine frames
        processed_audio = np.concatenate(frames) if frames else audio_data
        return processed_audio
    
    def _normalize_audio_levels(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Normalize the audio to optimal levels for Whisper transcription.
        
        Args:
            audio_data: Input audio as numpy array
            
        Returns:
            Normalized audio
        """
        # Calculate the target RMS (Root Mean Square) for optimal Whisper performance
        target_rms = 0.1  # This value may need adjustment based on testing
        
        # Calculate current RMS
        current_rms = np.sqrt(np.mean(audio_data ** 2))
        
        # Avoid division by zero
        if current_rms == 0:
            return audio_data
        
        # Calculate the gain needed to reach target RMS
        gain = target_rms / current_rms
        
        # Apply gain with a limit to avoid over-amplification
        gain = min(gain, 10.0)  # Maximum 10x amplification
        
        normalized_audio = audio_data * gain
        
        # Apply soft clipping to prevent harsh distortion
        normalized_audio = np.tanh(normalized_audio / 0.9) * 0.9
        
        return normalized_audio
    
    def _apply_high_pass_filter(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Apply high-pass filter to remove low-frequency noise.
        
        Args:
            audio_data: Input audio as numpy array
            
        Returns:
            Audio with high-pass filter applied
        """
        try:
            from scipy import signal
            
            # Define filter parameters
            low_freq_cutoff = 100  # Hz, cutoff frequency
            
            # Design Butterworth high-pass filter
            sos = signal.butter(10, low_freq_cutoff, 
                               btype='highpass', 
                               fs=self.sample_rate, 
                               output='sos')
            
            # Apply the filter
            filtered_audio = signal.sosfiltfilt(sos, audio_data)
            
            return filtered_audio
        except ImportError:
            logger.warning("scipy not available, skipping high-pass filter")
            return audio_data
        except Exception as e:
            logger.warning(f"Error applying high-pass filter: {str(e)}, returning original audio")
            return audio_data
    
    def detect_speech_quality(self, audio_data: np.ndarray) -> Dict[str, float]:
        """
        Analyze the quality of the speech audio to determine if it's suitable for transcription.
        
        Args:
            audio_data: Input audio as numpy array
            
        Returns:
            Dictionary with quality metrics
        """
        # Calculate various metrics
        rms = np.sqrt(np.mean(audio_data ** 2))
        peak_amplitude = np.max(np.abs(audio_data))
        duration = len(audio_data) / self.sample_rate
        
        # Simple SNR estimation (this is a very basic estimation)
        noise_floor = np.std(audio_data[audio_data < np.std(audio_data)])
        signal_level = np.mean(np.abs(audio_data))
        snr_approx = 20 * np.log10(signal_level / (noise_floor + 1e-10)) if noise_floor > 0 else 100
        
        return {
            "rms": rms,
            "peak_amplitude": peak_amplitude,
            "duration": duration,
            "snr_approx": snr_approx,
            "is_suitable": rms > 0.001 and duration > 0.1  # Basic thresholds
        }
    
    def preprocess_audio_file(self, filepath: str, output_path: Optional[str] = None) -> str:
        """
        Preprocess an audio file specifically for voice transcription.
        
        Args:
            filepath: Path to input audio file
            output_path: Optional path for preprocessed audio file. 
                        If None, creates a temporary file.
            
        Returns:
            Path to the preprocessed audio file
        """
        try:
            import tempfile
            import os
            
            # Load the audio file
            audio_data = self.audio_processor.load_audio_from_wav(filepath)
            
            # Apply preprocessing
            processed_audio = self.preprocess_for_transcription(audio_data)
            
            # Create output path if not provided
            if output_path is None:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                output_path = temp_file.name
                temp_file.close()
            
            # Save the processed audio
            self.audio_processor.save_audio_to_wav(processed_audio, output_path)
            
            logger.info(f"Audio file preprocessed: {filepath} -> {output_path}")
            
            return output_path
        except Exception as e:
            logger.error(f"Error preprocessing audio file: {str(e)}")
            raise


# Global instance of the voice audio processor
_voice_audio_processor = None


def get_voice_audio_processor() -> VoiceAudioProcessor:
    """
    Get the global voice audio processor instance.
    
    Returns:
        VoiceAudioProcessor instance
    """
    global _voice_audio_processor
    if _voice_audio_processor is None:
        _voice_audio_processor = VoiceAudioProcessor()
    return _voice_audio_processor