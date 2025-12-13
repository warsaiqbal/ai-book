"""
Perception result models for the AI-Robot Brain project.

This module defines data structures for perception results generated
by perception pipelines, extending the base perception result model.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import numpy as np
import json
from src.utils.data_models import (
    BaseEntity, Vector3, BoundingBox as BaseBoundingBox,
    PerceptionResult as BasePerceptionResult
)
from src.perception.models.sensor_data import SensorData
from src.perception.models.pipeline import PerceptionModel


class DetectionStatus:
    """Enumeration of detection statuses."""
    VALID = "valid"
    INVALID = "invalid"
    PENDING = "pending"
    FILTERED = "filtered"  # Filtered by post-processing
    SUPPRESSED = "suppressed"  # Suppressed by NMS or similar


class ResultType:
    """Enumeration of result types."""
    OBJECT_DETECTION = "object_detection"
    INSTANCE_SEGMENTATION = "instance_segmentation"
    SEMANTIC_SEGMENTATION = "semantic_segmentation"
    CLASSIFICATION = "classification"
    POSE_ESTIMATION = "pose_estimation"
    DEPTH_ESTIMATION = "depth_estimation"
    OCR = "ocr"
    TRACKING = "tracking"


@dataclass
class BoundingBox:
    """Enhanced bounding box with additional properties."""
    x: float  # X coordinate of top-left corner
    y: float  # Y coordinate of top-left corner
    width: float  # Width of the box
    height: float  # Height of the box
    z: Optional[float] = None  # Z coordinate for 3D bounding boxes
    depth: Optional[float] = None  # Depth for 3D bounding boxes
    confidence_map: Optional[List[List[float]]] = None  # Per-pixel confidence if available
    area: Optional[float] = None  # Precomputed area
    
    def __post_init__(self):
        """Calculate derived properties."""
        if self.area is None and self.width is not None and self.height is not None:
            self.area = self.width * self.height
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'z': self.z,
            'depth': self.depth,
            'confidence_map': self.confidence_map,
            'area': self.area
        }


@dataclass
class Keypoint:
    """A keypoint for pose estimation."""
    x: float
    y: float
    z: Optional[float] = None  # For 3D keypoints
    confidence: float = 1.0
    visibility: Optional[bool] = None  # Whether keypoint is visible in the image
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'confidence': self.confidence,
            'visibility': self.visibility
        }


@dataclass
class DetectionMask:
    """A segmentation mask for instance segmentation."""
    format: str  # "rle" (Run Length Encoding), "polygon", "binary_mask"
    data: Union[List[float], List[List[float]], str]  # Mask data in specified format
    bbox: Optional[BoundingBox] = None  # Bounding box of the mask
    area: Optional[float] = None  # Area of the mask
    centroid: Optional[Vector3] = None  # Centroid of the mask
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            'format': self.format,
            'data': self.data,
            'area': self.area
        }
        
        if self.bbox:
            result['bbox'] = self.bbox.to_dict()
        
        if self.centroid:
            result['centroid'] = {'x': self.centroid.x, 'y': self.centroid.y, 'z': self.centroid.z}
        
        return result


@dataclass
class TrackingInfo:
    """Information for tracked objects."""
    track_id: str
    age: int  # Number of frames this track has been active
    velocity: Optional[Vector3] = None  # Estimated velocity vector
    acceleration: Optional[Vector3] = None  # Estimated acceleration vector
    is_activated: bool = True
    is_confirmed: bool = False
    is_deleted: bool = False
    appearance_features: Optional[List[float]] = None  # Visual features for re-identification
    kalman_state: Optional[List[float]] = None  # Internal Kalman filter state
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            'track_id': self.track_id,
            'age': self.age,
            'is_activated': self.is_activated,
            'is_confirmed': self.is_confirmed,
            'is_deleted': self.is_deleted
        }
        
        if self.velocity:
            result['velocity'] = {'x': self.velocity.x, 'y': self.velocity.y, 'z': self.velocity.z}
        
        if self.acceleration:
            result['acceleration'] = {'x': self.acceleration.x, 'y': self.acceleration.y, 'z': self.acceleration.z}
        
        if self.appearance_features:
            result['appearance_features'] = self.appearance_features
        
        if self.kalman_state:
            result['kalman_state'] = self.kalman_state
        
        return result


@dataclass
class ClassificationResult:
    """Result for classification tasks."""
    label: str
    confidence: float
    all_scores: Optional[Dict[str, float]] = None  # Scores for all classes if available
    embedding: Optional[List[float]] = None  # Embedding vector if applicable
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            'label': self.label,
            'confidence': self.confidence,
        }
        
        if self.all_scores:
            result['all_scores'] = self.all_scores
        
        if self.embedding:
            result['embedding'] = self.embedding
        
        return result


@dataclass
class PerceptionResult(BasePerceptionResult):
    """
    Enhanced perception result with additional fields for detailed analysis
    and post-processing.
    """
    # Additional fields beyond base class
    result_type: str = ResultType.OBJECT_DETECTION  # Type of perception result
    detection_status: str = DetectionStatus.VALID  # Validation status of the result
    model_used: Optional[str] = None  # ID of the model that generated this result
    processing_time_ms: Optional[float] = None  # Time taken to generate this result
    uncertainty: Optional[float] = None  # Uncertainty measure (0.0-1.0)
    calibration_data: Optional[Dict[str, Any]] = None  # Calibration info for 3D reprojection
    keypoints: Optional[List[Keypoint]] = None  # For pose estimation results
    mask: Optional[DetectionMask] = None  # For segmentation results
    tracking_info: Optional[TrackingInfo] = None  # For tracking results
    classification_result: Optional[ClassificationResult] = None  # For classification results
    
    # Spatial relationships with other detections
    closest_objects: List[Dict[str, Any]] = field(default_factory=list)  # Other objects in proximity
    relationship_to_robot: Optional[Dict[str, Any]] = None  # Position relative to robot
    relationship_to_environment: Optional[Dict[str, Any]] = None  # Position relative to environment
    
    # Post-processing results
    filtered_by_nms: bool = False  # Whether this detection was filtered by non-maximum suppression
    merged_with_others: List[str] = field(default_factory=list)  # Other result IDs this was merged with
    split_from: Optional[str] = None  # Original result ID if this was split from a larger detection
    augmented_result: bool = False  # Whether this result comes from augmented data
    
    # Validation and verification
    validated_by: Optional[str] = None  # How the result was validated (manual, consistency check, etc.)
    validation_score: Optional[float] = None  # Score assigned during validation (0.0-1.0)
    verification_history: List[Dict[str, Any]] = field(default_factory=list)  # History of verification steps
    
    # Performance metrics specific to this result
    precision_at_ious: Optional[Dict[float, float]] = None  # Precision at different IoU thresholds
    recall_at_ious: Optional[Dict[float, float]] = None  # Recall at different IoU thresholds
    score_distribution: Optional[List[float]] = None  # Distribution of scores in the region
    
    # Extended attributes
    attributes: Dict[str, Any] = field(default_factory=dict)  # Additional attributes specific to the detection
    tags: List[str] = field(default_factory=list)  # Tags for organization/filtering
    
    def __post_init__(self):
        """Initialize nested objects if not provided."""
        if self.attributes is None:
            self.attributes = {}
    
    def add_attribute(self, key: str, value: Any):
        """Add an attribute to the result."""
        self.attributes[key] = value
    
    def remove_attribute(self, key: str):
        """Remove an attribute from the result."""
        if key in self.attributes:
            del self.attributes[key]
    
    def get_attribute(self, key: str, default: Any = None) -> Any:
        """Get an attribute from the result."""
        return self.attributes.get(key, default)
    
    def calculate_iou(self, other_result: 'PerceptionResult') -> float:
        """
        Calculate Intersection over Union between this result and another.
        
        Args:
            other_result: Another PerceptionResult to calculate IoU with
            
        Returns:
            IoU value between 0.0 and 1.0
        """
        if not self.bounding_box or not other_result.bounding_box:
            return 0.0
        
        box1 = self.bounding_box
        box2 = other_result.bounding_box
        
        # Calculate intersection area
        x1 = max(box1.x, box2.x)
        y1 = max(box1.y, box2.y)
        x2 = min(box1.x + box1.width, box2.x + box2.width)
        y2 = min(box1.y + box1.height, box2.y + box2.height)
        
        # Check if there's an intersection
        if x2 <= x1 or y2 <= y1:
            return 0.0
        
        # Calculate areas
        intersection_area = (x2 - x1) * (y2 - y1)
        box1_area = box1.width * box1.height
        box2_area = box2.width * box2.height
        union_area = box1_area + box2_area - intersection_area
        
        if union_area == 0:
            return 0.0
        
        return intersection_area / union_area
    
    def is_similar_to(self, other_result: 'PerceptionResult', iou_threshold: float = 0.5, 
                     class_threshold: float = 0.8) -> bool:
        """
        Check if this result is similar to another result.
        
        Args:
            other_result: Another PerceptionResult to compare with
            iou_threshold: IoU threshold for spatial similarity
            class_threshold: Threshold for class similarity
            
        Returns:
            True if results are similar, False otherwise
        """
        # Check if both results have bounding boxes
        if self.bounding_box and other_result.bounding_box:
            iou = self.calculate_iou(other_result)
            if iou < iou_threshold:
                return False
        
        # Check class similarity
        if self.classification and other_result.classification:
            if self.classification != other_result.classification:
                return False
        elif self.classification or other_result.classification:
            # One has classification, the other doesn't
            return False
        
        # Check confidence similarity if both have confidence
        if self.confidence is not None and other_result.confidence is not None:
            if abs(self.confidence - other_result.confidence) > (1 - class_threshold):
                return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            'id': self.id,
            'pipeline_id': self.pipeline_id,
            'sensor_data_id': self.sensor_data_id,
            'timestamp': self.timestamp,
            'detection_type': self.detection_type,
            'confidence': self.confidence,
            'classification': self.classification,
            'position': {
                'x': self.position.x,
                'y': self.position.y,
                'z': self.position.z
            } if self.position else None,
            'validation_status': self.validation_status,
            'attributes': self.attributes,
            
            # Additional fields
            'result_type': self.result_type,
            'detection_status': self.detection_status,
            'model_used': self.model_used,
            'processing_time_ms': self.processing_time_ms,
            'uncertainty': self.uncertainty,
            'calibration_data': self.calibration_data,
            'filtered_by_nms': self.filtered_by_nms,
            'merged_with_others': self.merged_with_others,
            'split_from': self.split_from,
            'augmented_result': self.augmented_result,
            'validated_by': self.validated_by,
            'validation_score': self.validation_score,
            'tags': self.tags
        }
        
        # Add optional objects if they exist
        if self.bounding_box:
            result['bounding_box'] = self.bounding_box.to_dict()
        
        if self.keypoints:
            result['keypoints'] = [kp.to_dict() for kp in self.keypoints]
        
        if self.mask:
            result['mask'] = self.mask.to_dict()
        
        if self.tracking_info:
            result['tracking_info'] = self.tracking_info.to_dict()
        
        if self.classification_result:
            result['classification_result'] = self.classification_result.to_dict()
        
        if self.relationship_to_robot:
            result['relationship_to_robot'] = self.relationship_to_robot
        
        if self.relationship_to_environment:
            result['relationship_to_environment'] = self.relationship_to_environment
        
        if self.closest_objects:
            result['closest_objects'] = self.closest_objects
        
        if self.precision_at_ious:
            result['precision_at_ious'] = self.precision_at_ious
        
        if self.recall_at_ious:
            result['recall_at_ious'] = self.recall_at_ious
        
        if self.score_distribution:
            result['score_distribution'] = self.score_distribution
        
        if self.verification_history:
            result['verification_history'] = self.verification_history
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create from dictionary."""
        # Parse position
        position = None
        if 'position' in data and data['position']:
            pos_data = data['position']
            position = Vector3(pos_data['x'], pos_data['y'], pos_data['z'])
        
        # Parse bounding box
        bounding_box = None
        if 'bounding_box' in data:
            bb_data = data['bounding_box']
            bounding_box = BoundingBox(
                x=bb_data['x'],
                y=bb_data['y'],
                width=bb_data['width'],
                height=bb_data['height'],
                z=bb_data.get('z'),
                depth=bb_data.get('depth'),
                confidence_map=bb_data.get('confidence_map'),
                area=bb_data.get('area')
            )
        
        # Parse keypoints
        keypoints = None
        if 'keypoints' in data:
            keypoints = [
                Keypoint(
                    x=kp['x'],
                    y=kp['y'],
                    z=kp.get('z'),
                    confidence=kp.get('confidence', 1.0),
                    visibility=kp.get('visibility')
                )
                for kp in data['keypoints']
            ]
        
        # Parse mask
        mask = None
        if 'mask' in data:
            mask_data = data['mask']
            bbox = None
            if 'bbox' in mask_data:
                bb_data = mask_data['bbox']
                bbox = BoundingBox(
                    x=bb_data['x'],
                    y=bb_data['y'],
                    width=bb_data['width'],
                    height=bb_data['height']
                )
            
            centroid = None
            if 'centroid' in mask_data:
                cent_data = mask_data['centroid']
                centroid = Vector3(cent_data['x'], cent_data['y'], cent_data['z'])
            
            mask = DetectionMask(
                format=mask_data['format'],
                data=mask_data['data'],
                bbox=bbox,
                area=mask_data.get('area'),
                centroid=centroid
            )
        
        # Parse tracking info
        tracking_info = None
        if 'tracking_info' in data:
            track_data = data['tracking_info']
            velocity = None
            acceleration = None
            
            if 'velocity' in track_data:
                vel_data = track_data['velocity']
                velocity = Vector3(vel_data['x'], vel_data['y'], vel_data['z'])
            
            if 'acceleration' in track_data:
                acc_data = track_data['acceleration']
                acceleration = Vector3(acc_data['x'], acc_data['y'], acc_data['z'])
            
            tracking_info = TrackingInfo(
                track_id=track_data['track_id'],
                age=track_data['age'],
                velocity=velocity,
                acceleration=acceleration,
                is_activated=track_data.get('is_activated', True),
                is_confirmed=track_data.get('is_confirmed', False),
                is_deleted=track_data.get('is_deleted', False),
                appearance_features=track_data.get('appearance_features'),
                kalman_state=track_data.get('kalman_state')
            )
        
        # Parse classification result
        classification_result = None
        if 'classification_result' in data:
            cr_data = data['classification_result']
            classification_result = ClassificationResult(
                label=cr_data['label'],
                confidence=cr_data['confidence'],
                all_scores=cr_data.get('all_scores'),
                embedding=cr_data.get('embedding')
            )
        
        # Create and return the result instance
        return cls(
            id=data['id'],
            pipeline_id=data['pipeline_id'],
            sensor_data_id=data['sensor_data_id'],
            timestamp=data['timestamp'],
            detection_type=data['detection_type'],
            confidence=data['confidence'],
            bounding_box=bounding_box,
            classification=data.get('classification'),
            position=position,
            validation_status=data.get('validation_status', 'pending'),
            attributes=data.get('attributes', {}),
            
            # Additional fields
            result_type=data.get('result_type', ResultType.OBJECT_DETECTION),
            detection_status=data.get('detection_status', DetectionStatus.VALID),
            model_used=data.get('model_used'),
            processing_time_ms=data.get('processing_time_ms'),
            uncertainty=data.get('uncertainty'),
            calibration_data=data.get('calibration_data'),
            keypoints=keypoints,
            mask=mask,
            tracking_info=tracking_info,
            classification_result=classification_result,
            closest_objects=data.get('closest_objects', []),
            relationship_to_robot=data.get('relationship_to_robot'),
            relationship_to_environment=data.get('relationship_to_environment'),
            filtered_by_nms=data.get('filtered_by_nms', False),
            merged_with_others=data.get('merged_with_others', []),
            split_from=data.get('split_from'),
            augmented_result=data.get('augmented_result', False),
            validated_by=data.get('validated_by'),
            validation_score=data.get('validation_score'),
            verification_history=data.get('verification_history', []),
            precision_at_ious=data.get('precision_at_ious'),
            recall_at_ious=data.get('recall_at_ious'),
            score_distribution=data.get('score_distribution'),
            tags=data.get('tags', [])
        )
    
    def save_to_file(self, file_path: str):
        """Save the perception result to a file."""
        config = self.to_dict()
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: str):
        """Load the perception result from a file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def validate_result(self) -> List[str]:
        """
        Validate the perception result and return any issues found.
        
        Returns:
            List of validation issues (empty if all valid)
        """
        issues = []
        
        # Check required fields
        if not self.id:
            issues.append("Result ID is required")
        
        if not self.pipeline_id:
            issues.append("Pipeline ID is required")
        
        if not self.sensor_data_id:
            issues.append("Sensor data ID is required")
        
        # Validate confidence range
        if self.confidence is not None and (self.confidence < 0.0 or self.confidence > 1.0):
            issues.append("Confidence must be between 0.0 and 1.0")
        
        # Validate uncertainty range if present
        if self.uncertainty is not None and (self.uncertainty < 0.0 or self.uncertainty > 1.0):
            issues.append("Uncertainty must be between 0.0 and 1.0")
        
        # Validate position if present
        if self.position:
            # Check for valid position values (not NaN or infinity)
            if any(np.isnan([self.position.x, self.position.y, self.position.z])):
                issues.append("Position contains NaN values")
            if any(np.isinf([self.position.x, self.position.y, self.position.z])):
                issues.append("Position contains infinite values")
        
        # Validate bounding box if present
        if self.bounding_box:
            if self.bounding_box.width <= 0 or self.bounding_box.height <= 0:
                issues.append("Bounding box must have positive width and height")
        
        # Validate detection status
        valid_statuses = [attr for attr in dir(DetectionStatus) if not attr.startswith('_')]
        if self.detection_status not in valid_statuses:
            issues.append(f"Invalid detection status: {self.detection_status}")
        
        # Validate result type
        valid_types = [attr for attr in dir(ResultType) if not attr.startswith('_')]
        if self.result_type not in valid_types:
            issues.append(f"Invalid result type: {self.result_type}")
        
        return issues


@dataclass
class PerceptionResultBatch:
    """Batch of perception results for processing."""
    batch_id: str
    results: List[PerceptionResult]
    created_at: str  # ISO format datetime string
    pipeline_id: Optional[str] = None
    sensor_data_ids: List[str] = field(default_factory=list)
    processed: bool = False
    processing_results: Optional[Dict[str, Any]] = None  # Results of post-processing
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'batch_id': self.batch_id,
            'results': [result.to_dict() for result in self.results],
            'created_at': self.created_at,
            'pipeline_id': self.pipeline_id,
            'sensor_data_ids': self.sensor_data_ids,
            'processed': self.processed,
            'processing_results': self.processing_results
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create from dictionary."""
        results = [PerceptionResult.from_dict(result_data) for result_data in data['results']]
        
        return cls(
            batch_id=data['batch_id'],
            results=results,
            created_at=data['created_at'],
            pipeline_id=data.get('pipeline_id'),
            sensor_data_ids=data.get('sensor_data_ids', []),
            processed=data.get('processed', False),
            processing_results=data.get('processing_results')
        )


@dataclass
class ResultValidationMetrics:
    """Metrics for validating perception results."""
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    mAP: float = 0.0  # Mean Average Precision
    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    accuracy: float = 0.0
    
    # Confidence-specific metrics
    confidence_threshold: float = 0.5
    precision_at_threshold: float = 0.0
    recall_at_threshold: float = 0.0
    
    # IoU-specific metrics
    iou_threshold: float = 0.5
    mAP_at_iou: float = 0.0  # mAP calculated at specific IoU threshold
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'precision': self.precision,
            'recall': self.recall,
            'f1_score': self.f1_score,
            'mAP': self.mAP,
            'true_positives': self.true_positives,
            'false_positives': self.false_positives,
            'false_negatives': self.false_negatives,
            'accuracy': self.accuracy,
            'confidence_threshold': self.confidence_threshold,
            'precision_at_threshold': self.precision_at_threshold,
            'recall_at_threshold': self.recall_at_threshold,
            'iou_threshold': self.iou_threshold,
            'mAP_at_iou': self.mAP_at_iou
        }


@dataclass
class SpatialRelationship:
    """Represents spatial relationships between detections."""
    reference_object_id: str
    related_object_id: str
    relationship_type: str  # "left_of", "right_of", "above", "below", "near", "far", etc.
    distance: float  # Distance in meters
    angle: Optional[float] = None  # Angle in radians (if applicable)
    confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'reference_object_id': self.reference_object_id,
            'related_object_id': self.related_object_id,
            'relationship_type': self.relationship_type,
            'distance': self.distance,
            'angle': self.angle,
            'confidence': self.confidence
        }


@dataclass
class PostProcessingResult:
    """Result of post-processing applied to perception results."""
    original_result_ids: List[str]  # IDs of results that were processed
    processed_result_ids: List[str]  # IDs of results after processing
    processing_type: str  # "nms", "tracking", "fusion", "filtering", etc.
    parameters_used: Dict[str, Any]  # Parameters used during processing
    performance_impact: Optional[Dict[str, float]] = None  # Impact on metrics
    timestamp: str = ""  # When processing was applied
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'original_result_ids': self.original_result_ids,
            'processed_result_ids': self.processed_result_ids,
            'processing_type': self.processing_type,
            'parameters_used': self.parameters_used,
            'performance_impact': self.performance_impact,
            'timestamp': self.timestamp
        }