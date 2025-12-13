"""
Physics configuration for Isaac Sim environments based on the 
physics configuration defined in the environment data model.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from pathlib import Path
import json
from src.simulation.models.environment import PhysicsProperties


@dataclass
class SimulationPhysicsConfig:
    """
    Comprehensive physics configuration for Isaac Sim environments.
    
    This class extends the PhysicsProperties with additional simulation-specific
    parameters for Isaac Sim.
    """
    # Basic physics properties (from PhysicsProperties)
    gravity: tuple = field(default_factory=lambda: (0.0, 0.0, -9.81))  # Gravity vector (x, y, z) in m/s^2
    solver_type: str = "pgs"  # Physics solver type: pgs (Projected Gauss-Seidel) or tgs (Tensor Gauss-Seidel)
    solver_iterations: int = 128  # Number of solver iterations
    enable_ccd: bool = False  # Enable continuous collision detection
    friction_model: str = "box"  # Friction model: box, cone, or none
    restitution_threshold: float = 2.0  # Restitution threshold in m/s
    enable_gpu_dynamics: bool = True  # Enable GPU dynamics (if available)
    gpu_max_particles: int = 131072  # Maximum particles for GPU dynamics

    # Isaac Sim specific parameters
    enable_stabilization: bool = True  # Enable simulation stabilization
    stabilization_threshold: float = 0.01  # Stabilization threshold
    sleep_threshold: float = 1e-5  # Sleep threshold for inactive bodies
    stabilization_callback: bool = True  # Use stabilization callback
    
    # Contact handling
    enable_contact_graph: bool = True  # Enable contact graph for efficient contact handling
    enable_edge_mode: bool = True  # Enable edge mode for better contact detection
    contact_correlation_distance: float = 0.002  # Distance to correlate contacts
    
    # Broad phase parameters
    broadphase_type: str = "scene_query"  # Broadphase algorithm: scene_query, sweep_and_prune, multi_sap
    enable_enhanced_determinism: bool = False  # Enable enhanced determinism (may impact performance)
    
    # Scene parameters
    scene_query_resolution: int = 512  # Resolution for scene queries (raycasting, etc.)
    enable_scene_query_api: bool = True  # Enable scene query API
    enable_scene_query_support: bool = True  # Enable scene query support
    
    # Collision parameters
    enable_fluid_implicit_cors: bool = False  # Enable fluid implicit coordinates of restitution
    enable_sleep_angular_velocity: float = 0.1  # Angular velocity threshold for sleeping
    enable_sleep_linear_velocity: float = 0.1  # Linear velocity threshold for sleeping
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for serialization."""
        return {
            'gravity': self.gravity,
            'solver_type': self.solver_type,
            'solver_iterations': self.solver_iterations,
            'enable_ccd': self.enable_ccd,
            'friction_model': self.friction_model,
            'restitution_threshold': self.restitution_threshold,
            'enable_gpu_dynamics': self.enable_gpu_dynamics,
            'gpu_max_particles': self.gpu_max_particles,
            'enable_stabilization': self.enable_stabilization,
            'stabilization_threshold': self.stabilization_threshold,
            'sleep_threshold': self.sleep_threshold,
            'stabilization_callback': self.stabilization_callback,
            'enable_contact_graph': self.enable_contact_graph,
            'enable_edge_mode': self.enable_edge_mode,
            'contact_correlation_distance': self.contact_correlation_distance,
            'broadphase_type': self.broadphase_type,
            'enable_enhanced_determinism': self.enable_enhanced_determinism,
            'scene_query_resolution': self.scene_query_resolution,
            'enable_scene_query_api': self.enable_scene_query_api,
            'enable_scene_query_support': self.enable_scene_query_support,
            'enable_fluid_implicit_cors': self.enable_fluid_implicit_cors,
            'enable_sleep_angular_velocity': self.enable_sleep_angular_velocity,
            'enable_sleep_linear_velocity': self.enable_sleep_linear_velocity
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create instance from a dictionary."""
        return cls(
            gravity=tuple(data.get('gravity', (0.0, 0.0, -9.81))),
            solver_type=data.get('solver_type', 'pgs'),
            solver_iterations=data.get('solver_iterations', 128),
            enable_ccd=data.get('enable_ccd', False),
            friction_model=data.get('friction_model', 'box'),
            restitution_threshold=data.get('restitution_threshold', 2.0),
            enable_gpu_dynamics=data.get('enable_gpu_dynamics', True),
            gpu_max_particles=data.get('gpu_max_particles', 131072),
            enable_stabilization=data.get('enable_stabilization', True),
            stabilization_threshold=data.get('stabilization_threshold', 0.01),
            sleep_threshold=data.get('sleep_threshold', 1e-5),
            stabilization_callback=data.get('stabilization_callback', True),
            enable_contact_graph=data.get('enable_contact_graph', True),
            enable_edge_mode=data.get('enable_edge_mode', True),
            contact_correlation_distance=data.get('contact_correlation_distance', 0.002),
            broadphase_type=data.get('broadphase_type', 'scene_query'),
            enable_enhanced_determinism=data.get('enable_enhanced_determinism', False),
            scene_query_resolution=data.get('scene_query_resolution', 512),
            enable_scene_query_api=data.get('enable_scene_query_api', True),
            enable_scene_query_support=data.get('enable_scene_query_support', True),
            enable_fluid_implicit_cors=data.get('enable_fluid_implicit_cors', False),
            enable_sleep_angular_velocity=data.get('enable_sleep_angular_velocity', 0.1),
            enable_sleep_linear_velocity=data.get('enable_sleep_linear_velocity', 0.1)
        )

    def to_physics_properties(self) -> PhysicsProperties:
        """Convert to a PhysicsProperties object for use in environment models."""
        from src.utils.data_models import Vector3
        gravity_vec = Vector3(*self.gravity)
        
        return PhysicsProperties(
            gravity=gravity_vec,
            solver_type=self.solver_type,
            solver_iterations=self.solver_iterations,
            enable_ccd=self.enable_ccd,
            friction_model=self.friction_model,
            restitution_threshold=self.restitution_threshold,
            enable_gpu_dynamics=self.enable_gpu_dynamics,
            gpu_max_particles=self.gpu_max_particles
        )


@dataclass
class RigidBodyConfig:
    """Configuration for a rigid body in the physics simulation."""
    mass: float = 1.0
    linear_damping: float = 0.05  # Damping for linear motion
    angular_damping: float = 0.05  # Damping for angular motion
    max_linear_velocity: float = 1000.0  # Maximum linear velocity
    max_angular_velocity: float = 1000.0  # Maximum angular velocity
    max_depenetration_velocity: float = 100.0  # Maximum depenetration velocity
    enable_gyroscopic_forces: bool = True  # Enable gyroscopic forces
    sleep_threshold: float = 1e-5  # Sleeping threshold
    stabilization_threshold: float = 0.05  # Stabilization threshold
    use_local_pose: bool = False  # Use local pose for kinematic bodies
    solver_position_iteration_count: int = 4  # Position iterations for the solver
    solver_velocity_iteration_count: int = 1  # Velocity iterations for the solver
    contact_report_threshold: float = 1e+30  # Threshold for contact reports
    orientation: str = "default"  # Orientation mode: default, no_gravity, or kinematic


@dataclass
class MaterialConfig:
    """Configuration for a physics material."""
    static_friction: float = 0.5
    dynamic_friction: float = 0.5
    restitution: float = 0.1
    friction_combine_mode: str = "average"  # average, min, multiply, or max
    restitution_combine_mode: str = "average"  # average, min, multiply, or max


@dataclass
class SceneConfig:
    """Configuration for the physics scene."""
    # Scene parameters
    gravity: tuple = field(default_factory=lambda: (0.0, 0.0, -9.81))
    simulation_dt: float = 1.0/60.0  # Simulation time step
    substeps: int = 1  # Number of substeps per simulation step
    enable_ccd: bool = False  # Enable continuous collision detection
    ccd_threshold: float = 1e-7  # CCD threshold
    enable_pbd: bool = False  # Enable position-based dynamics
    enable_gpu: bool = True  # Enable GPU acceleration
    
    # Scene query parameters
    scene_query_resolution: int = 512  # Resolution for scene queries
    enable_scene_queries: bool = True  # Enable scene query functionality
    
    # Solver parameters
    solver_type: str = "pgs"  # Solver type: pgs or tgs
    solver_iterations: int = 128
    velocity_iterations: int = 1
    position_iterations: int = 4


@dataclass
class PhysicsScene:
    """Complete physics scene configuration combining all physics elements."""
    name: str
    config: SimulationPhysicsConfig
    rigid_body_configs: Dict[str, RigidBodyConfig] = field(default_factory=dict)
    material_configs: Dict[str, MaterialConfig] = field(default_factory=dict)
    
    def add_rigid_body_config(self, name: str, config: RigidBodyConfig):
        """Add a rigid body configuration."""
        self.rigid_body_configs[name] = config
    
    def add_material_config(self, name: str, config: MaterialConfig):
        """Add a material configuration."""
        self.material_configs[name] = config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the entire physics scene to a dictionary."""
        result = {
            'name': self.name,
            'config': self.config.to_dict(),
            'rigid_body_configs': {name: config.to_dict() for name, config in self.rigid_body_configs.items()},
            'material_configs': {name: config.to_dict() for name, config in self.material_configs.items()}
        }
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create a PhysicsScene from a dictionary."""
        config = SimulationPhysicsConfig.from_dict(data['config'])
        
        scene = cls(
            name=data['name'],
            config=config
        )
        
        # Add rigid body configs
        for name, rb_data in data.get('rigid_body_configs', {}).items():
            scene.add_rigid_body_config(name, RigidBodyConfig(**rb_data))
        
        # Add material configs
        for name, mat_data in data.get('material_configs', {}).items():
            scene.add_material_config(name, MaterialConfig(**mat_data))
        
        return scene
    
    def save_to_file(self, file_path: str):
        """Save the physics scene configuration to a file."""
        config_dict = self.to_dict()
        with open(file_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: str):
        """Load the physics scene configuration from a file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


# Default physics configuration presets
def get_default_physics_config() -> SimulationPhysicsConfig:
    """Get a default physics configuration suitable for most simulations."""
    return SimulationPhysicsConfig()


def get_high_fidelity_physics_config() -> SimulationPhysicsConfig:
    """Get a high-fidelity physics configuration with more accurate but slower simulation."""
    return SimulationPhysicsConfig(
        solver_iterations=256,
        enable_ccd=True,
        stabilization_threshold=0.001,
        sleep_threshold=1e-6,
        scene_query_resolution=1024,
        enable_enhanced_determinism=True,
        broadphase_type="multi_sap"
    )


def get_performance_physics_config() -> SimulationPhysicsConfig:
    """Get a performance-oriented physics configuration with faster but less accurate simulation."""
    return SimulationPhysicsConfig(
        solver_iterations=64,
        enable_ccd=False,
        stabilization_threshold=0.05,
        sleep_threshold=1e-4,
        scene_query_resolution=256,
        enable_gpu_dynamics=True,
        enable_fluid_implicit_cors=False
    )


# Physics configuration utilities
def validate_physics_config(config: SimulationPhysicsConfig) -> Dict[str, str]:
    """
    Validate physics configuration parameters and return any issues found.
    
    Args:
        config: Physics configuration to validate
        
    Returns:
        Dictionary of validation issues (empty if all valid)
    """
    issues = {}
    
    # Validate gravity
    if len(config.gravity) != 3:
        issues['gravity'] = "Gravity must be a 3-tuple (x, y, z)"
    else:
        for i, g in enumerate(config.gravity):
            if not isinstance(g, (int, float)):
                issues[f'gravity[{i}]'] = f"Gravity component {i} must be a number"
    
    # Validate solver iterations
    if config.solver_iterations <= 0:
        issues['solver_iterations'] = "Solver iterations must be positive"
    
    # Validate GPU particles
    if config.gpu_max_particles <= 0:
        issues['gpu_max_particles'] = "GPU max particles must be positive"
    
    # Validate thresholds
    if config.stabilization_threshold <= 0:
        issues['stabilization_threshold'] = "Stabilization threshold must be positive"
    
    if config.sleep_threshold <= 0:
        issues['sleep_threshold'] = "Sleep threshold must be positive"
    
    # Validate contact correlation distance
    if config.contact_correlation_distance <= 0:
        issues['contact_correlation_distance'] = "Contact correlation distance must be positive"
    
    # Validate scene query resolution
    if config.scene_query_resolution <= 0:
        issues['scene_query_resolution'] = "Scene query resolution must be positive"
    elif config.scene_query_resolution & (config.scene_query_resolution - 1) != 0:
        # Check if it's a power of 2 (often preferred for graphics)
        pass  # We'll just warn, not fail
    
    return issues