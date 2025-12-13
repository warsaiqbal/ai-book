"""
Base simulation configuration for the AI-Robot Brain project.

This module defines the core configuration parameters for the simulation environment,
including physics properties, rendering settings, and global simulation parameters.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import os


@dataclass
class PhysicsConfig:
    """Configuration for physics simulation parameters."""
    gravity: tuple = (0.0, 0.0, -9.81)  # Gravity vector (x, y, z) in m/s^2
    solver_type: str = "pgs"  # Physics solver type
    solver_iterations: int = 128  # Number of solver iterations
    enable_ccd: bool = False  # Enable continuous collision detection
    ccd_threshold: float = 1e-7  # CCD threshold
    max_depenetration_velocity: float = 10.0  # Maximum depenetration velocity
    friction_model: str = "box"  # Friction model: box, cone, or none
    restitution_threshold: float = 2.0  # Restitution threshold in m/s


@dataclass
class RenderingConfig:
    """Configuration for rendering parameters."""
    resolution: tuple = (1920, 1080)  # Rendering resolution (width, height)
    enable_msaa: bool = True  # Enable multi-sample anti-aliasing
    msaa_samples: int = 4  # MSAA sample count
    enable_fxaa: bool = True  # Enable fast approximate anti-aliasing
    enable_postfx: bool = True  # Enable post-processing effects
    enable_rt: bool = True  # Enable ray tracing (if supported)
    max_render_time: float = 1.0 / 60.0  # Maximum time for rendering a frame


@dataclass
class SimulationConfig:
    """Main configuration for the Isaac Sim environment."""
    # Physics configuration
    physics: PhysicsConfig = None
    
    # Rendering configuration
    rendering: RenderingConfig = None
    
    # Simulation parameters
    time_step: float = 1.0 / 60.0  # Time step in seconds (60 FPS)
    enable_fixed_substeps: bool = True  # Enable fixed time step substeps
    max_substeps: int = 8  # Maximum number of substeps
    enable_gpu_dynamics: bool = True  # Enable GPU dynamics (if available)
    gpu_max_particles: int = 131072  # Maximum particles for GPU dynamics
    
    # Environment settings
    use_scene_query_api: bool = True  # Enable scene query API
    enable_scene_query_support: bool = True  # Enable scene query support
    
    # Asset paths
    asset_path: str = "/assets"  # Base path for assets
    robot_asset_path: str = "/assets/robots"  # Path for robot assets
    environment_asset_path: str = "/assets/environments"  # Path for environment assets
    
    def __post_init__(self):
        """Initialize nested dataclasses if not provided."""
        if self.physics is None:
            self.physics = PhysicsConfig()
        if self.rendering is None:
            self.rendering = RenderingConfig()


# Default configuration instance
DEFAULT_CONFIG = SimulationConfig()


def get_simulation_config(config_path: Optional[str] = None) -> SimulationConfig:
    """
    Load simulation configuration from file or return default.
    
    Args:
        config_path: Path to configuration file (optional)
        
    Returns:
        SimulationConfig: Loaded configuration or default
    """
    if config_path and os.path.exists(config_path):
        # TODO: Implement config file loading (JSON/YAML)
        pass
    
    return DEFAULT_CONFIG


def get_physics_config() -> PhysicsConfig:
    """Get physics configuration."""
    config = get_simulation_config()
    return config.physics


def get_rendering_config() -> RenderingConfig:
    """Get rendering configuration."""
    config = get_simulation_config()
    return config.rendering