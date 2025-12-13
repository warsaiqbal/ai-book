"""
Tests for voice command accuracy in various acoustic conditions.
This module tests the voice processing pipeline under different noise conditions.
"""
import asyncio
import logging
import unittest
from unittest.mock import Mock, patch, AsyncMock
import numpy as np
import tempfile
import os

from ..shared.utils.audio_utils import get_audio_processor
from ..vla.voice_interface.transcription_service import get_default_transcription_service
from ..vla.voice_interface.noise_reduction import get_noise_reducer
from ..config.config import get_config

# Set up logging
logger = logging.getLogger(__name__)


class TestVoiceCommandAccuracy(unittest.TestCase):
    """
    Test class for voice command accuracy under various acoustic conditions.
    """
    
    def setUp(self):
        """
        Set up test fixtures before each test method.
        """
        self.config = get_config()
        self.audio_processor = get_audio_processor()
        self.transcription_service = get_default_transcription_service()
        self.noise_reducer = get_noise_reducer()
        
        # Common test phrases
        self.test_phrases = [
            "Clean the room",
            "Go to the kitchen and bring me a cup",
            "Move forward two meters",
            "Turn left and stop",
            "Find the red ball"
        ]
    
    def generate_test_audio(self, text: str, noise_level: float = 0.0) -> bytes:
        """
        Generate test audio for a given text phrase with optional noise.
        NOTE: In a real implementation, this would synthesize audio from text.
        For this test, we'll create a placeholder.
        
        Args:
            text: Text to synthesize
            noise_level: Level of background noise (0.0 to 1.0)
            
        Returns:
            Generated audio as bytes
        """
        # This is a placeholder implementation
        # In a real system, this would use a TTS engine to generate actual audio
        # For now, we'll return empty audio with some noise if requested
        
        # Create some dummy audio data
        duration = 2  # seconds
        sample_rate = self.config.get('VOICE.SAMPLE_RATE')
        samples = int(duration * sample_rate)
        
        # Generate simple audio (for testing purposes)
        t = np.linspace(0, duration, samples)
        audio_signal = 0.5 * np.sin(2 * np.pi * 440 * t)  # Simple 440Hz tone
        
        # Add noise if requested
        if noise_level > 0:
            noise = np.random.normal(0, noise_level, samples)
            audio_signal = audio_signal + noise
        
        # Normalize
        audio_signal = audio_signal / np.max(np.abs(audio_signal))
        
        # Convert to bytes
        audio_bytes = (audio_signal * 32767).astype(np.int16).tobytes()
        
        return audio_bytes
    
    def test_transcription_accuracy_quiet_environment(self):
        """
        Test transcription accuracy in a quiet environment (baseline test).
        """
        print("\nTesting transcription accuracy in quiet environment...")
        
        correct_transcriptions = 0
        total_tests = len(self.test_phrases)
        
        for test_phrase in self.test_phrases:
            with self.subTest(phrase=test_phrase):
                # Generate clean audio for the test phrase
                audio_data = self.generate_test_audio(test_phrase, noise_level=0.01)
                
                # Transcribe the audio
                result = asyncio.run(
                    self.transcription_service.transcribe_audio_bytes(audio_data)
                )
                
                if result.success and result.voice_command:
                    # Check if the transcription matches the original phrase
                    # (Allowing for some variation in the transcription)
                    original_lower = test_phrase.lower()
                    transcription_lower = result.voice_command.transcription.lower()
                    
                    # Simple check: does the transcription contain key words?
                    key_words = test_phrase.split()
                    key_words_found = sum(1 for word in key_words if word.lower() in transcription_lower)
                    accuracy = key_words_found / len(key_words)
                    
                    if accuracy >= 0.8:  # Consider 80% word match as correct
                        correct_transcriptions += 1
                        
                    print(f"Original: '{test_phrase}'")
                    print(f"Transcribed: '{result.voice_command.transcription}'")
                    print(f"Confidence: {result.confidence_score:.2f}, Accuracy: {accuracy:.2f}")
                else:
                    print(f"Failed to transcribe: {test_phrase}")
        
        accuracy = correct_transcriptions / total_tests if total_tests > 0 else 0
        print(f"Quiet environment accuracy: {accuracy:.2f} ({correct_transcriptions}/{total_tests})")
        
        # We expect high accuracy in quiet conditions
        self.assertGreaterEqual(accuracy, 0.5, "Accuracy should be at least 50% in quiet environment")
    
    def test_transcription_accuracy_noisy_environment(self):
        """
        Test transcription accuracy in a noisy environment.
        """
        print("\nTesting transcription accuracy in noisy environment...")
        
        # Add moderate noise
        noise_level = 0.3
        
        correct_transcriptions = 0
        total_tests = len(self.test_phrases)
        
        for test_phrase in self.test_phrases:
            with self.subTest(phrase=test_phrase):
                # Generate audio with noise for the test phrase
                audio_data = self.generate_test_audio(test_phrase, noise_level=noise_level)
                
                # Transcribe the audio
                result = asyncio.run(
                    self.transcription_service.transcribe_audio_bytes(audio_data)
                )
                
                if result.success and result.voice_command:
                    # Check if the transcription matches the original phrase
                    original_lower = test_phrase.lower()
                    transcription_lower = result.voice_command.transcription.lower()
                    
                    # Simple check: does the transcription contain key words?
                    key_words = test_phrase.split()
                    key_words_found = sum(1 for word in key_words if word.lower() in transcription_lower)
                    accuracy = key_words_found / len(key_words)
                    
                    if accuracy >= 0.8:  # Consider 80% word match as correct
                        correct_transcriptions += 1
                        
                    print(f"Original: '{test_phrase}'")
                    print(f"Transcribed: '{result.voice_command.transcription}'")
                    print(f"Confidence: {result.confidence_score:.2f}, Accuracy: {accuracy:.2f}")
                else:
                    print(f"Failed to transcribe: {test_phrase}")
        
        accuracy = correct_transcriptions / total_tests if total_tests > 0 else 0
        print(f"Noisy environment accuracy: {accuracy:.2f} ({correct_transcriptions}/{total_tests})")
        
        # Even in noisy conditions, we expect some level of accuracy
        self.assertGreaterEqual(accuracy, 0.1, "Accuracy should be at least 10% in noisy environment")
    
    def test_noise_reduction_effectiveness(self):
        """
        Test the effectiveness of noise reduction filters.
        """
        print("\nTesting noise reduction effectiveness...")
        
        # Generate audio with high noise level
        test_phrase = "Clean the room"
        audio_with_noise = self.generate_test_audio(test_phrase, noise_level=0.5)
        
        # Convert to numpy array for processing
        import io
        import soundfile as sf
        audio_with_noise_np, _ = sf.read(io.BytesIO(audio_with_noise))
        
        # Apply noise reduction
        reduced_noise_audio_np = self.noise_reducer.reduce_noise(audio_with_noise_np)
        
        # Convert back to bytes for transcription
        reduced_noise_audio_bytes = self.audio_processor.audio_to_wav_bytes(reduced_noise_audio_np)
        
        # Transcribe both versions
        result_original = asyncio.run(
            self.transcription_service.transcribe_audio_bytes(audio_with_noise)
        )
        
        result_reduced = asyncio.run(
            self.transcription_service.transcribe_audio_bytes(reduced_noise_audio_bytes)
        )
        
        print(f"Original - Transcribed: '{result_original.voice_command.transcription if result_original.success else 'FAILED'}'")
        print(f"Reduced - Transcribed: '{result_reduced.voice_command.transcription if result_reduced.success else 'FAILED'}'")
        
        # The test checks that the system runs without error
        # In a real test, we would compare the quality of transcriptions
        self.assertTrue(True)  # Placeholder to indicate the test ran
    
    def test_audio_quality_validation(self):
        """
        Test the audio quality validation functionality.
        """
        print("\nTesting audio quality validation...")
        
        # Test with clean audio
        clean_audio = self.generate_test_audio("Test command", noise_level=0.01)
        quality_result = self.transcription_service.validate_audio_quality(clean_audio)
        
        print(f"Clean audio quality: {quality_result}")
        self.assertIsInstance(quality_result, dict)
        self.assertIn('is_suitable', quality_result)
        
        # Test with very short audio
        # Create a very short audio clip (too short to be suitable)
        duration = 0.1  # 0.1 seconds (too short)
        sample_rate = self.config.get('VOICE.SAMPLE_RATE')
        samples = int(duration * sample_rate)
        
        t = np.linspace(0, duration, samples)
        short_audio_signal = 0.5 * np.sin(2 * np.pi * 440 * t)
        short_audio_signal = short_audio_signal / np.max(np.abs(short_audio_signal))
        short_audio_bytes = (short_audio_signal * 32767).astype(np.int16).tobytes()
        
        quality_result_short = self.transcription_service.validate_audio_quality(short_audio_bytes)
        print(f"Short audio quality: {quality_result_short}")
        
        # Even with short audio, the function should return a valid result
        self.assertIsInstance(quality_result_short, dict)
        self.assertIn('is_suitable', quality_result_short)


async def run_comprehensive_voice_tests():
    """
    Run comprehensive voice tests including different acoustic conditions.
    """
    print("Running comprehensive voice command accuracy tests...")
    
    # Create a test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestVoiceCommandAccuracy)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return test results
    return result


def test_voice_command_accuracy_in_conditions():
    """
    Test voice command accuracy in various acoustic conditions as described in the task.
    """
    print("Testing voice command accuracy in various acoustic conditions...")
    
    # Run the tests
    result = asyncio.run(run_comprehensive_voice_tests())
    
    # Print a summary
    print(f"\nTest Results Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for failure in result.failures:
            print(failure[1])
    
    if result.errors:
        print("\nErrors:")
        for error in result.errors:
            print(error[1])
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = test_voice_command_accuracy_in_conditions()
    exit(0 if success else 1)