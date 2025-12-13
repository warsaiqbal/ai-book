"""
Perception pipeline data models for the AI-Robot Brain project.

This module defines data structures for perception pipelines that process
sensor data to understand the environment.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum
import json
from src.utils.data_models import (
    BaseEntity, Vector3, PerceptionPipeline as BasePerceptionPipeline,
    PerceptionModel as BasePerceptionModel, SensorData as BaseSensorData,
    PerceptionResult as BasePerceptionResult, SensorType
)


class PipelineStage(Enum):
    """Enumeration of pipeline stages."""
    PREPROCESSING = "preprocessing"
    FEATURE_EXTRACTION = "feature_extraction"
    OBJECT_DETECTION = "object_detection"
    CLASSIFICATION = "classification"
    SEGMENTATION = "segmentation"
    TRACKING = "tracking"
    POSTPROCESSING = "postprocessing"


class ModelFramework(Enum):
    """Enumeration of model frameworks (copied from utils.data_models)."""
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    TENSORRT = "tensorrt"
    ONNX = "onnx"
    OPENVINO = "openvino"
    TRT = "trt"


@dataclass
class ModelInput:
    """Defines the input requirements for a perception model."""
    sensor_type: SensorType
    required_resolution: Optional[tuple] = None  # (width, height)
    required_channels: Optional[int] = None
    preprocessing_steps: List[str] = field(default_factory=list)  # e.g., "normalize", "resize"
    format: str = "tensor"  # "tensor", "image", "pointcloud", etc.


@dataclass
class ModelOutput:
    """Defines the output of a perception model."""
    output_type: str  # "detections", "segmentation", "features", etc.
    output_format: str  # "tensor", "bbox", "mask", etc.
    confidence_threshold: float = 0.5
    output_resolution: Optional[tuple] = None  # (width, height) for image outputs


@dataclass
class PerceptionModel:
    """Enhanced perception model definition."""
    id: str
    name: str
    model_type: str  # "object_detection", "segmentation", "classification", "vslam", etc.
    framework: ModelFramework
    weights_path: str
    input_specs: List[ModelInput] = field(default_factory=list)
    output_specs: List[ModelOutput] = field(default_factory=list)
    input_channels: int = 3
    input_resolution: tuple = (640, 480)  # width, height
    output_format: Dict[str, Any] = field(default_factory=dict)
    accuracy: float = 0.0
    latency: float = 0.0  # in milliseconds
    pipeline_id: Optional[str] = None
    description: Optional[str] = ""
    version: str = "1.0.0"
    license: Optional[str] = None  # License information
    tags: List[str] = field(default_factory=list)  # e.g., ["indoor", "outdoor", "day", "night"]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'model_type': self.model_type,
            'framework': self.framework.value,
            'weights_path': self.weights_path,
            'input_specs': [spec.__dict__ for spec in self.input_specs],
            'output_specs': [spec.__dict__ for spec in self.output_specs],
            'input_channels': self.input_channels,
            'input_resolution': self.input_resolution,
            'output_format': self.output_format,
            'accuracy': self.accuracy,
            'latency': self.latency,
            'pipeline_id': self.pipeline_id,
            'description': self.description,
            'version': self.version,
            'license': self.license,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create from dictionary."""
        # Parse input_specs and output_specs from dict
        input_specs = [ModelInput(**spec) for spec in data.get('input_specs', [])]
        output_specs = [ModelOutput(**spec) for spec in data.get('output_specs', [])]
        
        return cls(
            id=data['id'],
            name=data['name'],
            model_type=data['model_type'],
            framework=ModelFramework(data['framework']),
            weights_path=data['weights_path'],
            input_specs=input_specs,
            output_specs=output_specs,
            input_channels=data.get('input_channels', 3),
            input_resolution=tuple(data.get('input_resolution', (640, 480))),
            output_format=data.get('output_format', {}),
            accuracy=data.get('accuracy', 0.0),
            latency=data.get('latency', 0.0),
            pipeline_id=data.get('pipeline_id'),
            description=data.get('description', ''),
            version=data.get('version', '1.0.0'),
            license=data.get('license'),
            tags=data.get('tags', [])
        )


@dataclass
class PipelineStageConfig:
    """Configuration for a specific stage in the perception pipeline."""
    stage: PipelineStage
    model: PerceptionModel
    input_mapping: Dict[str, str]  # Maps pipeline inputs to stage inputs
    output_mapping: Dict[str, str]  # Maps stage outputs to pipeline outputs
    parameters: Dict[str, Any] = field(default_factory=dict)  # Stage-specific parameters
    enabled: bool = True  # Whether this stage is enabled in the pipeline


@dataclass
class PerceptionResult:
    """Enhanced perception result with additional metadata."""
    id: str
    pipeline_id: str
    sensor_data_id: str
    timestamp: float
    detection_type: str  # "object", "person", "obstacle", "landmark", etc.
    confidence: float
    bounding_box: Optional[List[float]] = None  # [x, y, width, height] or [x1, y1, x2, y2]
    classification: Optional[str] = None  # Classification label
    position: Optional[Vector3] = None  # 3D position in world coordinates
    attributes: Dict[str, Any] = field(default_factory=dict)  # Additional attributes
    validation_status: str = "pending"  # "valid", "invalid", "pending"
    processing_time: Optional[float] = None  # Time taken to process in ms
    model_used: Optional[str] = None  # ID of model that generated this result
    confidence_map: Optional[str] = None  # Path to confidence map if applicable
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            'id': self.id,
            'pipeline_id': self.pipeline_id,
            'sensor_data_id': self.sensor_data_id,
            'timestamp': self.timestamp,
            'detection_type': self.detection_type,
            'confidence': self.confidence,
            'bounding_box': self.bounding_box,
            'classification': self.classification,
            'validation_status': self.validation_status,
            'processing_time': self.processing_time,
            'model_used': self.model_used,
            'confidence_map': self.confidence_map,
            'attributes': self.attributes
        }
        
        if self.position:
            result['position'] = {
                'x': self.position.x,
                'y': self.position.y,
                'z': self.position.z
            }
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create from dictionary."""
        position_data = data.get('position')
        position = None
        if position_data:
            position = Vector3(position_data['x'], position_data['y'], position_data['z'])
        
        return cls(
            id=data['id'],
            pipeline_id=data['pipeline_id'],
            sensor_data_id=data['sensor_data_id'],
            timestamp=data['timestamp'],
            detection_type=data['detection_type'],
            confidence=data['confidence'],
            bounding_box=data.get('bounding_box'),
            classification=data.get('classification'),
            position=position,
            attributes=data.get('attributes', {}),
            validation_status=data.get('validation_status', 'pending'),
            processing_time=data.get('processing_time'),
            model_used=data.get('model_used'),
            confidence_map=data.get('confidence_map')
        )


@dataclass
class PerceptionPipeline(BasePerceptionPipeline):
    """
    Enhanced perception pipeline model with additional functionality for 
    configuring and executing perception tasks.
    """
    # Additional fields beyond the base class
    stages: List[PipelineStageConfig] = field(default_factory=list)
    input_sensors: List[SensorType] = field(default_factory=list)
    output_formats: List[str] = field(default_factory=list)  # "detections", "masks", etc.
    processing_rate: float = 30.0  # Max processing rate in Hz
    robot_model_id: Optional[str] = None
    enabled: bool = True
    description: str = ""
    
    # Performance and optimization
    gpu_enabled: bool = True
    optimization_level: int = 2  # 0=no optimization, 1=FP16, 2=INT8, 3=TRT
    batch_size: int = 1
    
    # Calibration and configuration
    calibration_data_path: Optional[str] = None
    domain_randomization: bool = False
    domain_randomization_config: Dict[str, Any] = field(default_factory=dict)
    
    # Monitoring and logging
    logging_enabled: bool = True
    log_level: str = "info"  # "debug", "info", "warning", "error"
    
    def __post_init__(self):
        """Initialize nested objects if not provided (extend base implementation)."""
        if self.models is None:
            self.models = []
        if self.input_sensors is None:
            self.input_sensors = []
    
    def add_stage(self, stage_config: PipelineStageConfig):
        """Add a stage to the pipeline."""
        self.stages.append(stage_config)
        
        # Also add the model to the base models list if not already there
        if stage_config.model.id not in self.models:
            self.models.append(stage_config.model.id)
    
    def remove_stage(self, stage: PipelineStage):
        """Remove a stage from the pipeline."""
        self.stages = [s for s in self.stages if s.stage != stage]
        
        # Update the models list to reflect changes
        model_ids = [s.model.id for s in self.stages]
        self.models = [mid for mid in self.models if mid in model_ids]
    
    def get_stage_by_type(self, stage_type: PipelineStage) -> Optional[PipelineStageConfig]:
        """Get a specific stage by its type."""
        for stage in self.stages:
            if stage.stage == stage_type:
                return stage
        return None
    
    def configure_for_robot(self, robot_model_id: str):
        """Configure the pipeline for a specific robot model."""
        self.robot_model_id = robot_model_id
        # Additional robot-specific configuration could happen here
    
    def to_config_dict(self) -> Dict[str, Any]:
        """Convert the pipeline to a configuration dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'models': self.models,
            'input_sensors': [s.value for s in self.input_sensors],
            'detection_threshold': self.detection_threshold,
            'bounding_box_format': self.bounding_box_format,
            'processing_rate': self.processing_rate,
            'robot_model_id': self.robot_model_id,
            'enabled': self.enabled,
            'gpu_enabled': self.gpu_enabled,
            'optimization_level': self.optimization_level,
            'batch_size': self.batch_size,
            'calibration_data_path': self.calibration_data_path,
            'domain_randomization': self.domain_randomization,
            'domain_randomization_config': self.domain_randomization_config,
            'logging_enabled': self.logging_enabled,
            'log_level': self.log_level,
            'stages': [stage.to_dict() for stage in self.stages],
            'output_formats': self.output_formats
        }
    
    @classmethod
    def from_config_dict(cls, config_data: Dict[str, Any]):
        """Create a pipeline from a configuration dictionary."""
        # Create basic pipeline instance
        pipeline = cls(
            id=config_data['id'],
            name=config_data['name'],
            description=config_data.get('description', ''),
            models=config_data.get('models', []),
            input_sensors=[SensorType(s) for s in config_data.get('input_sensors', [])],
            detection_threshold=config_data.get('detection_threshold', 0.7),
            bounding_box_format=config_data.get('bounding_box_format', 'xywh'),
            processing_rate=config_data.get('processing_rate', 30.0),
            robot_model_id=config_data.get('robot_model_id'),
            enabled=config_data.get('enabled', True),
            gpu_enabled=config_data.get('gpu_enabled', True),
            optimization_level=config_data.get('optimization_level', 2),
            batch_size=config_data.get('batch_size', 1),
            calibration_data_path=config_data.get('calibration_data_path'),
            domain_randomization=config_data.get('domain_randomization', False),
            domain_randomization_config=config_data.get('domain_randomization_config', {}),
            logging_enabled=config_data.get('logging_enabled', True),
            log_level=config_data.get('log_level', 'info'),
            output_formats=config_data.get('output_formats', [])
        )
        
        # Add stages if they exist in config
        for stage_data in config_data.get('stages', []):
            # This would need to reconstruct PipelineStageConfig objects
            # For now, we'll just add placeholder code
            pass
        
        return pipeline
    
    def validate_pipeline(self) -> List[str]:
        """
        Validate the pipeline configuration and return any issues found.
        
        Returns:
            List of validation issues (empty if all valid)
        """
        issues = []
        
        # Validate that we have at least one stage
        if not self.stages:
            issues.append("Pipeline has no stages configured")
        
        # Validate that input sensors are specified
        if not self.input_sensors:
            issues.append("No input sensors specified for the pipeline")
        
        # Validate that models are specified
        if not self.models:
            issues.append("No models specified for the pipeline")
        
        # Validate processing rate is positive
        if self.processing_rate <= 0:
            issues.append("Processing rate must be positive")
        
        # Validate stage sequence makes sense
        stage_types = [stage.stage for stage in self.stages]
        if PipelineStage.OBJECT_DETECTION in stage_types and PipelineStage.PREPROCESSING not in stage_types:
            # This might be okay, but could be a warning
            pass
        
        return issues


@dataclass
class PipelineExecutionResult:
    """Result of executing a perception pipeline."""
    pipeline_id: str
    execution_id: str
    start_time: float
    end_time: float
    results: List[PerceptionResult]
    input_data_ids: List[str]
    success: bool = True
    error_message: Optional[str] = None
    processing_times: Dict[str, float] = field(default_factory=dict)  # stage -> time in ms
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'pipeline_id': self.pipeline_id,
            'execution_id': self.execution_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'results': [r.to_dict() for r in self.results],
            'input_data_ids': self.input_data_ids,
            'success': self.success,
            'error_message': self.error_message,
            'processing_times': self.processing_times
        }


@dataclass
class SyntheticDataConfig:
    """Configuration for synthetic data generation."""
    domain_randomization: bool = True
    texture_randomization: bool = True
    lighting_randomization: bool = True
    color_randomization: bool = True
    background_randomization: bool = True
    noise_injection: bool = True
    blur_augmentation: bool = False
    scale_augmentation: bool = True
    rotation_augmentation: bool = True
    
    # Domain randomization parameters
    lighting_min_intensity: float = 0.5
    lighting_max_intensity: float = 2.0
    texture_min_shininess: float = 0.0
    texture_max_shininess: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'domain_randomization': self.domain_randomization,
            'texture_randomization': self.texture_randomization,
            'lighting_randomization': self.lighting_randomization,
            'color_randomization': self.color_randomization,
            'background_randomization': self.background_randomization,
            'noise_injection': self.noise_injection,
            'blur_augmentation': self.blur_augmentation,
            'scale_augmentation': self.scale_augmentation,
            'rotation_augmentation': self.rotation_augmentation,
            'lighting_min_intensity': self.lighting_min_intensity,
            'lighting_max_intensity': self.lighting_max_intensity,
            'texture_min_shininess': self.texture_min_shininess,
            'texture_max_shininess': self.texture_max_shininess
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create from dictionary."""
        return cls(
            domain_randomization=data.get('domain_randomization', True),
            texture_randomization=data.get('texture_randomization', True),
            lighting_randomization=data.get('lighting_randomization', True),
            color_randomization=data.get('color_randomization', True),
            background_randomization=data.get('background_randomization', True),
            noise_injection=data.get('noise_injection', True),
            blur_augmentation=data.get('blur_augmentation', False),
            scale_augmentation=data.get('scale_augmentation', True),
            rotation_augmentation=data.get('rotation_augmentation', True),
            lighting_min_intensity=data.get('lighting_min_intensity', 0.5),
            lighting_max_intensity=data.get('lighting_max_intensity', 2.0),
            texture_min_shininess=data.get('texture_min_shininess', 0.0),
            texture_max_shininess=data.get('texture_max_shininess', 1.0)
        )