"""
Logging and configuration management system for the AI-Robot Brain project.

This module provides centralized configuration management and logging
capabilities for all components of the system.
"""

import os
import json
import yaml
import logging
import logging.config
from typing import Dict, Any, Optional, Union
from pathlib import Path
import sys
from dataclasses import dataclass, asdict


@dataclass
class LoggingConfig:
    """Configuration for logging system."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_bytes: int = 10485760  # 10MB
    backup_count: int = 5
    console_output: bool = True


@dataclass
class AppConfig:
    """Main application configuration."""
    # System configuration
    name: str = "AI-Robot Brain"
    version: str = "1.0.0"
    debug: bool = False
    
    # Robot-specific configuration
    robot_name: str = "bipedal_robot"
    namespace: str = "robot"
    use_sim_time: bool = True
    
    # Performance configuration
    simulation_rate: float = 60.0  # Hz
    control_rate: float = 100.0    # Hz
    perception_rate: float = 30.0  # Hz
    
    # Resource configuration
    max_memory_mb: int = 4096
    gpu_enabled: bool = True
    gpu_device: str = "cuda:0"
    
    # Paths configuration
    data_path: str = "./data"
    model_path: str = "./models"
    log_path: str = "./logs"
    config_path: str = "./config"
    assets_path: str = "./assets"
    
    # Network configuration (if applicable)
    network_interface: str = "lo"  # loopback by default
    robot_ip: str = "127.0.0.1"
    robot_port: int = 9090
    
    # Logging configuration
    logging: LoggingConfig = None
    
    def __post_init__(self):
        """Initialize nested objects if not provided."""
        if self.logging is None:
            self.logging = LoggingConfig()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self)
    
    def save_to_file(self, file_path: str, format: str = "json"):
        """Save configuration to file in specified format."""
        data = self.to_dict()
        
        if format.lower() == "json":
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        elif format.lower() == "yaml":
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported format: {format}")


class ConfigManager:
    """Singleton class for managing application configuration."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Create singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize configuration manager."""
        if not self._initialized:
            self.config: Optional[AppConfig] = None
            self._initialized = True
    
    def initialize(self, config: Union[AppConfig, str, None] = None):
        """Initialize with default config or from file."""
        if isinstance(config, str):
            # Load from file
            self.config = self.load_from_file(config)
        elif isinstance(config, AppConfig):
            self.config = config
        else:
            # Use default configuration
            self.config = AppConfig()
    
    def load_from_file(self, file_path: str) -> AppConfig:
        """Load configuration from file (JSON or YAML)."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        if file_path.suffix.lower() in ['.yaml', '.yml']:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
        elif file_path.suffix.lower() == '.json':
            with open(file_path, 'r') as f:
                data = json.load(f)
        else:
            raise ValueError(f"Unsupported config file format: {file_path.suffix}")
        
        # Create config object from data
        config = AppConfig(**data)
        
        # Handle nested logging config
        if 'logging' in data and data['logging']:
            config.logging = LoggingConfig(**data['logging'])
        
        return config
    
    def get_config(self) -> AppConfig:
        """Get the current configuration."""
        if self.config is None:
            self.initialize()
        return self.config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key (e.g., 'robot_name')."""
        if self.config is None:
            self.initialize()
        
        # Try to get value from config directly
        if hasattr(self.config, key):
            return getattr(self.config, key)
        
        # If not found, return default
        return default
    
    def set(self, key: str, value: Any):
        """Set a configuration value by key."""
        if self.config is None:
            self.initialize()
        
        if hasattr(self.config, key):
            setattr(self.config, key, value)
        else:
            raise AttributeError(f"Configuration has no attribute: {key}")


def setup_logging(config: LoggingConfig = None, name: str = "ai_robot_brain"):
    """
    Set up logging configuration for the application.
    
    Args:
        config: Logging configuration (uses default if not provided)
        name: Name of the logger
    """
    if config is None:
        config = LoggingConfig()
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(config.level.upper())
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(config.format)
    
    # Add console handler if enabled
    if config.console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(config.level.upper())
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Add file handler if path is specified
    if config.file_path:
        # Ensure log directory exists
        log_dir = Path(config.file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(config.file_path)
        file_handler.setLevel(config.level.upper())
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Prevent adding handlers multiple times
    logger.propagate = False
    
    return logger


def get_logger(name: str = "ai_robot_brain") -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Name of the logger to get
        
    Returns:
        Configured logger instance
    """
    config_manager = ConfigManager()
    config = config_manager.get_config()
    
    logger = setup_logging(config.logging, name)
    return logger


def validate_config(config: AppConfig) -> Dict[str, str]:
    """
    Validate configuration values and return any issues found.
    
    Args:
        config: Configuration to validate
        
    Returns:
        Dictionary of validation issues (empty if all valid)
    """
    issues = {}
    
    # Validate paths exist
    for path_attr in ['data_path', 'model_path', 'log_path', 'config_path', 'assets_path']:
        path = getattr(config, path_attr)
        if not os.path.exists(path):
            # Try to create the directory
            try:
                os.makedirs(path, exist_ok=True)
            except Exception as e:
                issues[path_attr] = f"Path does not exist and cannot be created: {path} ({e})"
    
    # Validate rates
    if config.simulation_rate <= 0:
        issues['simulation_rate'] = "Simulation rate must be positive"
    
    if config.control_rate <= 0:
        issues['control_rate'] = "Control rate must be positive"
    
    if config.perception_rate <= 0:
        issues['perception_rate'] = "Perception rate must be positive"
    
    # Validate memory limit
    if config.max_memory_mb <= 0:
        issues['max_memory_mb'] = "Max memory must be positive"
    
    # Validate port
    if not (1 <= config.robot_port <= 65535):
        issues['robot_port'] = "Port must be between 1 and 65535"
    
    return issues


def load_default_config() -> AppConfig:
    """Load default configuration for the AI-Robot Brain project."""
    config_manager = ConfigManager()
    config_manager.initialize()
    return config_manager.get_config()


def get_config_value(key: str, default: Any = None) -> Any:
    """Get a configuration value using the singleton manager."""
    config_manager = ConfigManager()
    return config_manager.get(key, default)


def init_app() -> AppConfig:
    """
    Initialize the application by loading configuration and setting up logging.
    
    Returns:
        The loaded application configuration
    """
    config_manager = ConfigManager()
    
    # Try to load from environment or default
    config_path = os.getenv("AI_ROBOT_CONFIG_PATH")
    if config_path and os.path.exists(config_path):
        config_manager.initialize(config_path)
    else:
        config_manager.initialize()
    
    # Validate configuration
    config = config_manager.get_config()
    issues = validate_config(config)
    
    if issues:
        logger = get_logger()
        for key, issue in issues.items():
            logger.warning(f"Configuration issue with {key}: {issue}")
    
    # Set up logging
    setup_logging(config.logging)
    
    return config


# Predefined configuration profiles
def get_simulation_config() -> AppConfig:
    """Get configuration optimized for simulation."""
    config = AppConfig(
        name="AI-Robot Brain - Simulation",
        debug=True,
        use_sim_time=True,
        simulation_rate=60.0,
        control_rate=100.0,
        perception_rate=30.0,
        logging=LoggingConfig(
            level="DEBUG",
            file_path="./logs/simulation.log",
            console_output=True
        )
    )
    return config


def get_real_robot_config() -> AppConfig:
    """Get configuration optimized for real robot deployment."""
    config = AppConfig(
        name="AI-Robot Brain - Real Robot",
        debug=False,
        use_sim_time=False,
        simulation_rate=50.0,  # May be slower in real world
        control_rate=200.0,    # Higher control rate for real hardware
        perception_rate=15.0,  # May be slower due to real sensor limitations
        logging=LoggingConfig(
            level="INFO",
            file_path="./logs/robot.log",
            console_output=False  # Less console output on robot
        )
    )
    return config


def get_development_config() -> AppConfig:
    """Get configuration optimized for development."""
    config = AppConfig(
        name="AI-Robot Brain - Development",
        debug=True,
        use_sim_time=True,
        simulation_rate=30.0,  # Slower for debugging
        control_rate=50.0,
        perception_rate=10.0,
        logging=LoggingConfig(
            level="DEBUG",
            file_path="./logs/development.log",
            console_output=True
        )
    )
    return config


# Initialize the configuration manager when module is imported
if ConfigManager._instance is None:
    config_manager = ConfigManager()