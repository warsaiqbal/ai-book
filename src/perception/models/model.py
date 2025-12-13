"""
Perception model data models for the AI-Robot Brain project.

This module defines data structures for individual perception models
that can be used in perception pipelines.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum
import json
from src.perception.models.pipeline import ModelFramework, ModelInput, ModelOutput


class ModelType(Enum):
    """Enumeration of model types."""
    OBJECT_DETECTION = "object_detection"
    INSTANCE_SEGMENTATION = "instance_segmentation"
    SEMANTIC_SEGMENTATION = "semantic_segmentation"
    CLASSIFICATION = "classification"
    VSLAM = "vslam"
    POSE_ESTIMATION = "pose_estimation"
    DEPTH_ESTIMATION = "depth_estimation"
    OCR = "ocr"
    ANOMALY_DETECTION = "anomaly_detection"


class ModelStatus(Enum):
    """Enumeration of model statuses."""
    DRAFT = "draft"
    TRAINING = "training"
    VALIDATION = "validation"
    TESTING = "testing"
    DEPLOYED = "deployed"
    DEPRECATED = "deprecated"


class ModelPrecision(Enum):
    """Enumeration of model precision formats."""
    FP32 = "fp32"
    FP16 = "fp16"
    INT8 = "int8"
    BINARY = "binary"


@dataclass
class ModelMetadata:
    """Metadata for a perception model."""
    created_by: str
    created_at: str  # ISO format datetime string
    last_modified_by: str
    last_modified_at: str  # ISO format datetime string
    version: str = "1.0.0"
    source_code_repo: Optional[str] = None
    training_data_description: Optional[str] = None
    evaluation_metrics: Dict[str, float] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)  # e.g., ["indoor", "outdoor", "day", "night"]


@dataclass
class ModelArchitecture:
    """Details about the model architecture."""
    name: str  # e.g., "YOLOv5", "ResNet50", "EfficientNet-B0"
    backbone: str  # e.g., "ResNet", "EfficientNet", "VisionTransformer"
    input_size: tuple  # (height, width, channels)
    num_classes: int
    anchors: Optional[List[List[float]]] = None  # For detection models
    heads: Optional[List[str]] = None  # e.g., ["classification", "detection", "segmentation"]
    layers: Optional[List[Dict[str, Any]]] = field(default_factory=list)  # Layer definitions
    parameters_count: Optional[int] = None  # Number of parameters


@dataclass
class TrainingConfiguration:
    """Configuration for model training."""
    epochs: int = 100
    batch_size: int = 32
    learning_rate: float = 0.001
    optimizer: str = "adam"  # "sgd", "adam", "rmsprop", etc.
    loss_function: str = "cross_entropy"  # "mse", "cross_entropy", "focal_loss", etc.
    scheduler: Optional[str] = None  # "step", "cosine", "exponential", etc.
    scheduler_params: Dict[str, Any] = field(default_factory=dict)
    augmentation_config: Dict[str, Any] = field(default_factory=dict)
    validation_split: float = 0.2
    test_split: float = 0.1
    early_stopping: bool = True
    early_stopping_patience: int = 10
    checkpoint_interval: int = 10  # Save checkpoint every N epochs


@dataclass
class ModelPerformance:
    """Performance metrics for the model."""
    inference_time_ms: float = 0.0  # Inference time in milliseconds
    power_consumption_w: Optional[float] = None  # Power consumption in watts
    memory_usage_mb: Optional[float] = None  # Peak memory usage in MB
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    mAP: Optional[float] = None  # Mean Average Precision (for detection)
    IoU: Optional[float] = None  # Intersection over Union (for segmentation)
    fps: Optional[float] = None  # Frames per second processing rate


@dataclass
class PerceptionModel:
    """Enhanced perception model with comprehensive configuration."""
    # Core identification
    id: str
    name: str
    model_type: ModelType
    framework: ModelFramework
    description: str = ""
    status: ModelStatus = ModelStatus.DRAFT
    
    # Model details
    architecture: ModelArchitecture = field(default_factory=ModelArchitecture)
    metadata: ModelMetadata = field(default_factory=lambda: 
        ModelMetadata(
            created_by="system", 
            created_at=datetime.now().isoformat(),
            last_modified_by="system", 
            last_modified_at=datetime.now().isoformat()
        )
    )
    weights_path: Optional[str] = None
    config_path: Optional[str] = None
    
    # Performance and optimization
    precision: ModelPrecision = ModelPrecision.FP32
    optimized_for_hardware: Optional[str] = None  # "jetson", "xavier", "gpu", etc.
    performance_metrics: ModelPerformance = field(default_factory=ModelPerformance)
    
    # Data requirements
    input_specs: List[ModelInput] = field(default_factory=list)
    output_specs: List[ModelOutput] = field(default_factory=list)
    
    # Training information
    training_config: TrainingConfiguration = field(default_factory=TrainingConfiguration)
    trained_on_datasets: List[str] = field(default_factory=list)
    trained_with_synthetic_data: bool = False
    synthetic_data_ratio: float = 0.0  # Ratio of synthetic to real data used in training
    
    # Deployment information
    compatible_pipelines: List[str] = field(default_factory=list)
    required_memory_mb: Optional[int] = None
    recommended_hardware: Optional[str] = None  # "gpu", "cpu", "tpu", "edge", etc.
    
    # Validation and evaluation
    evaluation_results: Dict[str, float] = field(default_factory=dict)  # e.g., {"mAP": 0.75, "accuracy": 0.92}
    validation_dataset: Optional[str] = None
    validation_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Version management
    version: str = "1.0.0"
    trained_at: Optional[str] = None  # ISO format datetime string
    parent_model_id: Optional[str] = None  # For models derived from others
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            'id': self.id,
            'name': self.name,
            'model_type': self.model_type.value,
            'framework': self.framework.value,
            'description': self.description,
            'status': self.status.value,
            
            # Architecture and metadata
            'architecture': {
                'name': self.architecture.name,
                'backbone': self.architecture.backbone,
                'input_size': self.architecture.input_size,
                'num_classes': self.architecture.num_classes,
                'anchors': self.architecture.anchors,
                'heads': self.architecture.heads,
                'layers': self.architecture.layers,
                'parameters_count': self.architecture.parameters_count
            },
            'metadata': {
                'created_by': self.metadata.created_by,
                'created_at': self.metadata.created_at,
                'last_modified_by': self.metadata.last_modified_by,
                'last_modified_at': self.metadata.last_modified_at,
                'version': self.metadata.version,
                'source_code_repo': self.metadata.source_code_repo,
                'training_data_description': self.metadata.training_data_description,
                'evaluation_metrics': self.metadata.evaluation_metrics,
                'tags': self.metadata.tags
            },
            
            # Model files
            'weights_path': self.weights_path,
            'config_path': self.config_path,
            
            # Performance and optimization
            'precision': self.precision.value,
            'optimized_for_hardware': self.optimized_for_hardware,
            'performance_metrics': {
                'inference_time_ms': self.performance_metrics.inference_time_ms,
                'power_consumption_w': self.performance_metrics.power_consumption_w,
                'memory_usage_mb': self.performance_metrics.memory_usage_mb,
                'accuracy': self.performance_metrics.accuracy,
                'precision': self.performance_metrics.precision,
                'recall': self.performance_metrics.recall,
                'f1_score': self.performance_metrics.f1_score,
                'mAP': self.performance_metrics.mAP,
                'IoU': self.performance_metrics.IoU,
                'fps': self.performance_metrics.fps
            },
            
            # Data requirements
            'input_specs': [spec.__dict__ for spec in self.input_specs],
            'output_specs': [spec.__dict__ for spec in self.output_specs],
            
            # Training information
            'training_config': {
                'epochs': self.training_config.epochs,
                'batch_size': self.training_config.batch_size,
                'learning_rate': self.training_config.learning_rate,
                'optimizer': self.training_config.optimizer,
                'loss_function': self.training_config.loss_function,
                'scheduler': self.training_config.scheduler,
                'scheduler_params': self.training_config.scheduler_params,
                'augmentation_config': self.training_config.augmentation_config,
                'validation_split': self.training_config.validation_split,
                'test_split': self.training_config.test_split,
                'early_stopping': self.training_config.early_stopping,
                'early_stopping_patience': self.training_config.early_stopping_patience,
                'checkpoint_interval': self.training_config.checkpoint_interval
            },
            'trained_on_datasets': self.trained_on_datasets,
            'trained_with_synthetic_data': self.trained_with_synthetic_data,
            'synthetic_data_ratio': self.synthetic_data_ratio,
            
            # Deployment information
            'compatible_pipelines': self.compatible_pipelines,
            'required_memory_mb': self.required_memory_mb,
            'recommended_hardware': self.recommended_hardware,
            
            # Validation and evaluation
            'evaluation_results': self.evaluation_results,
            'validation_dataset': self.validation_dataset,
            'validation_metrics': self.validation_metrics,
            
            # Version management
            'version': self.version,
            'trained_at': self.trained_at,
            'parent_model_id': self.parent_model_id
        }
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create from dictionary."""
        # Reconstruct architecture
        arch_data = data['architecture']
        architecture = ModelArchitecture(
            name=arch_data['name'],
            backbone=arch_data['backbone'],
            input_size=tuple(arch_data['input_size']),
            num_classes=arch_data['num_classes'],
            anchors=arch_data.get('anchors'),
            heads=arch_data.get('heads'),
            layers=arch_data.get('layers', []),
            parameters_count=arch_data.get('parameters_count')
        )
        
        # Reconstruct metadata
        meta_data = data['metadata']
        metadata = ModelMetadata(
            created_by=meta_data['created_by'],
            created_at=meta_data['created_at'],
            last_modified_by=meta_data['last_modified_by'],
            last_modified_at=meta_data['last_modified_at'],
            version=meta_data.get('version', '1.0.0'),
            source_code_repo=meta_data.get('source_code_repo'),
            training_data_description=meta_data.get('training_data_description'),
            evaluation_metrics=meta_data.get('evaluation_metrics', {}),
            tags=meta_data.get('tags', [])
        )
        
        # Reconstruct performance metrics
        perf_data = data['performance_metrics']
        performance_metrics = ModelPerformance(
            inference_time_ms=perf_data.get('inference_time_ms', 0.0),
            power_consumption_w=perf_data.get('power_consumption_w'),
            memory_usage_mb=perf_data.get('memory_usage_mb'),
            accuracy=perf_data.get('accuracy'),
            precision=perf_data.get('precision'),
            recall=perf_data.get('recall'),
            f1_score=perf_data.get('f1_score'),
            mAP=perf_data.get('mAP'),
            IoU=perf_data.get('IoU'),
            fps=perf_data.get('fps')
        )
        
        # Reconstruct training config
        train_data = data['training_config']
        training_config = TrainingConfiguration(
            epochs=train_data.get('epochs', 100),
            batch_size=train_data.get('batch_size', 32),
            learning_rate=train_data.get('learning_rate', 0.001),
            optimizer=train_data.get('optimizer', 'adam'),
            loss_function=train_data.get('loss_function', 'cross_entropy'),
            scheduler=train_data.get('scheduler'),
            scheduler_params=train_data.get('scheduler_params', {}),
            augmentation_config=train_data.get('augmentation_config', {}),
            validation_split=train_data.get('validation_split', 0.2),
            test_split=train_data.get('test_split', 0.1),
            early_stopping=train_data.get('early_stopping', True),
            early_stopping_patience=train_data.get('early_stopping_patience', 10),
            checkpoint_interval=train_data.get('checkpoint_interval', 10)
        )
        
        # Create and return the model instance
        return cls(
            id=data['id'],
            name=data['name'],
            model_type=ModelType(data['model_type']),
            framework=ModelFramework(data['framework']),
            description=data.get('description', ''),
            status=ModelStatus(data['status']),
            architecture=architecture,
            metadata=metadata,
            weights_path=data.get('weights_path'),
            config_path=data.get('config_path'),
            precision=ModelPrecision(data.get('precision', 'fp32')),
            optimized_for_hardware=data.get('optimized_for_hardware'),
            performance_metrics=performance_metrics,
            input_specs=[ModelInput(**spec) for spec in data.get('input_specs', [])],
            output_specs=[ModelOutput(**spec) for spec in data.get('output_specs', [])],
            training_config=training_config,
            trained_on_datasets=data.get('trained_on_datasets', []),
            trained_with_synthetic_data=data.get('trained_with_synthetic_data', False),
            synthetic_data_ratio=data.get('synthetic_data_ratio', 0.0),
            compatible_pipelines=data.get('compatible_pipelines', []),
            required_memory_mb=data.get('required_memory_mb'),
            recommended_hardware=data.get('recommended_hardware'),
            evaluation_results=data.get('evaluation_results', {}),
            validation_dataset=data.get('validation_dataset'),
            validation_metrics=data.get('validation_metrics', {}),
            version=data.get('version', '1.0.0'),
            trained_at=data.get('trained_at'),
            parent_model_id=data.get('parent_model_id')
        )
    
    def save_to_file(self, file_path: str):
        """Save the model configuration to a file."""
        config = self.to_dict()
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: str):
        """Load the model configuration from a file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def update_evaluation_results(self, metrics: Dict[str, float]):
        """Update the model's evaluation results."""
        self.evaluation_results.update(metrics)
        self.metadata.evaluation_metrics.update(metrics)
        # Update individual performance metrics if present
        if 'accuracy' in metrics:
            self.performance_metrics.accuracy = metrics['accuracy']
        if 'mAP' in metrics:
            self.performance_metrics.mAP = metrics['mAP']
        if 'IoU' in metrics:
            self.performance_metrics.IoU = metrics['IoU']
    
    def validate_model_config(self) -> List[str]:
        """
        Validate the model configuration and return any issues found.
        
        Returns:
            List of validation issues (empty if all valid)
        """
        issues = []
        
        # Validate required fields
        if not self.id:
            issues.append("Model ID is required")
        
        if not self.name:
            issues.append("Model name is required")
        
        if not self.weights_path:
            issues.append("Weights path is required")
        
        if not self.input_specs:
            issues.append("At least one input specification is required")
        
        # Validate architecture
        if self.architecture.input_size[0] <= 0 or self.architecture.input_size[1] <= 0:
            issues.append("Input size dimensions must be positive")
        
        if self.architecture.num_classes <= 0:
            issues.append("Number of classes must be positive")
        
        # Validate training configuration
        if self.training_config.epochs <= 0:
            issues.append("Number of epochs must be positive")
        
        if self.training_config.batch_size <= 0:
            issues.append("Batch size must be positive")
        
        if self.training_config.learning_rate <= 0:
            issues.append("Learning rate must be positive")
        
        # Validate performance metrics
        if self.performance_metrics.inference_time_ms < 0:
            issues.append("Inference time cannot be negative")
        
        return issues
    
    def can_deploy_on_hardware(self, hardware_type: str) -> bool:
        """
        Check if the model can be deployed on specific hardware.
        
        Args:
            hardware_type: Type of hardware ("gpu", "cpu", "edge", etc.)
            
        Returns:
            True if model can be deployed on the hardware, False otherwise
        """
        if self.recommended_hardware:
            return self.recommended_hardware.lower() == hardware_type.lower()
        
        # Default checks
        if hardware_type.lower() == "edge":
            # Check if model is lightweight enough
            if self.architecture.parameters_count and self.architecture.parameters_count > 5000000:  # 5M params
                return False
            if self.required_memory_mb and self.required_memory_mb > 2000:  # 2GB
                return False
        elif hardware_type.lower() == "cpu":
            # Check if model is too large for CPU
            if self.architecture.parameters_count and self.architecture.parameters_count > 50000000:  # 50M params
                return False
        
        return True


@dataclass
class ModelRegistryEntry:
    """Registry entry for tracking deployed models."""
    model_id: str
    deployed_at: str  # ISO format datetime string
    pipeline_id: str
    status: ModelStatus
    performance_monitoring: bool = True
    monitoring_endpoint: Optional[str] = None
    accuracy_threshold: float = 0.8  # Minimum accuracy threshold
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'model_id': self.model_id,
            'deployed_at': self.deployed_at,
            'pipeline_id': self.pipeline_id,
            'status': self.status.value,
            'performance_monitoring': self.performance_monitoring,
            'monitoring_endpoint': self.monitoring_endpoint,
            'accuracy_threshold': self.accuracy_threshold
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create from dictionary."""
        return cls(
            model_id=data['model_id'],
            deployed_at=data['deployed_at'],
            pipeline_id=data['pipeline_id'],
            status=ModelStatus(data['status']),
            performance_monitoring=data.get('performance_monitoring', True),
            monitoring_endpoint=data.get('monitoring_endpoint'),
            accuracy_threshold=data.get('accuracy_threshold', 0.8)
        )


@dataclass
class ModelTrainingResult:
    """Result of training a perception model."""
    model_id: str
    training_id: str
    start_time: str  # ISO format datetime string
    end_time: str  # ISO format datetime string
    final_loss: float
    final_accuracy: Optional[float] = None
    epochs_completed: int = 0
    best_checkpoint_path: Optional[str] = None
    training_logs_path: Optional[str] = None
    validation_results: Dict[str, float] = field(default_factory=dict)
    hyperparameters_used: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'model_id': self.model_id,
            'training_id': self.training_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'final_loss': self.final_loss,
            'final_accuracy': self.final_accuracy,
            'epochs_completed': self.epochs_completed,
            'best_checkpoint_path': self.best_checkpoint_path,
            'training_logs_path': self.training_logs_path,
            'validation_results': self.validation_results,
            'hyperparameters_used': self.hyperparameters_used,
            'success': self.success,
            'error_message': self.error_message
        }


@dataclass
class ModelUpdatePlan:
    """Plan for updating a deployed model."""
    model_id: str
    update_type: str  # "patch", "minor", "major", "retrain"
    reason: str  # Reason for the update
    target_performance_gain: Optional[Dict[str, float]] = field(default_factory=dict)  # Expected improvements
    required_downtime_minutes: int = 0
    validation_required: bool = True
    rollout_strategy: str = "blue_green"  # "blue_green", "canary", "rolling"
    rollback_plan: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'model_id': self.model_id,
            'update_type': self.update_type,
            'reason': self.reason,
            'target_performance_gain': self.target_performance_gain,
            'required_downtime_minutes': self.required_downtime_minutes,
            'validation_required': self.validation_required,
            'rollout_strategy': self.rollout_strategy,
            'rollback_plan': self.rollback_plan
        }