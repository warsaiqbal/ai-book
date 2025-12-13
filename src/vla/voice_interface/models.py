"""
Voice Command Data Model for the VLA system.
This module defines specialized data models for voice commands and related
voice processing entities that extend the base models.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from ...shared.models.data_models import VoiceCommand as BaseVoiceCommand, Point3D, Quaternion, Pose
from ...shared.utils.audio_utils import get_audio_processor


class VoiceCommandSegment(BaseModel):
    """
    Represents a segment of a voice command with timing and confidence information.
    """
    start_time: float  # Start time in seconds from beginning of audio
    end_time: float    # End time in seconds from beginning of audio
    text: str          # Transcribed text for this segment
    confidence: float  # Confidence score for this segment (0-1)
    tokens: Optional[List[str]] = None  # List of tokens in this segment
    temperature: Optional[float] = None  # Temperature used during transcription


class VoiceActivityInfo(BaseModel):
    """
    Information about voice activity in an audio recording.
    """
    has_voice: bool  # Whether voice activity was detected
    voice_start_time: Optional[float] = None  # Time of first voice activity (seconds)
    voice_end_time: Optional[float] = None    # Time of last voice activity (seconds)
    total_voice_duration: float = 0.0         # Total duration of voice activity (seconds)
    max_amplitude: float = 0.0               # Maximum amplitude during voice activity
    avg_amplitude: float = 0.0               # Average amplitude during voice activity
    snr_estimate: Optional[float] = None     # Estimated signal-to-noise ratio


class VoiceCommandClassification(BaseModel):
    """
    Classification result for a voice command.
    """
    intent: str                    # Primary intent of the command
    confidence: float             # Confidence in the classification (0-1)
    alternative_intents: Optional[List[Dict[str, Any]]] = None  # Other possible interpretations
    entities: Optional[Dict[str, Any]] = None  # Extracted entities from the command
    action_required: Optional[str] = None  # Specific action to take based on command


class EnhancedVoiceCommand(BaseVoiceCommand):
    """
    Enhanced voice command model that includes additional fields for
    voice processing and analysis beyond the base model.
    """
    # Additional fields specific to voice processing
    segments: List[VoiceCommandSegment] = Field(default_factory=list)  # Segments of the transcription
    voice_activity: Optional[VoiceActivityInfo] = None  # Voice activity information
    classification: Optional[VoiceCommandClassification] = None  # Command classification
    language_confidence: Optional[float] = None  # Confidence in detected language
    processing_time_ms: Optional[float] = None  # Time taken to process (milliseconds)
    audio_features: Optional[Dict[str, Any]] = None  # Additional audio features
    audio_quality_score: Optional[float] = None  # Quality score of the audio input (0-1)
    
    # Relations to other entities in the system
    related_command_id: Optional[str] = None  # ID of a related previous command (for multi-turn)
    follow_up_commands: Optional[List[str]] = None  # Potential follow-up command IDs
    context_snapshot: Optional[Dict[str, Any]] = None  # Context at time of command
    
    # Additional metadata
    device_location: Optional[Point3D] = None  # 3D location of the device that captured the command
    device_orientation: Optional[Quaternion] = None  # Orientation of the device
    spatial_context: Optional[Pose] = None  # Spatial context of the command
    acoustic_environment: Optional[str] = None  # Description of acoustic environment
    
    def add_segment(self, start_time: float, end_time: float, text: str, confidence: float):
        """
        Add a segment to the voice command.
        
        Args:
            start_time: Start time in seconds
            end_time: End time in seconds
            text: Transcribed text
            confidence: Confidence score (0-1)
        """
        segment = VoiceCommandSegment(
            start_time=start_time,
            end_time=end_time,
            text=text,
            confidence=confidence
        )
        self.segments.append(segment)
    
    def calculate_average_confidence(self) -> float:
        """
        Calculate the average confidence across all segments.
        
        Returns:
            Average confidence score (0-1)
        """
        if not self.segments:
            return self.confidence if self.confidence else 0.0
        
        total_confidence = sum(segment.confidence for segment in self.segments)
        return total_confidence / len(self.segments)
    
    def set_voice_activity(self, audio_data: bytes):
        """
        Analyze audio data to populate voice activity information.
        
        Args:
            audio_data: Raw audio data as bytes
        """
        try:
            # Use the audio processor to analyze the audio
            import io
            import soundfile as sf
            import numpy as np
            
            audio_np, sr = sf.read(io.BytesIO(audio_data))
            
            # Calculate voice activity metrics
            energy_threshold = 0.001  # Adjust based on your environment
            voice_frames = audio_np[np.abs(audio_np) > energy_threshold]
            
            if len(voice_frames) > 0:
                # Calculate time indices for voice activity
                voice_indices = np.where(np.abs(audio_np) > energy_threshold)[0]
                total_samples = len(audio_np)
                
                # Calculate start and end of voice activity in seconds
                start_time = voice_indices[0] / sr if len(voice_indices) > 0 else 0
                end_time = voice_indices[-1] / sr if len(voice_indices) > 0 else 0
                duration = end_time - start_time
                
                # Calculate amplitudes
                max_amplitude = float(np.max(np.abs(voice_frames))) if len(voice_frames) > 0 else 0.0
                avg_amplitude = float(np.mean(np.abs(voice_frames))) if len(voice_frames) > 0 else 0.0
                
                self.voice_activity = VoiceActivityInfo(
                    has_voice=True,
                    voice_start_time=start_time,
                    voice_end_time=end_time,
                    total_voice_duration=duration,
                    max_amplitude=max_amplitude,
                    avg_amplitude=avg_amplitude
                )
            else:
                self.voice_activity = VoiceActivityInfo(
                    has_voice=False,
                    total_voice_duration=0.0,
                    max_amplitude=0.0,
                    avg_amplitude=0.0
                )
        except Exception as e:
            import logging
            logging.error(f"Error calculating voice activity: {str(e)}")
    
    def get_command_duration(self) -> float:
        """
        Calculate the total duration of the voice command based on segments.
        
        Returns:
            Duration in seconds
        """
        if self.segments:
            # Duration based on segments
            max_end_time = max(segment.end_time for segment in self.segments) if self.segments else 0.0
            min_start_time = min(segment.start_time for segment in self.segments) if self.segments else 0.0
            return max_end_time - min_start_time
        else:
            # If no segments, return 0 or try to get from metadata if possible
            return 0.0


class VoiceCommandBatch(BaseModel):
    """
    A batch of voice commands, typically from a single session or context.
    """
    id: str
    timestamp: datetime
    commands: List[EnhancedVoiceCommand]
    session_id: Optional[str] = None  # ID of the session these commands belong to
    metadata: Dict[str, Any] = Field(default_factory=dict)  # Additional metadata
    
    def add_command(self, command: EnhancedVoiceCommand):
        """
        Add a voice command to the batch.
        
        Args:
            command: EnhancedVoiceCommand to add
        """
        self.commands.append(command)
    
    def get_commands_by_intent(self, intent: str) -> List[EnhancedVoiceCommand]:
        """
        Get all commands in the batch that match a specific intent.
        
        Args:
            intent: The intent to filter by
            
        Returns:
            List of commands with the specified intent
        """
        return [
            cmd for cmd in self.commands
            if cmd.classification and cmd.classification.intent == intent
        ]


class VoiceProcessingPipelineConfig(BaseModel):
    """
    Configuration for the voice processing pipeline.
    """
    whisper_model: str = "base"  # Model size for Whisper
    language: Optional[str] = None  # Language code (e.g., 'en', 'es')
    sample_rate: int = 16000  # Target sample rate
    energy_threshold: float = 0.01  # Threshold for voice activity detection
    silence_duration_threshold: float = 1.0  # Seconds of silence to consider speech ended
    vad_enabled: bool = True  # Whether to use voice activity detection
    noise_suppression: bool = True  # Whether to apply noise suppression
    quality_threshold: float = 0.5  # Minimum quality score for commands to be processed
    response_timeout: float = 10.0  # Timeout for processing responses (seconds)


class VoiceCommandResult(BaseModel):
    """
    Result of processing a voice command through the pipeline.
    """
    success: bool
    voice_command: Optional[EnhancedVoiceCommand] = None
    error_message: Optional[str] = None
    processing_time_ms: Optional[float] = None
    confidence_score: Optional[float] = None
    action_required: Optional[str] = None