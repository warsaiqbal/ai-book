"""
Speech Recognition Interface for the VLA system.
This module provides a high-level interface for speech recognition tasks,
integrating Whisper with the voice interface components.
"""
import asyncio
import logging
from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime

from ...shared.models.data_models import VoiceCommand
from ...shared.utils.audio_utils import get_audio_processor
from ...shared.utils.logging import get_logger
from .whisper_integration import get_whisper_integration
from .audio_processing import get_voice_audio_processor

# Set up logging
logger = get_logger(__name__)


class SpeechRecognitionInterface:
    """
    High-level interface for speech recognition tasks.
    Provides methods to recognize speech from various input sources and
    convert them to VoiceCommand objects.
    """
    
    def __init__(self):
        """
        Initialize the speech recognition interface.
        """
        self.whisper_integration = get_whisper_integration()
        self.audio_processor = get_audio_processor()
        self.voice_audio_processor = get_voice_audio_processor()
        self.is_listening = False
        self.listening_callbacks = []
    
    async def recognize_from_microphone(self, duration: float = 5.0, 
                                      device_id: Optional[str] = None) -> Optional[VoiceCommand]:
        """
        Record audio from the microphone and recognize speech.
        
        Args:
            duration: Duration in seconds to record audio
            device_id: Optional ID of the audio input device
            
        Returns:
            VoiceCommand object with recognized speech, or None if recognition failed
        """
        try:
            logger.info(f"Recording audio from microphone for {duration} seconds")
            
            # Record audio from microphone
            audio_data_bytes = self.audio_processor.record_audio(duration)
            
            # Convert bytes to numpy array for preprocessing
            import io
            import soundfile as sf
            import numpy as np
            
            audio_np, sr = sf.read(io.BytesIO(audio_data_bytes))
            
            # Preprocess the audio specifically for voice recognition
            preprocessed_audio = self.voice_audio_processor.preprocess_for_transcription(audio_np)
            
            # Convert back to bytes for Whisper processing
            processed_bytes = self.audio_processor.audio_to_wav_bytes(preprocessed_audio)
            
            # Transcribe the audio
            transcription_result = await self.whisper_integration.transcribe_audio_bytes(
                processed_bytes
            )
            
            if transcription_result is None:
                logger.error("Failed to transcribe recorded audio")
                return None
            
            # Create VoiceCommand object
            voice_command = VoiceCommand(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                audioData=None,  # Not storing raw audio to save space
                transcription=transcription_result["transcription"],
                confidence=transcription_result["confidence"],
                intent="",  # Will be determined by cognitive planning
                rawAudioPath=None,
                metadata={
                    "sourceDevice": device_id or f"mic_{self.audio_processor.device_index}",
                    "audioFormat": "wav",
                    "language": transcription_result["language"],
                    "noiseLevel": "unknown"  # Would be computed in a full implementation
                }
            )
            
            logger.info(f"Successfully recognized speech: '{voice_command.transcription}'")
            return voice_command
            
        except Exception as e:
            logger.error(f"Error in microphone speech recognition: {str(e)}")
            return None
    
    async def recognize_from_audio_file(self, filepath: str, 
                                      device_id: Optional[str] = None) -> Optional[VoiceCommand]:
        """
        Recognize speech from an audio file.
        
        Args:
            filepath: Path to the audio file
            device_id: Optional ID of the device where the command originated
            
        Returns:
            VoiceCommand object with recognized speech, or None if recognition failed
        """
        try:
            logger.info(f"Recognizing speech from audio file: {filepath}")
            
            # Preprocess the audio file
            preprocessed_path = self.voice_audio_processor.preprocess_audio_file(filepath)
            
            # Transcribe the preprocessed audio file
            transcription_result = await self.whisper_integration.transcribe_audio(
                preprocessed_path
            )
            
            # Clean up temporary file if it was created
            import os
            if os.path.basename(filepath) != os.path.basename(preprocessed_path):
                os.unlink(preprocessed_path)
            
            if transcription_result is None:
                logger.error("Failed to transcribe audio file")
                return None
            
            # Create VoiceCommand object
            voice_command = VoiceCommand(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                audioData=None,
                transcription=transcription_result["transcription"],
                confidence=transcription_result["confidence"],
                intent="",  # Will be determined by cognitive planning
                rawAudioPath=filepath,
                metadata={
                    "sourceDevice": device_id or "file_input",
                    "audioFormat": "wav",
                    "language": transcription_result["language"],
                    "noiseLevel": "unknown"
                }
            )
            
            logger.info(f"Successfully recognized speech from file: '{voice_command.transcription}'")
            return voice_command
            
        except Exception as e:
            logger.error(f"Error in audio file speech recognition: {str(e)}")
            return None
    
    async def recognize_from_audio_bytes(self, audio_bytes: bytes, 
                                       device_id: Optional[str] = None) -> Optional[VoiceCommand]:
        """
        Recognize speech from audio data in bytes format.
        
        Args:
            audio_bytes: Audio data in bytes
            device_id: Optional ID of the device where the command originated
            
        Returns:
            VoiceCommand object with recognized speech, or None if recognition failed
        """
        try:
            logger.info("Recognizing speech from audio bytes")
            
            # Preprocess the audio bytes
            import io
            import soundfile as sf
            import numpy as np
            
            # Load the audio from bytes
            audio_np, sr = sf.read(io.BytesIO(audio_bytes))
            
            # Preprocess the audio specifically for voice recognition
            preprocessed_audio = self.voice_audio_processor.preprocess_for_transcription(audio_np)
            
            # Convert back to bytes for Whisper processing
            processed_bytes = self.audio_processor.audio_to_wav_bytes(preprocessed_audio)
            
            # Transcribe the audio
            transcription_result = await self.whisper_integration.transcribe_audio_bytes(
                processed_bytes
            )
            
            if transcription_result is None:
                logger.error("Failed to transcribe audio bytes")
                return None
            
            # Create VoiceCommand object
            voice_command = VoiceCommand(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                audioData=None,
                transcription=transcription_result["transcription"],
                confidence=transcription_result["confidence"],
                intent="",  # Will be determined by cognitive planning
                rawAudioPath=None,
                metadata={
                    "sourceDevice": device_id or "byte_input",
                    "audioFormat": "wav",
                    "language": transcription_result["language"],
                    "noiseLevel": "unknown"
                }
            )
            
            logger.info(f"Successfully recognized speech from bytes: '{voice_command.transcription}'")
            return voice_command
            
        except Exception as e:
            logger.error(f"Error in audio bytes speech recognition: {str(e)}")
            return None
    
    def start_continuous_listening(self, callback: callable, 
                                 silence_threshold: float = 0.01,
                                 min_audio_duration: float = 0.5):
        """
        Start continuous listening for voice commands.
        
        Args:
            callback: Function to call when a voice command is recognized
            silence_threshold: Threshold below which audio is considered silent
            min_audio_duration: Minimum duration of audio to process (in seconds)
        """
        if self.is_listening:
            logger.warning("Continuous listening is already active")
            return
        
        self.is_listening = True
        self.listening_callbacks.append(callback)
        
        async def listening_loop():
            logger.info("Starting continuous listening loop")
            
            while self.is_listening:
                try:
                    # Record a chunk of audio
                    audio_chunk = self.audio_processor.get_audio_chunk(timeout=1.0)
                    
                    if audio_chunk is not None:
                        # Convert to numpy array to check for speech
                        import io
                        import soundfile as sf
                        import numpy as np
                        
                        audio_np, sr = sf.read(io.BytesIO(audio_chunk))
                        
                        # Check if the audio contains speech (not just silence)
                        if not self.audio_processor.detect_silence(
                            audio_np, 
                            threshold=silence_threshold,
                            min_silence_duration=min_audio_duration
                        ):
                            # Process the non-silent audio
                            voice_command = await self.recognize_from_audio_bytes(
                                audio_chunk
                            )
                            
                            if voice_command:
                                # Call all registered callbacks
                                for cb in self.listening_callbacks:
                                    try:
                                        cb(voice_command)
                                    except Exception as e:
                                        logger.error(f"Error in listening callback: {str(e)}")
                
                except Exception as e:
                    logger.error(f"Error in continuous listening loop: {str(e)}")
                    await asyncio.sleep(0.1)  # Small delay to prevent busy loop
        
        # Run the listening loop in the background
        asyncio.create_task(listening_loop())
    
    def stop_continuous_listening(self):
        """
        Stop continuous listening for voice commands.
        """
        logger.info("Stopping continuous listening")
        self.is_listening = False
        self.listening_callbacks.clear()
    
    async def batch_recognize(self, audio_files: List[str]) -> List[Optional[VoiceCommand]]:
        """
        Perform batch recognition on multiple audio files.
        
        Args:
            audio_files: List of paths to audio files
            
        Returns:
            List of VoiceCommand objects (None for failed recognitions)
        """
        logger.info(f"Starting batch recognition for {len(audio_files)} files")
        
        tasks = []
        for filepath in audio_files:
            task = self.recognize_from_audio_file(filepath)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions that occurred during batch processing
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error processing file {audio_files[i]}: {str(result)}")
                processed_results.append(None)
            else:
                processed_results.append(result)
        
        logger.info("Batch recognition completed")
        return processed_results
    
    def estimate_recognition_quality(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Estimate the quality of audio for speech recognition.
        
        Args:
            audio_data: Audio data in bytes
            
        Returns:
            Dictionary with quality metrics
        """
        try:
            import io
            import soundfile as sf
            import numpy as np
            
            # Load the audio from bytes
            audio_np, sr = sf.read(io.BytesIO(audio_data))
            
            # Use the voice audio processor to analyze quality
            quality_metrics = self.voice_audio_processor.detect_speech_quality(audio_np)
            
            return quality_metrics
        except Exception as e:
            logger.error(f"Error estimating recognition quality: {str(e)}")
            return {
                "is_suitable": False,
                "error": str(e)
            }


# Global instance of the speech recognition interface
_speech_recognition_interface = None


def get_speech_recognition_interface() -> SpeechRecognitionInterface:
    """
    Get the global speech recognition interface instance.
    
    Returns:
        SpeechRecognitionInterface instance
    """
    global _speech_recognition_interface
    if _speech_recognition_interface is None:
        _speech_recognition_interface = SpeechRecognitionInterface()
    return _speech_recognition_interface