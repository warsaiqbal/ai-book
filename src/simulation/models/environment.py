"""
Specialized data models for the simulation environment based on the 
base models defined in utils.data_models.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
from src.utils.data_models import (
    BaseEntity, Vector3, SimulatedEnvironment as BaseSimulatedEnvironment,
    RobotModel, Sensor
)


@dataclass
class PhysicsProperties:
    """Specific physics properties for the simulation environment."""
    gravity: Vector3 = field(default_factory=lambda: Vector3(0.0, 0.0, -9.81))
    solver_type: str = "pgs"  # Physics solver type: pgs, tgs
    solver_iterations: int = 128
    enable_ccd: bool = False
    friction_model: str = "box"
    restitution_threshold: float = 2.0
    enable_gpu_dynamics: bool = True
    gpu_max_particles: int = 131072

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for serialization."""
        return {
            'gravity': {'x': self.gravity.x, 'y': self.gravity.y, 'z': self.gravity.z},
            'solver_type': self.solver_type,
            'solver_iterations': self.solver_iterations,
            'enable_ccd': self.enable_ccd,
            'friction_model': self.friction_model,
            'restitution_threshold': self.restitution_threshold,
            'enable_gpu_dynamics': self.enable_gpu_dynamics,
            'gpu_max_particles': self.gpu_max_particles
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create instance from a dictionary."""
        gravity_data = data.get('gravity', {'x': 0.0, 'y': 0.0, 'z': -9.81})
        gravity = Vector3(gravity_data['x'], gravity_data['y'], gravity_data['z'])
        
        return cls(
            gravity=gravity,
            solver_type=data.get('solver_type', 'pgs'),
            solver_iterations=data.get('solver_iterations', 128),
            enable_ccd=data.get('enable_ccd', False),
            friction_model=data.get('friction_model', 'box'),
            restitution_threshold=data.get('restitution_threshold', 2.0),
            enable_gpu_dynamics=data.get('enable_gpu_dynamics', True),
            gpu_max_particles=data.get('gpu_max_particles', 131072)
        )


@dataclass
class EnvironmentAsset:
    """Represents an asset in the simulation environment."""
    id: str
    name: str
    asset_type: str  # 'static', 'dynamic', 'decoration', etc.
    position: Vector3 = field(default_factory=Vector3)
    orientation: float = 0.0  # Yaw rotation in radians
    scale: Vector3 = field(default_factory=lambda: Vector3(1.0, 1.0, 1.0))
    asset_path: Optional[str] = None
    is_interactable: bool = False
    mass: Optional[float] = None
    physical_properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'asset_type': self.asset_type,
            'position': {'x': self.position.x, 'y': self.position.y, 'z': self.position.z},
            'orientation': self.orientation,
            'scale': {'x': self.scale.x, 'y': self.scale.y, 'z': self.scale.z},
            'asset_path': self.asset_path,
            'is_interactable': self.is_interactable,
            'mass': self.mass,
            'physical_properties': self.physical_properties
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create instance from a dictionary."""
        pos_data = data.get('position', {'x': 0.0, 'y': 0.0, 'z': 0.0})
        position = Vector3(pos_data['x'], pos_data['y'], pos_data['z'])
        
        scale_data = data.get('scale', {'x': 1.0, 'y': 1.0, 'z': 1.0})
        scale = Vector3(scale_data['x'], scale_data['y'], scale_data['z'])
        
        return cls(
            id=data['id'],
            name=data['name'],
            asset_type=data['asset_type'],
            position=position,
            orientation=data.get('orientation', 0.0),
            scale=scale,
            asset_path=data.get('asset_path'),
            is_interactable=data.get('is_interactable', False),
            mass=data.get('mass'),
            physical_properties=data.get('physical_properties', {})
        )


@dataclass
class LightingConfiguration:
    """Configuration for lighting in the simulation environment."""
    main_light_intensity: float = 1000.0
    main_light_color: List[float] = field(default_factory=lambda: [1.0, 1.0, 1.0])  # RGB [0-1]
    ambient_light_intensity: float = 200.0
    shadows_enabled: bool = True
    shadow_resolution: int = 2048
    environment_map_path: Optional[str] = None
    time_of_day: float = 12.0  # 0-24 hour format

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for serialization."""
        return {
            'main_light_intensity': self.main_light_intensity,
            'main_light_color': self.main_light_color,
            'ambient_light_intensity': self.ambient_light_intensity,
            'shadows_enabled': self.shadows_enabled,
            'shadow_resolution': self.shadow_resolution,
            'environment_map_path': self.environment_map_path,
            'time_of_day': self.time_of_day
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create instance from a dictionary."""
        return cls(
            main_light_intensity=data.get('main_light_intensity', 1000.0),
            main_light_color=data.get('main_light_color', [1.0, 1.0, 1.0]),
            ambient_light_intensity=data.get('ambient_light_intensity', 200.0),
            shadows_enabled=data.get('shadows_enabled', True),
            shadow_resolution=data.get('shadow_resolution', 2048),
            environment_map_path=data.get('environment_map_path'),
            time_of_day=data.get('time_of_day', 12.0)
        )


@dataclass
class SimulatedEnvironment(BaseSimulatedEnvironment):
    """
    Specialized simulation environment model with additional fields specific to Isaac Sim.
    
    Extends the base SimulatedEnvironment with Isaac Sim specific properties.
    """
    # Additional Isaac Sim specific properties
    isaac_env_path: Optional[str] = None
    enable_fabric: bool = True
    enable_scene_query_support: bool = True
    enable_gfx_renders: bool = True
    enable_immediate_stacking: bool = True
    
    # Store specialized objects instead of base types
    physics_properties_obj: Optional[PhysicsProperties] = None
    lighting_config_obj: Optional[LightingConfiguration] = None
    assets_obj: List[EnvironmentAsset] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize objects if not provided."""
        super().__post_init__()  # Call parent __post_init__
        
        if self.physics_properties_obj is None:
            # Convert dict to object if physics_properties is a dict, otherwise create default
            if self.physics_properties:
                self.physics_properties_obj = PhysicsProperties.from_dict(self.physics_properties)
            else:
                self.physics_properties_obj = PhysicsProperties()
        
        if self.lighting_config_obj is None:
            # Create default lighting configuration
            self.lighting_config_obj = LightingConfiguration()
            
        if not self.assets_obj and self.assets:
            # Convert assets list if it exists as base format
            for asset_data in self.assets:
                if isinstance(asset_data, dict):
                    self.assets_obj.append(EnvironmentAsset.from_dict(asset_data))
        
        # Ensure assets is always a list of objects
        if self.assets is None:
            self.assets = []
    
    def add_asset(self, asset: EnvironmentAsset):
        """Add an asset to the environment."""
        self.assets_obj.append(asset)
        # Also update the base assets list for compatibility
        self.assets.append(asset.to_dict())
    
    def remove_asset(self, asset_id: str):
        """Remove an asset from the environment by ID."""
        self.assets_obj = [asset for asset in self.assets_obj if asset.id != asset_id]
        self.assets = [asset for asset in self.assets if asset.get('id') != asset_id]
    
    def add_robot(self, robot: RobotModel):
        """Add a robot to the environment (update the base class relationship)."""
        # This would be handled by the base class relationship
        
    def add_sensor(self, sensor: Sensor):
        """Add a sensor to the environment (update the base class relationship)."""
        # This would be handled by the base class relationship
    
    def get_asset_by_id(self, asset_id: str) -> Optional[EnvironmentAsset]:
        """Get an asset by its ID."""
        for asset in self.assets_obj:
            if asset.id == asset_id:
                return asset
        return None
    
    def to_config_dict(self) -> Dict[str, Any]:
        """Convert the environment to a configuration dictionary suitable for Isaac Sim."""
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description,
            'dimensions': {
                'x': self.dimensions.x,
                'y': self.dimensions.y,
                'z': self.dimensions.z
            },
            'physics': self.physics_properties_obj.to_dict() if self.physics_properties_obj else {},
            'lighting': self.lighting_config_obj.to_dict() if self.lighting_config_obj else {},
            'assets': [asset.to_dict() for asset in self.assets_obj],
            'isaac_env_path': self.isaac_env_path,
            'enable_fabric': self.enable_fabric,
            'enable_scene_query_support': self.enable_scene_query_support,
            'enable_gfx_renders': self.enable_gfx_renders,
            'enable_immediate_stacking': self.enable_immediate_stacking
        }
    
    @classmethod
    def from_config_dict(cls, config_data: Dict[str, Any]):
        """Create an environment from a configuration dictionary."""
        # Extract base properties
        name = config_data.get('name', 'unnamed')
        env_id = config_data.get('id', f'env_{hash(str(config_data)) % 10000}')
        description = config_data.get('description', '')
        
        # Create dimensions
        dims_data = config_data.get('dimensions', {'x': 10.0, 'y': 10.0, 'z': 3.0})
        dimensions = Vector3(dims_data['x'], dims_data['y'], dims_data['z'])
        
        # Create instance
        env = cls(
            id=env_id,
            name=name,
            description=description,
            dimensions=dimensions
        )
        
        # Set Isaac-specific properties
        env.isaac_env_path = config_data.get('isaac_env_path')
        env.enable_fabric = config_data.get('enable_fabric', True)
        env.enable_scene_query_support = config_data.get('enable_scene_query_support', True)
        env.enable_gfx_renders = config_data.get('enable_gfx_renders', True)
        env.enable_immediate_stacking = config_data.get('enable_immediate_stacking', True)
        
        # Set physics properties
        if 'physics' in config_data:
            env.physics_properties_obj = PhysicsProperties.from_dict(config_data['physics'])
        
        # Set lighting configuration
        if 'lighting' in config_data:
            env.lighting_config_obj = LightingConfiguration.from_dict(config_data['lighting'])
        
        # Set assets
        if 'assets' in config_data:
            for asset_data in config_data['assets']:
                env.assets_obj.append(EnvironmentAsset.from_dict(asset_data))
        
        return env
    
    def save_to_file(self, file_path: str):
        """Save the environment configuration to a file."""
        import json
        
        config = self.to_config_dict()
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: str):
        """Load the environment configuration from a file."""
        import json
        
        with open(file_path, 'r') as f:
            config = json.load(f)
        
        return cls.from_config_dict(config)


# Additional specialized classes for simulation-specific functionality

@dataclass
class SimulationState:
    """Represents the current state of a simulation run."""
    environment_id: str
    timestamp: float
    simulation_time: float
    robots_state: Dict[str, Dict[str, Any]]  # robot_id -> state_dict
    sensor_data: Dict[str, Any]  # sensor_id -> data
    physics_stats: Dict[str, float]  # Various physics performance metrics
    rendering_stats: Dict[str, float]  # Rendering performance metrics
    is_paused: bool = False
    is_complete: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'environment_id': self.environment_id,
            'timestamp': self.timestamp,
            'simulation_time': self.simulation_time,
            'robots_state': self.robots_state,
            'sensor_data': self.sensor_data,
            'physics_stats': self.physics_stats,
            'rendering_stats': self.rendering_stats,
            'is_paused': self.is_paused,
            'is_complete': self.is_complete
        }

@dataclass
class SimulationRunConfiguration:
    """Configuration for a specific simulation run."""
    environment: SimulatedEnvironment
    robot_models: List[RobotModel]
    initial_conditions: Dict[str, Any] = field(default_factory=dict)
    run_duration: float = 60.0  # seconds
    time_step: float = 1.0/60.0  # seconds
    record_data: bool = True
    record_video: bool = False
    random_seed: Optional[int] = None
    scenario_description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'environment': self.environment.to_config_dict(),
            'robot_models': [robot.to_dict() for robot in self.robot_models],
            'initial_conditions': self.initial_conditions,
            'run_duration': self.run_duration,
            'time_step': self.time_step,
            'record_data': self.record_data,
            'record_video': self.record_video,
            'random_seed': self.random_seed,
            'scenario_description': self.scenario_description
        }