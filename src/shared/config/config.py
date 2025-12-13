import os
from pathlib import Path
from typing import Dict, Any

import yaml
from dotenv import load_dotenv


class Config:
    """
    Configuration class to load settings from YAML file and environment variables.
    Environment variables take precedence over YAML file values.
    """

    def __init__(self, config_path: str = None):
        # Load environment variables from .env file
        load_dotenv()

        # Default config path
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"

        # Load configuration from YAML file
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)

        # Override with environment variables if they exist
        self._override_with_env_vars()

    def _override_with_env_vars(self):
        """Override config values with environment variables if they exist."""
        # Voice configuration
        self._update_config_value('VOICE', 'WHISPER_MODEL', 'WHISPER_MODEL')
        self._update_config_value('VOICE', 'SAMPLE_RATE', 'VOICE_SAMPLE_RATE', int)
        self._update_config_value('VOICE', 'CHUNK_SIZE', 'VOICE_CHUNK_SIZE', int)
        self._update_config_value('VOICE', 'AUDIO_DEVICE_INDEX', 'AUDIO_DEVICE_INDEX', int)

        # LLM configuration
        self._update_config_value('LLM', 'MODEL', 'LLM_MODEL')
        self._update_config_value('LLM', 'MAX_TOKENS', 'LLM_MAX_TOKENS', int)
        self._update_config_value('LLM', 'TEMPERATURE', 'LLM_TEMPERATURE', float)
        self._update_config_value('LLM', 'TIMEOUT_SECONDS', 'LLM_TIMEOUT_SECONDS', int)

        # Navigation configuration
        self._update_config_value('NAVIGATION', 'MAX_LINEAR_VELOCITY', 'MAX_LINEAR_VELOCITY', float)
        self._update_config_value('NAVIGATION', 'MAX_ANGULAR_VELOCITY', 'MAX_ANGULAR_VELOCITY', float)
        self._update_config_value('NAVIGATION', 'GOAL_TOLERANCE', 'GOAL_TOLERANCE', float)
        self._update_config_value('NAVIGATION', 'ANGULAR_TOLERANCE', 'ANGULAR_TOLERANCE', float)

        # Perception configuration
        self._update_config_value('PERCEPTION', 'CONFIDENCE_THRESHOLD', 'PERCEPTION_CONFIDENCE_THRESHOLD', float)
        self._update_config_value('PERCEPTION', 'MAX_DETECTION_DISTANCE', 'PERCEPTION_MAX_DETECTION_DISTANCE', float)
        # Handle DETECTION_CLASSES as a comma-separated string
        detection_classes = os.getenv('PERCEPTION_DETECTION_CLASSES')
        if detection_classes is not None:
            self._config['PERCEPTION']['DETECTION_CLASSES'] = [cls.strip() for cls in detection_classes.split(',')]

        # Manipulation configuration
        self._update_config_value('MANIPULATION', 'GRIPPER_OPEN_POSITION', 'GRIPPER_OPEN_POSITION', float)
        self._update_config_value('MANIPULATION', 'GRIPPER_CLOSE_POSITION', 'GRIPPER_CLOSE_POSITION', float)
        self._update_config_value('MANIPULATION', 'MAX_GRIPPER_FORCE', 'MAX_GRIPPER_FORCE', float)

        # System configuration
        self._update_config_value('SYSTEM', 'SIMULATION_MODE', 'SIMULATION_MODE', self._str_to_bool)
        self._update_config_value('SYSTEM', 'DEBUG_MODE', 'DEBUG_MODE', self._str_to_bool)
        self._update_config_value('SYSTEM', 'ROS_DOMAIN_ID', 'ROS_DOMAIN_ID', int)
        self._update_config_value('SYSTEM', 'DEFAULT_ROBOT_MODEL', 'DEFAULT_ROBOT_MODEL')
        self._update_config_value('SYSTEM', 'API_HOST', 'API_HOST')
        self._update_config_value('SYSTEM', 'API_PORT', 'API_PORT', int)

    def _update_config_value(self, section: str, key: str, env_name: str, converter=None):
        """Update a config value with environment variable if it exists."""
        env_value = os.getenv(env_name)
        if env_value is not None:
            if converter:
                try:
                    env_value = converter(env_value)
                except ValueError:
                    # If conversion fails, keep original value
                    pass
            self._config[section][key] = env_value

    def _str_to_bool(self, value: str) -> bool:
        """Convert string to boolean."""
        if isinstance(value, bool):
            return value
        if value.lower() in ('true', '1', 'yes', 'on', 'y'):
            return True
        if value.lower() in ('false', '0', 'no', 'off', 'n'):
            return False
        # If it's not a recognized boolean string, raise an error
        raise ValueError(f"Cannot convert '{value}' to boolean")

    def get(self, key: str) -> Any:
        """
        Get a configuration value using dot notation.
        Example: config.get('VOICE.WHISPER_MODEL')
        """
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                raise KeyError(f"Configuration key '{key}' not found")

        return value

    def get_section(self, section: str) -> Dict[str, Any]:
        """Get an entire configuration section."""
        if section in self._config:
            return self._config[section]
        else:
            raise KeyError(f"Configuration section '{section}' not found")


# Singleton instance
_config = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config