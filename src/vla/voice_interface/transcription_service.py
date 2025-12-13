"""
Whisper Transcription Service for the VLA system.
This module provides a complete service for handling voice transcription
using OpenAI's Whisper model with additional processing and validation.
"""
import asyncio
import logging
import time
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
import tempfile
import os

from ...shared.models.data_models import VoiceCommand
from ...shared.utils.logging import get_logger
from ...shared.utils.audio_utils import get_audio_processor
from ...config.config import get_config
from .whisper_integration import get_whisper_integration
from .audio_processing import get_voice_audio_processor
from .models import EnhancedVoiceCommand, VoiceCommandResult, VoiceProcessingPipelineConfig


# Set up logging
logger = get_logger(__name__)


class WhisperTranscriptionService:
    """
    Complete service for handling voice transcription using Whisper.
    Manages the entire pipeline from audio input to processed VoiceCommand.
    """
    
    def __init__(self, config: Optional[VoiceProcessingPipelineConfig] = None):
        """
        Initialize the Whisper transcription service.
        
        Args:
            config: Optional configuration for the service
        """
        self.config = config or VoiceProcessingPipelineConfig()
        self.whisper_integration = get_whisper_integration()
        self.audio_processor = get_audio_processor()
        self.voice_audio_processor = get_voice_audio_processor()
        self.active_transcriptions = {}  # Track active transcription tasks
        
        logger.info("Whisper Transcription Service initialized")
    
    async def transcribe_audio_bytes(self, audio_data: bytes, 
                                   device_id: Optional[str] = None,
                                   language: Optional[str] = None) -> VoiceCommandResult:
        """
        Transcribe audio from bytes using Whisper.
        
        Args:
            audio_data: Audio data in bytes
            device_id: Optional ID of the device where the command originated
            language: Optional language for transcription
            
        Returns:
            VoiceCommandResult with transcription result
        """
        start_time = time.time()
        
        try:
            # Preprocess the audio
            import io
            import soundfile as sf
            import numpy as np
            
            # Load the audio from bytes
            audio_np, sr = sf.read(io.BytesIO(audio_data))
            
            # Preprocess the audio specifically for voice recognition
            preprocessed_audio = self.voice_audio_processor.preprocess_for_transcription(audio_np)
            
            # Convert back to bytes for Whisper processing
            processed_bytes = self.audio_processor.audio_to_wav_bytes(preprocessed_audio)
            
            # Check audio quality before transcription
            quality_metrics = self.voice_audio_processor.detect_speech_quality(audio_np)
            if not quality_metrics.get("is_suitable", False):
                logger.warning("Audio quality is not suitable for transcription")
                return VoiceCommandResult(
                    success=False,
                    error_message="Audio quality not suitable for transcription",
                    confidence_score=quality_metrics.get("snr_approx", 0.0)
                )
            
            # Perform transcription
            transcription_result = await self.whisper_integration.transcribe_audio_bytes(
                processed_bytes, 
                language=language
            )
            
            if transcription_result is None:
                logger.error("Whisper transcription failed")
                return VoiceCommandResult(
                    success=False,
                    error_message="Whisper transcription failed"
                )
            
            # Create EnhancedVoiceCommand
            voice_command = EnhancedVoiceCommand(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                audioData=None,  # Not storing raw audio to save space
                transcription=transcription_result["transcription"],
                confidence=transcription_result["confidence"],
                intent="",  # To be filled by cognitive planning
                rawAudioPath=None,
                metadata={
                    "sourceDevice": device_id or "unknown",
                    "audioFormat": "wav",
                    "language": transcription_result["language"],
                    "noiseLevel": "unknown",
                    "processing_pipeline": "whisper"
                },
                audio_quality_score=quality_metrics.get("snr_approx", 0.5)
            )
            
            # Set voice activity information
            voice_command.set_voice_activity(audio_data)
            
            processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Update processing time in the voice command
            voice_command.processing_time_ms = processing_time
            
            logger.info(f"Successfully transcribed voice command: {voice_command.transcription[:50]}...")
            
            return VoiceCommandResult(
                success=True,
                voice_command=voice_command,
                processing_time_ms=processing_time,
                confidence_score=transcription_result["confidence"]
            )
            
        except Exception as e:
            logger.error(f"Error in transcribe_audio_bytes: {str(e)}")
            return VoiceCommandResult(
                success=False,
                error_message=f"Error during transcription: {str(e)}"
            )
    
    async def transcribe_audio_file(self, filepath: str, 
                                  device_id: Optional[str] = None,
                                  language: Optional[str] = None) -> VoiceCommandResult:
        """
        Transcribe audio from a file using Whisper.
        
        Args:
            filepath: Path to the audio file
            device_id: Optional ID of the device where the command originated
            language: Optional language for transcription
            
        Returns:
            VoiceCommandResult with transcription result
        """
        start_time = time.time()
        
        try:
            # Preprocess the audio file
            preprocessed_path = self.voice_audio_processor.preprocess_audio_file(filepath)
            
            # Perform transcription
            transcription_result = await self.whisper_integration.transcribe_audio(
                preprocessed_path, 
                language=language
            )
            
            # Clean up temporary file if it was created
            original_filename = os.path.basename(filepath)
            processed_filename = os.path.basename(preprocessed_path)
            if original_filename != processed_filename:
                try:
                    os.unlink(preprocessed_path)
                except OSError:
                    pass  # File might already be deleted
            
            if transcription_result is None:
                logger.error("Whisper transcription failed")
                return VoiceCommandResult(
                    success=False,
                    error_message="Whisper transcription failed"
                )
            
            # Load original audio to analyze voice activity
            import soundfile as sf
            original_audio, _ = sf.read(filepath)
            original_audio_bytes = self.audio_processor.audio_to_wav_bytes(original_audio)
            
            # Create EnhancedVoiceCommand
            voice_command = EnhancedVoiceCommand(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                audioData=None,
                transcription=transcription_result["transcription"],
                confidence=transcription_result["confidence"],
                intent="",  # To be filled by cognitive planning
                rawAudioPath=filepath,
                metadata={
                    "sourceDevice": device_id or "file_input",
                    "audioFormat": "wav",
                    "language": transcription_result["language"],
                    "noiseLevel": "unknown",
                    "processing_pipeline": "whisper"
                }
            )
            
            # Set voice activity information
            voice_command.set_voice_activity(original_audio_bytes)
            
            processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Update processing time in the voice command
            voice_command.processing_time_ms = processing_time
            
            logger.info(f"Successfully transcribed voice command from file: {voice_command.transcription[:50]}...")
            
            return VoiceCommandResult(
                success=True,
                voice_command=voice_command,
                processing_time_ms=processing_time,
                confidence_score=transcription_result["confidence"]
            )
            
        except Exception as e:
            logger.error(f"Error in transcribe_audio_file: {str(e)}")
            return VoiceCommandResult(
                success=False,
                error_message=f"Error during transcription: {str(e)}"
            )
    
    async def transcribe_microphone(self, duration: float = 5.0, 
                                  device_id: Optional[str] = None,
                                  language: Optional[str] = None) -> VoiceCommandResult:
        """
        Record audio from microphone and transcribe using Whisper.
        
        Args:
            duration: Duration to record audio (in seconds)
            device_id: Optional ID of the audio device
            language: Optional language for transcription
            
        Returns:
            VoiceCommandResult with transcription result
        """
        start_time = time.time()
        
        try:
            logger.info(f"Recording audio from microphone for {duration} seconds")
            
            # Record audio from microphone
            audio_data_bytes = self.audio_processor.record_audio(duration)
            
            # Transcribe the recorded audio
            result = await self.transcribe_audio_bytes(
                audio_data_bytes, 
                device_id=device_id, 
                language=language
            )
            
            # Update processing time to include recording time
            total_processing_time = (time.time() - start_time) * 1000
            if result.voice_command:
                result.voice_command.processing_time_ms = total_processing_time
            
            return result
            
        except Exception as e:
            logger.error(f"Error in transcribe_microphone: {str(e)}")
            return VoiceCommandResult(
                success=False,
                error_message=f"Error during microphone transcription: {str(e)}"
            )
    
    async def batch_transcribe(self, audio_data_list: List[bytes], 
                             device_ids: Optional[List[str]] = None,
                             language: Optional[str] = None) -> List[VoiceCommandResult]:
        """
        Transcribe multiple audio data in parallel.
        
        Args:
            audio_data_list: List of audio data in bytes
            device_ids: Optional list of device IDs for each audio
            language: Optional language for transcription
            
        Returns:
            List of VoiceCommandResult for each audio
        """
        logger.info(f"Starting batch transcription for {len(audio_data_list)} audio clips")
        
        # Create transcription tasks
        tasks = []
        for i, audio_data in enumerate(audio_data_list):
            device_id = device_ids[i] if device_ids and i < len(device_ids) else None
            task = self.transcribe_audio_bytes(audio_data, device_id=device_id, language=language)
            tasks.append(task)
        
        # Execute tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error in batch transcription for item {i}: {str(result)}")
                processed_results.append(VoiceCommandResult(
                    success=False,
                    error_message=f"Error in batch transcription: {str(result)}"
                ))
            else:
                processed_results.append(result)
        
        logger.info("Batch transcription completed")
        return processed_results
    
    async def transcribe_with_fallback(self, audio_data: bytes,
                                     primary_language: Optional[str] = None,
                                     fallback_languages: Optional[List[str]] = None,
                                     device_id: Optional[str] = None) -> VoiceCommandResult:
        """
        Transcribe audio with fallback languages if the primary language fails.
        
        Args:
            audio_data: Audio data in bytes
            primary_language: Primary language for transcription
            fallback_languages: List of fallback languages to try
            device_id: Optional ID of the device where the command originated
            
        Returns:
            VoiceCommandResult with transcription result
        """
        languages_to_try = [primary_language]
        
        if fallback_languages:
            languages_to_try.extend(fallback_languages)
        
        for lang in languages_to_try:
            try:
                logger.info(f"Attempting transcription with language: {lang or 'auto-detect'}")
                result = await self.transcribe_audio_bytes(audio_data, device_id=device_id, language=lang)
                
                # If successful or we don't need to try fallbacks, return the result
                if result.success:
                    logger.info(f"Transcription successful with language: {lang or 'auto-detect'}")
                    # Update the metadata to include the language used
                    if result.voice_command:
                        result.voice_command.metadata["language_used"] = lang or "auto-detect"
                    return result
                
            except Exception as e:
                logger.warning(f"Transcription failed with language {lang}: {str(e)}")
                continue  # Try the next language
        
        # If all attempts failed, return the last error result
        return VoiceCommandResult(
            success=False,
            error_message="All transcription attempts with different languages failed"
        )
    
    def validate_audio_quality(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Validate the quality of audio for transcription.
        
        Args:
            audio_data: Audio data in bytes
            
        Returns:
            Dictionary with validation results
        """
        try:
            import io
            import soundfile as sf
            import numpy as np
            
            # Load the audio
            audio_np, sr = sf.read(io.BytesIO(audio_data))
            
            # Use the voice audio processor to analyze quality
            quality_metrics = self.voice_audio_processor.detect_speech_quality(audio_np)
            
            # Additional quality checks
            duration = len(audio_np) / sr
            is_suitable_for_transcription = (
                quality_metrics["is_suitable"] and 
                duration >= 0.5 and  # At least 0.5 seconds
                duration <= 30.0     # At most 30 seconds
            )
            
            return {
                "is_suitable": is_suitable_for_transcription,
                "quality_metrics": quality_metrics,
                "duration": duration,
                "sample_rate": sr
            }
        except Exception as e:
            logger.error(f"Error validating audio quality: {str(e)}")
            return {
                "is_suitable": False,
                "error": str(e)
            }
    
    async def transcribe_with_context(self, audio_data: bytes, 
                                    context: Optional[Dict[str, Any]] = None,
                                    device_id: Optional[str] = None,
                                    language: Optional[str] = None) -> VoiceCommandResult:
        """
        Transcribe audio with additional context that can improve transcription quality.
        
        Args:
            audio_data: Audio data in bytes
            context: Additional context information
            device_id: Optional ID of the device where the command originated
            language: Optional language for transcription
            
        Returns:
            VoiceCommandResult with transcription result
        """
        # For now, we'll just store the context in the metadata
        # In a more advanced implementation, the context could be used to
        # influence the transcription process or be used for post-processing
        
        result = await self.transcribe_audio_bytes(audio_data, device_id=device_id, language=language)
        
        if result.voice_command and context:
            # Store context in the voice command's metadata
            result.voice_command.context_snapshot = context
        
        return result


class TranscriptionServiceManager:
    """
    Manager for handling multiple transcription services and their lifecycle.
    """
    
    def __init__(self):
        """
        Initialize the transcription service manager.
        """
        self.services: Dict[str, WhisperTranscriptionService] = {}
        self.default_service = self.create_default_service()
    
    def create_default_service(self) -> WhisperTranscriptionService:
        """
        Create a default transcription service with default configuration.
        
        Returns:
            Default WhisperTranscriptionService instance
        """
        config = VoiceProcessingPipelineConfig()
        service = WhisperTranscriptionService(config)
        self.services["default"] = service
        return service
    
    def create_service(self, name: str, config: VoiceProcessingPipelineConfig) -> WhisperTranscriptionService:
        """
        Create a new transcription service with the given name and configuration.
        
        Args:
            name: Name of the service
            config: Configuration for the service
            
        Returns:
            New WhisperTranscriptionService instance
        """
        service = WhisperTranscriptionService(config)
        self.services[name] = service
        return service
    
    def get_service(self, name: str = "default") -> WhisperTranscriptionService:
        """
        Get a transcription service by name.
        
        Args:
            name: Name of the service (default is "default")
            
        Returns:
            WhisperTranscriptionService instance
        """
        return self.services.get(name, self.default_service)
    
    def remove_service(self, name: str) -> bool:
        """
        Remove a transcription service by name.
        
        Args:
            name: Name of the service to remove
            
        Returns:
            True if the service was removed, False otherwise
        """
        if name in self.services:
            del self.services[name]
            return True
        return False
    
    async def transcribe_audio_bytes(self, audio_data: bytes, 
                                   service_name: str = "default",
                                   device_id: Optional[str] = None,
                                   language: Optional[str] = None) -> VoiceCommandResult:
        """
        Transcribe audio using a named service.
        
        Args:
            audio_data: Audio data in bytes
            service_name: Name of the service to use
            device_id: Optional ID of the device where the command originated
            language: Optional language for transcription
            
        Returns:
            VoiceCommandResult with transcription result
        """
        service = self.get_service(service_name)
        return await service.transcribe_audio_bytes(audio_data, device_id, language)
    
    async def transcribe_audio_file(self, filepath: str, 
                                  service_name: str = "default",
                                  device_id: Optional[str] = None,
                                  language: Optional[str] = None) -> VoiceCommandResult:
        """
        Transcribe audio file using a named service.
        
        Args:
            filepath: Path to the audio file
            service_name: Name of the service to use
            device_id: Optional ID of the device where the command originated
            language: Optional language for transcription
            
        Returns:
            VoiceCommandResult with transcription result
        """
        service = self.get_service(service_name)
        return await service.transcribe_audio_file(filepath, device_id, language)


# Global transcription service manager instance
_transcription_service_manager = None


def get_transcription_service_manager() -> TranscriptionServiceManager:
    """
    Get the global transcription service manager instance.
    
    Returns:
        TranscriptionServiceManager instance
    """
    global _transcription_service_manager
    if _transcription_service_manager is None:
        _transcription_service_manager = TranscriptionServiceManager()
    return _transcription_service_manager


def get_default_transcription_service() -> WhisperTranscriptionService:
    """
    Get the default transcription service instance.
    
    Returns:
        WhisperTranscriptionService instance
    """
    manager = get_transcription_service_manager()
    return manager.get_service("default")