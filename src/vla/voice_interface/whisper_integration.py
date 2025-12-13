"""
Whisper Integration Module for the VLA system.
This module handles the integration with OpenAI's Whisper for speech-to-text conversion.
"""
import asyncio
import logging
import os
import tempfile
import threading
from typing import Optional, Dict, Any
from pathlib import Path

import torch
import whisper

from ..config.config import get_config
from ..utils.audio_utils import get_audio_processor, AudioProcessor
from ..models.data_models import VoiceCommand

# Set up logging
logger = logging.getLogger(__name__)


class WhisperIntegration:
    """
    Class for integrating with OpenAI's Whisper model for speech-to-text conversion.
    """
    
    def __init__(self):
        """
        Initialize the Whisper integration with configuration settings.
        """
        config = get_config()
        self.model_size = config.get('VOICE.WHISPER_MODEL')
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load the Whisper model
        self.model = None
        self.load_model()
    
    def load_model(self):
        """
        Load the Whisper model based on the configured model size.
        """
        try:
            logger.info(f"Loading Whisper model: {self.model_size} on {self.device}")
            
            # Check if model is already downloaded, otherwise it will be downloaded automatically
            self.model = whisper.load_model(self.model_size, device=self.device)
            
            logger.info(f"Whisper model {self.model_size} loaded successfully on {self.device}")
        except Exception as e:
            logger.error(f"Error loading Whisper model: {str(e)}")
            # Fallback to a smaller model if the configured one fails
            try:
                logger.info("Attempting to load a smaller model as fallback")
                self.model = whisper.load_model("base", device=self.device)
                logger.info("Fallback model loaded successfully")
            except Exception as fallback_error:
                logger.error(f"Fallback model also failed to load: {fallback_error}")
                raise
    
    async def transcribe_audio(self, audio_path: str, language: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Transcribe audio file using the Whisper model.
        
        Args:
            audio_path: Path to the audio file to transcribe
            language: Optional language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            Dictionary with transcription result, or None if transcription failed
        """
        if self.model is None:
            logger.error("Whisper model is not loaded")
            return None
        
        try:
            # Run transcription in a separate thread to prevent blocking the event loop
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                lambda: self.model.transcribe(
                    audio_path, 
                    language=language,
                    task="transcribe"
                )
            )
            
            logger.info(f"Audio transcribed successfully: {audio_path}")
            
            # The result contains 'text', 'segments', 'language', and other metadata
            return {
                "transcription": result["text"],
                "language": result.get("language", language or "unknown"),
                "confidence": self._estimate_confidence(result),
                "segments": result.get("segments", [])
            }
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return None
    
    async def transcribe_audio_bytes(self, audio_bytes: bytes, language: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Transcribe audio from bytes using the Whisper model.
        
        Args:
            audio_bytes: Audio data in bytes
            language: Optional language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            Dictionary with transcription result, or None if transcription failed
        """
        try:
            # Create a temporary file with the audio bytes
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name
            
            # Transcribe the temporary file
            result = await self.transcribe_audio(temp_path, language)
            
            # Clean up the temporary file
            os.unlink(temp_path)
            
            return result
        except Exception as e:
            logger.error(f"Error transcribing audio bytes: {str(e)}")
            return None
    
    def _estimate_confidence(self, result: Dict[str, Any]) -> float:
        """
        Estimate the confidence of the transcription.
        Whisper doesn't provide confidence scores directly, so we estimate based on
        the log probability and other metrics.
        
        Args:
            result: The transcription result from Whisper
            
        Returns:
            Estimated confidence score between 0 and 1
        """
        # Extract information from the result
        avg_logprob = result.get("avg_logprob", -1.0)
        
        # Convert log probability to a confidence score (rough estimation)
        # More positive logprob means higher confidence
        # Clamp the result between 0 and 1
        confidence = max(0.0, min(1.0, 1.0 + avg_logprob))
        
        return confidence
    
    async def transcribe_realtime_audio(self, audio_data: bytes, language: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Transcribe audio in near real-time.
        
        Args:
            audio_data: Audio data in bytes
            language: Optional language code
            
        Returns:
            Dictionary with transcription result
        """
        try:
            # For real-time transcription, we'll use a slightly different approach
            # First, save the audio to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            # Load audio with librosa which Whisper uses internally
            import librosa
            audio, sample_rate = librosa.load(temp_path, sr=16000)
            
            # Clean up the temp file
            os.unlink(temp_path)
            
            # Pad or trim audio to ensure consistency
            audio = whisper.pad_or_trim(audio)
            
            # Convert to mel spectrogram
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
            
            # Detect language if not provided
            if language is None:
                _, probs = self.model.detect_language(mel)
                language = max(probs, key=probs.get)
            
            # Encode audio
            audio_enc = self.model.encode(mel)
            
            # Decode to text
            result = self.model.decode(audio_enc, whisper.DecodingOptions(language=language))
            
            # Extract the text
            transcription = result.text
            
            logger.info("Real-time audio transcribed successfully")
            
            return {
                "transcription": transcription,
                "language": language,
                "confidence": 0.5,  # Placeholder since we can't easily get confidence from this method
                "segments": []
            }
            
        except Exception as e:
            logger.error(f"Error in real-time transcription: {str(e)}")
            return None


class WhisperTranscriptionService:
    """
    Service class that manages the transcription workflow from audio input to VoiceCommand object.
    """
    
    def __init__(self):
        """
        Initialize the transcription service.
        """
        self.whisper_integration = WhisperIntegration()
        self.audio_processor = get_audio_processor()
        self.config = get_config()
    
    async def process_voice_command(self, audio_data: bytes, 
                                   device_id: Optional[str] = None) -> Optional[VoiceCommand]:
        """
        Process a voice command by transcribing the audio and creating a VoiceCommand object.
        
        Args:
            audio_data: Audio data in bytes
            device_id: Optional ID of the device where the command originated
            
        Returns:
            VoiceCommand object with transcription, or None if processing failed
        """
        try:
            # Transcribe the audio
            transcription_result = await self.whisper_integration.transcribe_audio_bytes(audio_data)
            
            if transcription_result is None:
                logger.error("Failed to transcribe audio")
                return None
            
            # Create the VoiceCommand object
            import uuid
            from datetime import datetime
            
            voice_command = VoiceCommand(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                audioData=None,  # Not storing raw audio data to save space, but could save path to file
                transcription=transcription_result["transcription"],
                confidence=transcription_result["confidence"],
                intent="",  # This would be filled by the cognitive planning module
                rawAudioPath=None,  # Would be set if we store the audio file
                metadata={
                    "sourceDevice": device_id or "unknown",
                    "audioFormat": "wav",
                    "language": transcription_result["language"],
                    "noiseLevel": "unknown"  # Would be computed by audio preprocessing
                }
            )
            
            logger.info(f"Voice command processed successfully: {voice_command.id}")
            return voice_command
            
        except Exception as e:
            logger.error(f"Error processing voice command: {str(e)}")
            return None


# Global instance of the Whisper integration
_whisper_integration = None


def get_whisper_integration() -> WhisperIntegration:
    """
    Get the global Whisper integration instance.
    
    Returns:
        WhisperIntegration instance
    """
    global _whisper_integration
    if _whisper_integration is None:
        _whisper_integration = WhisperIntegration()
    return _whisper_integration


# Global instance of the transcription service
_transcription_service = None


def get_transcription_service() -> WhisperTranscriptionService:
    """
    Get the global transcription service instance.
    
    Returns:
        WhisperTranscriptionService instance
    """
    global _transcription_service
    if _transcription_service is None:
        _transcription_service = WhisperTranscriptionService()
    return _transcription_service