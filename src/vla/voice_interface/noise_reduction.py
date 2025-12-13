"""
Noise Reduction Filters for the VLA system.
This module provides various noise reduction techniques for audio preprocessing
before voice transcription.
"""
import logging
import numpy as np
from typing import Optional, Tuple
from scipy import signal
from scipy.fft import fft, ifft

from ...shared.utils.audio_utils import get_audio_processor
from ...config.config import get_config
from ...shared.utils.logging import get_logger

# Set up logging
logger = get_logger(__name__)


class NoiseReductionFilters:
    """
    Collection of noise reduction filters for audio preprocessing.
    """
    
    def __init__(self):
        """
        Initialize the noise reduction filters with configuration.
        """
        self.config = get_config()
        self.sample_rate = self.config.get('VOICE.SAMPLE_RATE')
        self.audio_processor = get_audio_processor()
        
        # Parameters for various noise reduction techniques
        self.spectral_gate_threshold = 0.01  # Adjust based on testing
        self.adaptive_filter_step_size = 0.01
        self.wiener_filter_noise_reduc_factor = 0.5
    
    def apply_spectral_gate(self, audio_data: np.ndarray, 
                           noise_percentile: float = 25.0) -> np.ndarray:
        """
        Apply spectral gating to reduce noise in the audio.
        
        Args:
            audio_data: Input audio as numpy array
            noise_percentile: Percentile of magnitude spectrum considered as noise
            
        Returns:
            Noise-reduced audio as numpy array
        """
        try:
            # Compute STFT
            stft = signal.stft(audio_data, fs=self.sample_rate, nperseg=1024)[2]
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Estimate noise profile based on the noise_percentile
            noise_threshold = np.percentile(magnitude, noise_percentile, axis=1, keepdims=True)
            
            # Apply spectral gating
            enhanced_magnitude = np.maximum(magnitude - noise_threshold * self.spectral_gate_threshold, 0)
            
            # Reconstruct audio
            enhanced_stft = enhanced_magnitude * np.exp(1j * phase)
            _, enhanced_audio = signal.istft(enhanced_stft, fs=self.sample_rate)
            
            # Ensure the output has the same length as the input
            if len(enhanced_audio) > len(audio_data):
                enhanced_audio = enhanced_audio[:len(audio_data)]
            elif len(enhanced_audio) < len(audio_data):
                # Pad with zeros if needed
                padding = len(audio_data) - len(enhanced_audio)
                enhanced_audio = np.pad(enhanced_audio, (0, padding), 'constant')
            
            logger.debug("Spectral gating applied successfully")
            return enhanced_audio
        except Exception as e:
            logger.error(f"Error applying spectral gate: {str(e)}")
            # Return original audio if processing fails
            return audio_data
    
    def apply_adaptive_filter(self, audio_data: np.ndarray, 
                             reference_noise: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Apply adaptive filtering to reduce noise using a reference noise signal.
        
        Args:
            audio_data: Input audio as numpy array
            reference_noise: Optional reference noise signal
            
        Returns:
            Noise-reduced audio as numpy array
        """
        try:
            if reference_noise is None:
                # If no reference signal is provided, create a simple estimation
                # by taking the beginning of the audio as reference noise
                # (assuming it contains mostly noise)
                reference_duration = min(len(audio_data)//10, 8000)  # 0.5 seconds at 16kHz
                reference_noise = audio_data[:reference_duration]
            
            # Create a simple adaptive filter using the LMS algorithm
            filter_length = 128
            weights = np.zeros(filter_length)
            
            output_signal = np.zeros_like(audio_data)
            reference_extended = np.concatenate([reference_noise, np.zeros(len(audio_data) - len(reference_noise))])
            
            for i in range(filter_length, len(audio_data)):
                # Get the reference samples for the filter
                ref_samples = reference_extended[i-filter_length:i][::-1]
                
                # Calculate filter output
                filtered_noise = np.dot(weights, ref_samples)
                
                # Calculate error (desired signal is the original audio)
                error = audio_data[i] - filtered_noise
                
                # Update filter weights using LMS algorithm
                weights += self.adaptive_filter_step_size * error * ref_samples
                
                # Output is the original signal minus the estimated noise
                output_signal[i] = error
            
            logger.debug("Adaptive filter applied successfully")
            return output_signal
        except Exception as e:
            logger.error(f"Error applying adaptive filter: {str(e)}")
            # Return original audio if processing fails
            return audio_data
    
    def apply_wiener_filter(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Apply Wiener filtering for noise reduction.
        
        Args:
            audio_data: Input audio as numpy array
            
        Returns:
            Noise-reduced audio as numpy array
        """
        try:
            # Compute FFT of the signal
            signal_fft = fft(audio_data)
            power_spectrum = np.abs(signal_fft) ** 2
            
            # Estimate noise power (simple estimation using minimum values)
            noise_power = np.mean(np.sort(power_spectrum)[:len(power_spectrum)//10])
            
            # Compute Wiener filter
            wiener_filter = power_spectrum / (power_spectrum + noise_power / self.wiener_filter_noise_reduc_factor)
            
            # Apply the filter in frequency domain
            filtered_fft = signal_fft * wiener_filter
            
            # Convert back to time domain
            filtered_audio = np.real(ifft(filtered_fft))
            
            logger.debug("Wiener filter applied successfully")
            return filtered_audio
        except Exception as e:
            logger.error(f"Error applying Wiener filter: {str(e)}")
            # Return original audio if processing fails
            return audio_data
    
    def apply_bandpass_filter(self, audio_data: np.ndarray, 
                             low_freq: float = 300.0, 
                             high_freq: float = 3400.0) -> np.ndarray:
        """
        Apply a bandpass filter to keep only the frequencies in the human speech range.
        
        Args:
            audio_data: Input audio as numpy array
            low_freq: Low frequency cutoff (Hz)
            high_freq: High frequency cutoff (Hz)
            
        Returns:
            Filtered audio as numpy array
        """
        try:
            # Normalize frequencies to Nyquist frequency
            low = low_freq / (self.sample_rate / 2)
            high = high_freq / (self.sample_rate / 2)
            
            if low >= 1.0 or high <= 0.0 or low >= high:
                logger.warning(f"Invalid frequency range for bandpass: low={low_freq}Hz, high={high_freq}Hz")
                return audio_data
            
            # Design Butterworth bandpass filter
            order = 6  # Filter order
            b, a = signal.butter(order, [low, high], btype='band', fs=self.sample_rate)
            
            # Apply the filter
            filtered_audio = signal.filtfilt(b, a, audio_data)
            
            logger.debug(f"Bandpass filter applied: {low_freq}Hz - {high_freq}Hz")
            return filtered_audio
        except Exception as e:
            logger.error(f"Error applying bandpass filter: {str(e)}")
            # Return original audio if processing fails
            return audio_data
    
    def apply_compressor(self, audio_data: np.ndarray, 
                        threshold: float = 0.5, 
                        ratio: float = 2.0) -> np.ndarray:
        """
        Apply dynamic range compression to normalize audio levels.
        
        Args:
            audio_data: Input audio as numpy array
            threshold: Threshold level for compression
            ratio: Compression ratio (3:1, 4:1, etc.)
            
        Returns:
            Compressed audio as numpy array
        """
        try:
            # Calculate envelope of the signal
            envelope = np.abs(signal.hilbert(audio_data))
            
            # Calculate gain reduction
            gain_reduction = np.zeros_like(envelope)
            above_threshold = envelope > threshold
            gain_reduction[above_threshold] = 1 - (1/ratio) * (1 - threshold/envelope[above_threshold])
            
            # Apply gain reduction
            compressed_audio = audio_data * (1 - gain_reduction)
            
            logger.debug("Dynamic range compression applied")
            return compressed_audio
        except Exception as e:
            logger.error(f"Error applying compressor: {str(e)}")
            # Return original audio if processing fails
            return audio_data
    
    def reduce_noise(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Apply a combination of noise reduction techniques for optimal results.
        
        Args:
            audio_data: Input audio as numpy array
            
        Returns:
            Noise-reduced audio as numpy array
        """
        logger.debug("Starting combined noise reduction")
        
        # Step 1: Apply bandpass filter to keep only speech frequencies
        audio = self.apply_bandpass_filter(audio_data)
        
        # Step 2: Apply spectral gating for non-stationary noise
        audio = self.apply_spectral_gate(audio)
        
        # Step 3: Apply Wiener filtering for stationary noise
        audio = self.apply_wiener_filter(audio)
        
        # Step 4: Apply compression to normalize levels
        audio = self.apply_compressor(audio)
        
        logger.debug("Combined noise reduction completed")
        return audio
    
    def estimate_noise_profile(self, audio_data: np.ndarray, 
                              silence_threshold: float = 0.01) -> np.ndarray:
        """
        Estimate the noise profile from the audio signal based on low-energy segments.
        
        Args:
            audio_data: Input audio as numpy array
            silence_threshold: Threshold below which audio is considered silent
            
        Returns:
            Estimated noise profile as numpy array
        """
        try:
            # Identify low-energy segments as noise
            energy = np.abs(audio_data)
            noise_mask = energy < silence_threshold
            
            if np.any(noise_mask):
                noise_profile = audio_data[noise_mask]
                logger.debug(f"Noise profile estimated from {np.sum(noise_mask)} samples")
                return noise_profile
            else:
                logger.warning("No low-energy segments found for noise estimation")
                return np.zeros(100)  # Return a small zero array as fallback
        except Exception as e:
            logger.error(f"Error estimating noise profile: {str(e)}")
            return np.zeros(100)
    
    def apply_denoise_with_profile(self, audio_data: np.ndarray, 
                                  noise_profile: np.ndarray) -> np.ndarray:
        """
        Apply denoising using a pre-estimated noise profile.
        
        Args:
            audio_data: Input audio as numpy array
            noise_profile: Pre-estimated noise profile
            
        Returns:
            Denoised audio as numpy array
        """
        try:
            # Use spectral subtraction approach
            # Compute FFT of both signals
            audio_fft = fft(audio_data)
            noise_fft = fft(np.pad(noise_profile, (0, len(audio_data) - len(noise_profile)), 'constant'))
            
            # Compute magnitude spectra
            audio_magnitude = np.abs(audio_fft)
            noise_magnitude = np.abs(noise_fft)
            
            # Estimate noise power spectrum
            noise_power = noise_magnitude ** 2
            audio_power = audio_magnitude ** 2
            
            # Apply spectral subtraction
            enhanced_power = np.maximum(audio_power - 0.5 * noise_power, 0)  # 0.5 is a suppression factor
            enhanced_magnitude = np.sqrt(enhanced_power)
            
            # Preserve original phase
            enhanced_fft = enhanced_magnitude * np.exp(1j * np.angle(audio_fft))
            
            # Convert back to time domain
            enhanced_audio = np.real(ifft(enhanced_fft))
            
            logger.debug("Denoising with profile applied")
            return enhanced_audio
        except Exception as e:
            logger.error(f"Error applying denoise with profile: {str(e)}")
            # Return original audio if processing fails
            return audio_data


class AdvancedNoiseReducer:
    """
    Advanced noise reduction using multiple techniques and machine learning approaches.
    This is a wrapper that combines the basic filters with more sophisticated approaches.
    """
    
    def __init__(self):
        """
        Initialize the advanced noise reducer.
        """
        self.basic_filters = NoiseReductionFilters()
        self.ml_model = None  # Placeholder for ML-based noise reduction
        
        # Try to load the ML model if available
        self._try_load_ml_model()
    
    def _try_load_ml_model(self):
        """
        Try to load an ML-based noise reduction model (e.g., RNNoise).
        """
        try:
            import rnnoise
            self.ml_model = rnnoise.RNNoise()
            logger.info("RNNoise model loaded successfully")
        except ImportError:
            logger.warning("RNNoise not available, using basic filters only")
        except Exception as e:
            logger.warning(f"Could not load RNNoise model: {str(e)}, using basic filters only")
    
    def reduce_noise_with_ml(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Apply noise reduction with ML-based techniques if available.
        
        Args:
            audio_data: Input audio as numpy array
            
        Returns:
            Noise-reduced audio as numpy array
        """
        if self.ml_model is not None:
            try:
                # Process audio in chunks to work with RNNoise
                chunk_size = 480  # RNNoise works with 10ms chunks at 48kHz
                # Resample to 48kHz if needed
                if self.basic_filters.sample_rate != 48000:
                    raise ValueError("RNNoise requires 48kHz audio")
                
                # Convert to frames for RNNoise
                frames = []
                for i in range(0, len(audio_data), chunk_size):
                    chunk = audio_data[i:i+chunk_size]
                    # Pad chunk if necessary
                    if len(chunk) < chunk_size:
                        chunk = np.pad(chunk, (0, chunk_size - len(chunk)), 'constant')
                    frames.append(chunk)
                
                # Process each frame
                processed_frames = []
                for frame in frames:
                    # Convert to int16 format for RNNoise
                    frame_int16 = (frame * 32767).astype(np.int16)
                    # Process with RNNoise
                    processed_frame = self.ml_model.process_frame(frame_int16.tobytes())
                    # Convert back to float
                    processed_frame_np = np.frombuffer(processed_frame, dtype=np.int16).astype(np.float32) / 32767.0
                    processed_frames.append(processed_frame_np)
                
                # Combine frames back into audio
                processed_audio = np.concatenate(processed_frames)
                
                # Trim to original length
                if len(processed_audio) > len(audio_data):
                    processed_audio = processed_audio[:len(audio_data)]
                
                logger.debug("ML-based noise reduction applied")
                return processed_audio
            except Exception as e:
                logger.warning(f"ML-based noise reduction failed: {str(e)}, falling back to basic filters")
        
        # Fall back to basic filters if ML processing fails
        return self.basic_filters.reduce_noise(audio_data)
    
    def reduce_noise(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Apply the best available noise reduction technique.
        
        Args:
            audio_data: Input audio as numpy array
            
        Returns:
            Noise-reduced audio as numpy array
        """
        return self.reduce_noise_with_ml(audio_data)


# Global noise reducer instance
_noise_reducer = None


def get_noise_reducer() -> AdvancedNoiseReducer:
    """
    Get the global noise reducer instance.
    
    Returns:
        AdvancedNoiseReducer instance
    """
    global _noise_reducer
    if _noise_reducer is None:
        _noise_reducer = AdvancedNoiseReducer()
    return _noise_reducer


def apply_noise_reduction(audio_data: np.ndarray) -> np.ndarray:
    """
    Apply noise reduction to audio data using the global noise reducer.
    
    Args:
        audio_data: Input audio as numpy array
        
    Returns:
        Noise-reduced audio as numpy array
    """
    reducer = get_noise_reducer()
    return reducer.reduce_noise(audio_data)