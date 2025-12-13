"""
Utility functions for mathematical operations, particularly for vector and quaternion operations
needed in robotics applications.
"""
import math
from typing import List, Tuple, Union

import numpy as np

from ..models.data_models import Point3D, Quaternion, Pose


def normalize_vector(vector: List[float]) -> List[float]:
    """
    Normalize a 3D vector to unit length.
    
    Args:
        vector: A 3D vector [x, y, z]
        
    Returns:
        Normalized vector as a list
    """
    magnitude = math.sqrt(sum(v ** 2 for v in vector))
    if magnitude == 0:
        return [0.0, 0.0, 0.0]
    return [v / magnitude for v in vector]


def quaternion_multiply(q1: List[float], q2: List[float]) -> List[float]:
    """
    Multiply two quaternions.
    
    Args:
        q1: First quaternion [x, y, z, w]
        q2: Second quaternion [x, y, z, w]
        
    Returns:
        Resultant quaternion [x, y, z, w]
    """
    x1, y1, z1, w1 = q1
    x2, y2, z2, w2 = q2
    
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2
    z = w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    
    return [x, y, z, w]


def quaternion_to_euler(q: List[float]) -> Tuple[float, float, float]:
    """
    Convert a quaternion to Euler angles (roll, pitch, yaw).
    
    Args:
        q: Quaternion [x, y, z, w]
        
    Returns:
        Tuple of (roll, pitch, yaw) in radians
    """
    x, y, z, w = q
    
    # Roll (x-axis rotation)
    sinr_cosp = 2 * (w * x + y * z)
    cosr_cosp = 1 - 2 * (x * x + y * y)
    roll = math.atan2(sinr_cosp, cosr_cosp)
    
    # Pitch (y-axis rotation)
    sinp = 2 * (w * y - z * x)
    if abs(sinp) >= 1:
        pitch = math.copysign(math.pi / 2, sinp)  # Use 90 degrees if out of range
    else:
        pitch = math.asin(sinp)
    
    # Yaw (z-axis rotation)
    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    yaw = math.atan2(siny_cosp, cosy_cosp)
    
    return (roll, pitch, yaw)


def euler_to_quaternion(roll: float, pitch: float, yaw: float) -> List[float]:
    """
    Convert Euler angles (roll, pitch, yaw) to a quaternion.
    
    Args:
        roll: Roll angle in radians
        pitch: Pitch angle in radians
        yaw: Yaw angle in radians
        
    Returns:
        Quaternion [x, y, z, w]
    """
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    
    w = cr * cp * cy + sr * sp * sy
    x = sr * cp * cy - cr * sp * sy
    y = cr * sp * cy + sr * cp * sy
    z = cr * cp * sy - sr * sp * cy
    
    return [x, y, z, w]


def quaternion_rotate_vector(q: List[float], v: List[float]) -> List[float]:
    """
    Rotate a 3D vector by a quaternion.
    
    Args:
        q: Quaternion [x, y, z, w] representing the rotation
        v: 3D vector [x, y, z] to be rotated
        
    Returns:
        Rotated 3D vector [x, y, z]
    """
    # Convert vector to quaternion (with w=0)
    vec_quat = [v[0], v[1], v[2], 0]
    
    # Multiply: q * v * q_conjugate
    q_conjugate = [-q[0], -q[1], -q[2], q[3]]
    temp = quaternion_multiply(q, vec_quat)
    rotated_quat = quaternion_multiply(temp, q_conjugate)
    
    # Return the vector part (x, y, z)
    return rotated_quat[:3]


def calculate_distance_3d(p1: Union[Point3D, List[float]], p2: Union[Point3D, List[float]]) -> float:
    """
    Calculate the Euclidean distance between two 3D points.
    
    Args:
        p1: First point as Point3D or [x, y, z]
        p2: Second point as Point3D or [x, y, z]
        
    Returns:
        Distance between the two points
    """
    # Convert to lists if Point3D objects
    if isinstance(p1, Point3D):
        p1 = [p1.x, p1.y, p1.z]
    if isinstance(p2, Point3D):
        p2 = [p2.x, p2.y, p2.z]
    
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dz = p2[2] - p1[2]
    
    return math.sqrt(dx*dx + dy*dy + dz*dz)


def pose_to_transform_matrix(pose: Pose) -> np.ndarray:
    """
    Convert a Pose (position and orientation) to a 4x4 transformation matrix.
    
    Args:
        pose: Pose object containing position and orientation
        
    Returns:
        4x4 transformation matrix as numpy array
    """
    # Convert position and orientation to lists
    pos = [pose.position.x, pose.position.y, pose.position.z]
    quat = [pose.orientation.x, pose.orientation.y, pose.orientation.z, pose.orientation.w]
    
    # Create rotation matrix from quaternion
    x, y, z, w = quat
    
    # Rotation matrix from quaternion
    rotation_matrix = np.array([
        [1 - 2*y*y - 2*z*z, 2*x*y - 2*z*w, 2*x*z + 2*y*w],
        [2*x*y + 2*z*w, 1 - 2*x*x - 2*z*z, 2*y*z - 2*x*w],
        [2*x*z - 2*y*w, 2*y*z + 2*x*w, 1 - 2*x*x - 2*y*y]
    ])
    
    # Create 4x4 transformation matrix
    transform_matrix = np.eye(4)
    transform_matrix[:3, :3] = rotation_matrix
    transform_matrix[:3, 3] = pos
    
    return transform_matrix


def transform_pose(pose: Pose, transform_matrix: np.ndarray) -> Pose:
    """
    Apply a transformation matrix to a pose.
    
    Args:
        pose: Original pose
        transform_matrix: 4x4 transformation matrix
        
    Returns:
        Transformed pose
    """
    # Convert the original pose to a transformation matrix
    original_matrix = pose_to_transform_matrix(pose)
    
    # Apply the transformation
    result_matrix = np.dot(transform_matrix, original_matrix)
    
    # Extract position
    new_position = Point3D(
        x=float(result_matrix[0, 3]),
        y=float(result_matrix[1, 3]),
        z=float(result_matrix[2, 3])
    )
    
    # Extract rotation (convert rotation matrix back to quaternion)
    rotation_matrix = result_matrix[:3, :3]
    
    # Convert rotation matrix to quaternion
    trace = np.trace(rotation_matrix)
    if trace > 0:
        s = math.sqrt(trace + 1.0) * 2  # S=4*qw
        qw = 0.25 * s
        qx = (rotation_matrix[2, 1] - rotation_matrix[1, 2]) / s
        qy = (rotation_matrix[0, 2] - rotation_matrix[2, 0]) / s
        qz = (rotation_matrix[1, 0] - rotation_matrix[0, 1]) / s
    else:
        if rotation_matrix[0, 0] > rotation_matrix[1, 1] and rotation_matrix[0, 0] > rotation_matrix[2, 2]:
            s = math.sqrt(1.0 + rotation_matrix[0, 0] - rotation_matrix[1, 1] - rotation_matrix[2, 2]) * 2
            qw = (rotation_matrix[2, 1] - rotation_matrix[1, 2]) / s
            qx = 0.25 * s
            qy = (rotation_matrix[0, 1] + rotation_matrix[1, 0]) / s
            qz = (rotation_matrix[0, 2] + rotation_matrix[2, 0]) / s
        elif rotation_matrix[1, 1] > rotation_matrix[2, 2]:
            s = math.sqrt(1.0 + rotation_matrix[1, 1] - rotation_matrix[0, 0] - rotation_matrix[2, 2]) * 2
            qw = (rotation_matrix[0, 2] - rotation_matrix[2, 0]) / s
            qx = (rotation_matrix[0, 1] + rotation_matrix[1, 0]) / s
            qy = 0.25 * s
            qz = (rotation_matrix[1, 2] + rotation_matrix[2, 1]) / s
        else:
            s = math.sqrt(1.0 + rotation_matrix[2, 2] - rotation_matrix[0, 0] - rotation_matrix[1, 1]) * 2
            qw = (rotation_matrix[1, 0] - rotation_matrix[0, 1]) / s
            qx = (rotation_matrix[0, 2] + rotation_matrix[2, 0]) / s
            qy = (rotation_matrix[1, 2] + rotation_matrix[2, 1]) / s
            qz = 0.25 * s
    
    new_orientation = Quaternion(x=qx, y=qy, z=qz, w=qw)
    
    return Pose(position=new_position, orientation=new_orientation)


def interpolate_poses(start_pose: Pose, end_pose: Pose, t: float) -> Pose:
    """
    Interpolate between two poses using linear interpolation for position
    and spherical linear interpolation (SLERP) for orientation.
    
    Args:
        start_pose: Starting pose
        end_pose: Ending pose
        t: Interpolation parameter between 0 and 1
        
    Returns:
        Interpolated pose
    """
    # Clamp t to [0, 1]
    t = max(0.0, min(1.0, t))
    
    # Linear interpolation for position
    interp_x = start_pose.position.x + t * (end_pose.position.x - start_pose.position.x)
    interp_y = start_pose.position.y + t * (end_pose.position.y - start_pose.position.y)
    interp_z = start_pose.position.z + t * (end_pose.position.z - start_pose.position.z)
    
    new_position = Point3D(x=interp_x, y=interp_y, z=interp_z)
    
    # SLERP for orientation
    q1 = [start_pose.orientation.x, start_pose.orientation.y, 
          start_pose.orientation.z, start_pose.orientation.w]
    q2 = [end_pose.orientation.x, end_pose.orientation.y, 
          end_pose.orientation.z, end_pose.orientation.w]
    
    # Calculate dot product
    dot = sum(a * b for a, b in zip(q1, q2))
    
    # If dot product is negative, negate one quaternion to take shorter path
    if dot < 0.0:
        q2 = [-x for x in q2]
        dot = -dot
    
    # If quaternions are very close, just linearly interpolate
    if dot > 0.9995:
        new_orientation = Quaternion(
            x=q1[0] + t * (q2[0] - q1[0]),
            y=q1[1] + t * (q2[1] - q1[1]),
            z=q1[2] + t * (q2[2] - q1[2]),
            w=q1[3] + t * (q2[3] - q1[3])
        )
        # Normalize the result
        norm = math.sqrt(new_orientation.x**2 + new_orientation.y**2 + 
                         new_orientation.z**2 + new_orientation.w**2)
        new_orientation.x /= norm
        new_orientation.y /= norm
        new_orientation.z /= norm
        new_orientation.w /= norm
    else:
        # Calculate angle between quaternions
        angle = math.acos(dot)
        sin_angle = math.sin(angle)
        
        # SLERP formula
        ratio_a = math.sin((1 - t) * angle) / sin_angle
        ratio_b = math.sin(t * angle) / sin_angle
        
        new_orientation = Quaternion(
            x=ratio_a * q1[0] + ratio_b * q2[0],
            y=ratio_a * q1[1] + ratio_b * q2[1],
            z=ratio_a * q1[2] + ratio_b * q2[2],
            w=ratio_a * q1[3] + ratio_b * q2[3]
        )
    
    return Pose(position=new_position, orientation=new_orientation)


def skew_symmetric_matrix(v: List[float]) -> np.ndarray:
    """
    Create a skew-symmetric matrix from a 3D vector.
    Used in various robotics calculations.
    
    Args:
        v: 3D vector [x, y, z]
        
    Returns:
        3x3 skew-symmetric matrix
    """
    return np.array([
        [0, -v[2], v[1]],
        [v[2], 0, -v[0]],
        [-v[1], v[0], 0]
    ])