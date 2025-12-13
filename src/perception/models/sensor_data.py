"""
Sensor data models for the perception module in the AI-Robot Brain project.

This module defines data structures for sensor data used in perception tasks,
extending the base sensor data model with perception-specific features.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
import numpy as np
from datetime import datetime
import json
from src.utils.data_models import (
    BaseEntity, Vector3, DataType as BaseDataType, 
    SensorData as BaseSensorData, SensorType as BaseSensorType
)


class DataType:
    """Enumeration of data types for perception (extending base)."""
    IMAGE = "image"
    DEPTH_IMAGE = "depth_image"
    LIDAR = "lidar"
    POINT_CLOUD = "point_cloud"
    IMU = "imu"
    JOINT_STATE = "joint_state"
    LASER_SCAN = "laser_scan"
    ODOMETRY = "odometry"
    CAMERA_INFO = "camera_info"
    TF = "tf"
    CUSTOM = "custom"


@dataclass
class CameraIntrinsics:
    """Camera intrinsic parameters."""
    fx: float  # Focal length x
    fy: float  # Focal length y
    cx: float  # Principal point x
    cy: float  # Principal point y
    width: int  # Image width
    height: int  # Image height
    distortion_coeffs: List[float] = field(default_factory=list)  # [k1, k2, p1, p2, k3, ...]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'fx': self.fx,
            'fy': self.fy,
            'cx': self.cx,
            'cy': self.cy,
            'width': self.width,
            'height': self.height,
            'distortion_coeffs': self.distortion_coeffs
        }


@dataclass
class CameraExtrinsics:
    """Camera extrinsic parameters (position and orientation relative to robot)."""
    position: Vector3
    orientation: Vector3  # Euler angles (roll, pitch, yaw) in radians
    transform_matrix: List[float] = field(default_factory=list)  # 4x4 transform matrix as flattened list
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'position': {'x': self.position.x, 'y': self.position.y, 'z': self.position.z},
            'orientation': {'x': self.orientation.x, 'y': self.orientation.y, 'z': self.orientation.z},
            'transform_matrix': self.transform_matrix
        }


@dataclass
class SensorCalibration:
    """Calibration information for a sensor."""
    intrinsics: Optional[CameraIntrinsics] = None
    extrinsics: Optional[CameraExtrinsics] = None
    timestamp: Optional[str] = None  # ISO format datetime string
    calibration_method: Optional[str] = None  # "manual", "auto", "checkerboard", etc.
    reprojection_error: Optional[float] = None  # Error metric for camera calibration
    valid: bool = True  # Whether calibration is valid
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            'timestamp': self.timestamp,
            'calibration_method': self.calibration_method,
            'reprojection_error': self.reprojection_error,
            'valid': self.valid
        }
        
        if self.intrinsics:
            result['intrinsics'] = self.intrinsics.to_dict()
        
        if self.extrinsics:
            result['extrinsics'] = self.extrinsics.to_dict()
        
        return result


@dataclass
class SensorQualityMetrics:
    """Quality metrics for sensor data."""
    signal_to_noise_ratio: Optional[float] = None
    sharpness: Optional[float] = None  # For image data
    contrast: Optional[float] = None  # For image data
    brightness: Optional[float] = None  # For image data
    exposure_time: Optional[float] = None  # For camera data in seconds
    frame_rate: Optional[float] = None  # Actual frame rate achieved
    data_completeness: Optional[float] = None  # Ratio of valid to expected data points
    temporal_jitter: Optional[float] = None  # Timing consistency
    latency: Optional[float] = None  # Processing delay in seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'signal_to_noise_ratio': self.signal_to_noise_ratio,
            'sharpness': self.sharpness,
            'contrast': self.contrast,
            'brightness': self.brightness,
            'exposure_time': self.exposure_time,
            'frame_rate': self.frame_rate,
            'data_completeness': self.data_completeness,
            'temporal_jitter': self.temporal_jitter,
            'latency': self.latency
        }


@dataclass
class Annotation:
    """Annotation for sensor data used in training."""
    id: str
    annotation_type: str  # "bbox", "polygon", "mask", "keypoints", "text", etc.
    label: str
    confidence: float = 1.0
    points: List[List[float]] = field(default_factory=list)  # Points for polygon/bbox annotations
    attributes: Dict[str, Any] = field(default_factory=dict)  # Additional attributes
    is_synthetic: bool = False  # Whether annotation was generated synthetically
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'annotation_type': self.annotation_type,
            'label': self.label,
            'confidence': self.confidence,
            'points': self.points,
            'attributes': self.attributes,
            'is_synthetic': self.is_synthetic
        }


@dataclass
class SensorDataChunk:
    """A chunk of sensor data for batch processing."""
    chunk_id: str
    data_type: str  # Image, point cloud, etc.
    data_path: str  # Path to the data file
    size: int  # Size in bytes
    timestamp: float  # Unix timestamp
    duration: float  # Duration in seconds
    frame_count: Optional[int] = None  # For video/image sequences
    chunk_index: Optional[int] = None  # Index in sequence of chunks
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'chunk_id': self.chunk_id,
            'data_type': self.data_type,
            'data_path': self.data_path,
            'size': self.size,
            'timestamp': self.timestamp,
            'duration': self.duration,
            'frame_count': self.frame_count,
            'chunk_index': self.chunk_index
        }


@dataclass
class SensorData(BaseSensorData):
    """
    Enhanced sensor data model with perception-specific features.
    Extends the base SensorData with additional fields relevant to perception tasks.
    """
    # Additional perception-specific fields
    calibration: Optional[SensorCalibration] = None
    quality_metrics: Optional[SensorQualityMetrics] = None
    annotations: List[Annotation] = field(default_factory=list)
    is_synthetic: bool = False  # Whether data was generated synthetically
    synthetic_config: Optional[Dict[str, Any]] = None  # Configuration for synthetic data generation
    preprocessed_path: Optional[str] = None  # Path to preprocessed version of the data
    feature_vectors: Optional[List[float]] = None  # Extracted features if applicable
    perceptual_hash: Optional[str] = None  # Hash for data deduplication
    domain: Optional[str] = None  # "real", "synthetic", "mixed" - for domain randomization
    environment_type: Optional[str] = None  # "indoor", "outdoor", "urban", "rural", etc.
    lighting_condition: Optional[str] = None  # "daylight", "night", "dawn_dusk", "artificial"
    weather_condition: Optional[str] = None  # "clear", "rainy", "snowy", "foggy", etc.
    occlusion_level: float = 0.0  # 0.0-1.0 level of occlusion in the scene
    difficulty_level: str = "easy"  # "easy", "medium", "hard" - for benchmarking
    
    # Data provenance
    source_dataset: Optional[str] = None  # Name of the dataset this data came from
    data_collection_method: Optional[str] = None  # "manual", "automatic", "simulation"
    annotator_id: Optional[str] = None  # ID of the annotator if manually annotated
    annotation_tool: Optional[str] = None  # Tool used for annotation
    
    # For batch processing
    data_chunks: List[SensorDataChunk] = field(default_factory=list)
    chunk_index: Optional[int] = None  # Index if this is part of a chunked dataset
    
    # Extended metadata
    tags: List[str] = field(default_factory=list)  # Tags for quick filtering
    is_valid_for_training: bool = True  # Whether this data should be used for training
    
    def __post_init__(self):
        """Initialize nested objects if not provided."""
        if self.metadata is None:
            self.metadata = {}
    
    def add_annotation(self, annotation: Annotation):
        """Add an annotation to the sensor data."""
        self.annotations.append(annotation)
    
    def remove_annotation(self, annotation_id: str):
        """Remove an annotation by ID."""
        self.annotations = [ann for ann in self.annotations if ann.id != annotation_id]
    
    def get_annotations_by_label(self, label: str) -> List[Annotation]:
        """Get all annotations with a specific label."""
        return [ann for ann in self.annotations if ann.label == label]
    
    def calculate_perceptual_hash(self) -> str:
        """
        Calculate a perceptual hash for the data (simplified implementation).
        In a real implementation, this would compute a proper perceptual hash.
        """
        import hashlib
        # This is a simplified hash based on the filename and timestamp
        hash_input = f"{self.data_path}_{self.timestamp}_{self.width}_{self.height}".encode('utf-8')
        self.perceptual_hash = hashlib.md5(hash_input).hexdigest()
        return self.perceptual_hash
    
    def validate_data(self) -> List[str]:
        """
        Validate the sensor data and return any issues found.
        
        Returns:
            List of validation issues (empty if all valid)
        """
        issues = []
        
        # Check if required fields are present
        if not self.data_path:
            issues.append("Data path is required")
        
        if not self.data_type:
            issues.append("Data type is required")
        
        # Validate data type
        valid_types = [attr for attr in dir(DataType) if not attr.startswith('_')]
        if self.data_type not in valid_types:
            issues.append(f"Unknown data type: {self.data_type}")
        
        # Validate dimensions if image data
        if self.data_type in [DataType.IMAGE, DataType.DEPTH_IMAGE] and (not self.width or not self.height):
            issues.append("Width and height are required for image data")
        
        # Validate annotations if present
        for i, annotation in enumerate(self.annotations):
            if not annotation.id:
                issues.append(f"Annotation {i} has no ID")
            if not annotation.label:
                issues.append(f"Annotation {i} has no label")
        
        # Validate quality metrics if present
        if self.quality_metrics:
            if self.quality_metrics.signal_to_noise_ratio is not None and self.quality_metrics.signal_to_noise_ratio < 0:
                issues.append("SNR cannot be negative")
            if self.quality_metrics.sharpness is not None and (self.quality_metrics.sharpness < 0 or self.quality_metrics.sharpness > 1):
                issues.append("Sharpness must be between 0 and 1")
            if self.quality_metrics.occlusion_level < 0 or self.quality_metrics.occlusion_level > 1:
                issues.append("Occlusion level must be between 0 and 1")
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            'id': self.id,
            'sensor_id': self.sensor_id,
            'timestamp': self.timestamp,
            'data_type': self.data_type,
            'data_path': self.data_path,
            'format': self.format,
            'frame_id': self.frame_id,
            'width': self.width,
            'height': self.height,
            'metadata': self.metadata,
            'simulated_environment_state': self.simulated_environment_state,
            
            # Perception-specific fields
            'is_synthetic': self.is_synthetic,
            'synthetic_config': self.synthetic_config,
            'preprocessed_path': self.preprocessed_path,
            'feature_vectors': self.feature_vectors,
            'perceptual_hash': self.perceptual_hash,
            'domain': self.domain,
            'environment_type': self.environment_type,
            'lighting_condition': self.lighting_condition,
            'weather_condition': self.weather_condition,
            'occlusion_level': self.occlusion_level,
            'difficulty_level': self.difficulty_level,
            'source_dataset': self.source_dataset,
            'data_collection_method': self.data_collection_method,
            'annotator_id': self.annotator_id,
            'annotation_tool': self.annotation_tool,
            'chunk_index': self.chunk_index,
            'tags': self.tags,
            'is_valid_for_training': self.is_valid_for_training
        }
        
        # Add optional objects if they exist
        if self.calibration:
            result['calibration'] = self.calibration.to_dict()
        
        if self.quality_metrics:
            result['quality_metrics'] = self.quality_metrics.to_dict()
        
        if self.annotations:
            result['annotations'] = [ann.to_dict() for ann in self.annotations]
        
        if self.data_chunks:
            result['data_chunks'] = [chunk.to_dict() for chunk in self.data_chunks]
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create from dictionary."""
        # Handle complex nested objects
        calibration = None
        if 'calibration' in data:
            cal_data = data['calibration']
            intrinsics = None
            extrinsics = None
            
            if 'intrinsics' in cal_data:
                intr_data = cal_data['intrinsics']
                intrinsics = CameraIntrinsics(
                    fx=intr_data['fx'],
                    fy=intr_data['fy'],
                    cx=intr_data['cx'],
                    cy=intr_data['cy'],
                    width=intr_data['width'],
                    height=intr_data['height'],
                    distortion_coeffs=intr_data.get('distortion_coeffs', [])
                )
            
            if 'extrinsics' in cal_data:
                ext_data = cal_data['extrinsics']
                ext_pos = ext_data['position']
                ext_rot = ext_data['orientation']
                extrinsics = CameraExtrinsics(
                    position=Vector3(ext_pos['x'], ext_pos['y'], ext_pos['z']),
                    orientation=Vector3(ext_rot['x'], ext_rot['y'], ext_rot['z']),
                    transform_matrix=ext_data.get('transform_matrix', [])
                )
            
            calibration = SensorCalibration(
                intrinsics=intrinsics,
                extrinsics=extrinsics,
                timestamp=cal_data.get('timestamp'),
                calibration_method=cal_data.get('calibration_method'),
                reprojection_error=cal_data.get('reprojection_error'),
                valid=cal_data.get('valid', True)
            )
        
        quality_metrics = None
        if 'quality_metrics' in data:
            qm_data = data['quality_metrics']
            quality_metrics = SensorQualityMetrics(
                signal_to_noise_ratio=qm_data.get('signal_to_noise_ratio'),
                sharpness=qm_data.get('sharpness'),
                contrast=qm_data.get('contrast'),
                brightness=qm_data.get('brightness'),
                exposure_time=qm_data.get('exposure_time'),
                frame_rate=qm_data.get('frame_rate'),
                data_completeness=qm_data.get('data_completeness'),
                temporal_jitter=qm_data.get('temporal_jitter'),
                latency=qm_data.get('latency')
            )
        
        annotations = []
        if 'annotations' in data:
            for ann_data in data['annotations']:
                annotations.append(Annotation(
                    id=ann_data['id'],
                    annotation_type=ann_data['annotation_type'],
                    label=ann_data['label'],
                    confidence=ann_data.get('confidence', 1.0),
                    points=ann_data.get('points', []),
                    attributes=ann_data.get('attributes', {}),
                    is_synthetic=ann_data.get('is_synthetic', False)
                ))
        
        data_chunks = []
        if 'data_chunks' in data:
            for chunk_data in data['data_chunks']:
                data_chunks.append(SensorDataChunk(
                    chunk_id=chunk_data['chunk_id'],
                    data_type=chunk_data['data_type'],
                    data_path=chunk_data['data_path'],
                    size=chunk_data['size'],
                    timestamp=chunk_data['timestamp'],
                    duration=chunk_data['duration'],
                    frame_count=chunk_data.get('frame_count'),
                    chunk_index=chunk_data.get('chunk_index')
                ))
        
        # Create and return the sensor data instance
        return cls(
            id=data['id'],
            sensor_id=data['sensor_id'],
            timestamp=data['timestamp'],
            data_type=data['data_type'],
            data_path=data['data_path'],
            format=data.get('format', 'unknown'),
            frame_id=data.get('frame_id', 'sensor_link'),
            width=data.get('width'),
            height=data.get('height'),
            metadata=data.get('metadata', {}),
            simulated_environment_state=data.get('simulated_environment_state', ''),
            
            # Perception-specific fields
            calibration=calibration,
            quality_metrics=quality_metrics,
            annotations=annotations,
            is_synthetic=data.get('is_synthetic', False),
            synthetic_config=data.get('synthetic_config'),
            preprocessed_path=data.get('preprocessed_path'),
            feature_vectors=data.get('feature_vectors'),
            perceptual_hash=data.get('perceptual_hash'),
            domain=data.get('domain'),
            environment_type=data.get('environment_type'),
            lighting_condition=data.get('lighting_condition'),
            weather_condition=data.get('weather_condition'),
            occlusion_level=data.get('occlusion_level', 0.0),
            difficulty_level=data.get('difficulty_level', 'easy'),
            source_dataset=data.get('source_dataset'),
            data_collection_method=data.get('data_collection_method'),
            annotator_id=data.get('annotator_id'),
            annotation_tool=data.get('annotation_tool'),
            data_chunks=data_chunks,
            chunk_index=data.get('chunk_index'),
            tags=data.get('tags', []),
            is_valid_for_training=data.get('is_valid_for_training', True)
        )
    
    def save_to_file(self, file_path: str):
        """Save the sensor data configuration to a file."""
        config = self.to_dict()
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: str):
        """Load the sensor data configuration from a file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


@dataclass
class MultiModalSensorData:
    """Container for multi-modal sensor data from different sensors."""
    id: str
    timestamp: float
    sensor_data_map: Dict[str, SensorData]  # sensor_id -> SensorData
    fusion_strategy: str = "early"  # "early", "late", "intermediate"
    synchronized: bool = True
    sync_tolerance: float = 0.01  # Tolerance for synchronization in seconds
    fused_data_path: Optional[str] = None  # Path to fused data if applicable
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'sensor_data_map': {id: data.to_dict() for id, data in self.sensor_data_map.items()},
            'fusion_strategy': self.fusion_strategy,
            'synchronized': self.synchronized,
            'sync_tolerance': self.sync_tolerance,
            'fused_data_path': self.fused_data_path
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create from dictionary."""
        sensor_data_map = {
            id: SensorData.from_dict(sd_data) 
            for id, sd_data in data['sensor_data_map'].items()
        }
        
        return cls(
            id=data['id'],
            timestamp=data['timestamp'],
            sensor_data_map=sensor_data_map,
            fusion_strategy=data.get('fusion_strategy', 'early'),
            synchronized=data.get('synchronized', True),
            sync_tolerance=data.get('sync_tolerance', 0.01),
            fused_data_path=data.get('fused_data_path')
        )


@dataclass
class SensorDataBatch:
    """Batch of sensor data for training or inference."""
    batch_id: str
    data_list: List[SensorData]
    batch_size: int
    created_at: str  # ISO format datetime string
    processed: bool = False
    processing_results: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'batch_id': self.batch_id,
            'data_list': [data.to_dict() for data in self.data_list],
            'batch_size': self.batch_size,
            'created_at': self.created_at,
            'processed': self.processed,
            'processing_results': self.processing_results
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create from dictionary."""
        data_list = [SensorData.from_dict(sd_data) for sd_data in data['data_list']]
        
        return cls(
            batch_id=data['batch_id'],
            data_list=data_list,
            batch_size=data['batch_size'],
            created_at=data['created_at'],
            processed=data.get('processed', False),
            processing_results=data.get('processing_results')
        )


@dataclass
class DataAugmentationConfig:
    """Configuration for data augmentation."""
    rotation_range: float = 15.0  # Maximum rotation in degrees
    width_shift_range: float = 0.1  # Maximum horizontal shift as fraction of width
    height_shift_range: float = 0.1  # Maximum vertical shift as fraction of height
    shear_range: float = 0.0  # Shear intensity
    zoom_range: float = 0.0  # Range for random zoom
    horizontal_flip: bool = False  # Whether to randomly flip horizontally
    vertical_flip: bool = False  # Whether to randomly flip vertically
    brightness_range: Optional[List[float]] = None  # [lower, upper] brightness multiplier
    channel_shift_range: float = 0.0  # Value for channel shift
    fill_mode: str = 'nearest'  # Points outside boundaries are filled with 'nearest', 'constant', etc.
    cval: float = 0.0  # Value to fill with when fill_mode is 'constant'
    
    # Perception-specific augmentations
    occlusion_augmentation: bool = False  # Whether to simulate occlusions
    noise_augmentation: bool = False  # Whether to add synthetic noise
    blur_augmentation: bool = False  # Whether to apply synthetic blur
    weather_augmentation: bool = False  # Whether to simulate weather conditions
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'rotation_range': self.rotation_range,
            'width_shift_range': self.width_shift_range,
            'height_shift_range': self.height_shift_range,
            'shear_range': self.shear_range,
            'zoom_range': self.zoom_range,
            'horizontal_flip': self.horizontal_flip,
            'vertical_flip': self.vertical_flip,
            'brightness_range': self.brightness_range,
            'channel_shift_range': self.channel_shift_range,
            'fill_mode': self.fill_mode,
            'cval': self.cval,
            'occlusion_augmentation': self.occlusion_augmentation,
            'noise_augmentation': self.noise_augmentation,
            'blur_augmentation': self.blur_augmentation,
            'weather_augmentation': self.weather_augmentation
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create from dictionary."""
        return cls(
            rotation_range=data.get('rotation_range', 15.0),
            width_shift_range=data.get('width_shift_range', 0.1),
            height_shift_range=data.get('height_shift_range', 0.1),
            shear_range=data.get('shear_range', 0.0),
            zoom_range=data.get('zoom_range', 0.0),
            horizontal_flip=data.get('horizontal_flip', False),
            vertical_flip=data.get('vertical_flip', False),
            brightness_range=data.get('brightness_range'),
            channel_shift_range=data.get('channel_shift_range', 0.0),
            fill_mode=data.get('fill_mode', 'nearest'),
            cval=data.get('cval', 0.0),
            occlusion_augmentation=data.get('occlusion_augmentation', False),
            noise_augmentation=data.get('noise_augmentation', False),
            blur_augmentation=data.get('blur_augmentation', False),
            weather_augmentation=data.get('weather_augmentation', False)
        )