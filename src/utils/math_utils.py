"""
Utility functions for vector and quaternion operations.

This module provides mathematical utilities for 3D geometry operations
needed throughout the AI-Robot Brain system.
"""

from typing import Tuple, Union
import math


def vector3_magnitude(x: float, y: float, z: float) -> float:
    """Calculate the magnitude of a 3D vector."""
    return math.sqrt(x*x + y*y + z*z)


def vector3_normalize(x: float, y: float, z: float) -> Tuple[float, float, float]:
    """Normalize a 3D vector to unit length."""
    mag = vector3_magnitude(x, y, z)
    if mag == 0:
        return (0.0, 0.0, 0.0)
    return (x/mag, y/mag, z/mag)


def vector3_dot(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> float:
    """Calculate the dot product of two 3D vectors."""
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]


def vector3_cross(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """Calculate the cross product of two 3D vectors."""
    return (
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0]
    )


def quaternion_multiply(q1: Tuple[float, float, float, float], q2: Tuple[float, float, float, float]) -> Tuple[float, float, float, float]:
    """Multiply two quaternions."""
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    
    w = w1*w2 - x1*x2 - y1*y2 - z1*z2
    x = w1*x2 + x1*w2 + y1*z2 - z1*y2
    y = w1*y2 - x1*z2 + y1*w2 + z1*x2
    z = w1*z2 + x1*y2 - y1*x2 + z1*w2
    
    return (w, x, y, z)


def quaternion_normalize(q: Tuple[float, float, float, float]) -> Tuple[float, float, float, float]:
    """Normalize a quaternion to unit length."""
    w, x, y, z = q
    mag = math.sqrt(w*w + x*x + y*y + z*z)
    if mag == 0:
        return (1.0, 0.0, 0.0, 0.0)
    return (w/mag, x/mag, y/mag, z/mag)


def quaternion_to_euler(q: Tuple[float, float, float, float]) -> Tuple[float, float, float]:
    """Convert a quaternion to Euler angles (roll, pitch, yaw)."""
    w, x, y, z = q
    
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


def euler_to_quaternion(roll: float, pitch: float, yaw: float) -> Tuple[float, float, float, float]:
    """Convert Euler angles (roll, pitch, yaw) to a quaternion."""
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)
    
    w = cr * cp * cy + sr * sp * sy
    x = sr * cp * cy - cr * sp * sy
    y = cr * sp * cy + sr * cp * sy
    z = cr * cp * sy - sr * sp * cy
    
    return (w, x, y, z)


def quaternion_rotate_vector(q: Tuple[float, float, float, float], v: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """Rotate a 3D vector by a quaternion."""
    # Convert vector to quaternion
    v_quat = (0.0, v[0], v[1], v[2])
    
    # Conjugate of q
    q_conj = (q[0], -q[1], -q[2], -q[3])
    
    # Rotate: q * v * q_conj
    temp = quaternion_multiply(v_quat, q_conj)
    rotated = quaternion_multiply(q, temp)
    
    # Extract the vector part
    return (rotated[1], rotated[2], rotated[3])


def transform_point(point: Tuple[float, float, float], 
                   translation: Tuple[float, float, float], 
                   rotation: Tuple[float, float, float, float]) -> Tuple[float, float, float]:
    """Transform a point with translation and rotation."""
    # First rotate the point by the quaternion
    rotated_point = quaternion_rotate_vector(rotation, point)
    
    # Then translate
    return (
        rotated_point[0] + translation[0],
        rotated_point[1] + translation[1],
        rotated_point[2] + translation[2]
    )


def pose_to_transform_matrix(pose) -> list:
    """
    Convert a Pose object to a 4x4 transformation matrix.
    
    Args:
        pose: A Pose object with position (Vector3) and orientation (Quaternion)
        
    Returns:
        A 4x4 transformation matrix as a list of 16 elements
    """
    # Convert quaternion to rotation matrix
    w, x, y, z = pose.orientation.w, pose.orientation.x, pose.orientation.y, pose.orientation.z
    
    # Calculate rotation matrix elements
    r11 = 1 - 2*(y*y + z*z)
    r12 = 2*(x*y - w*z)
    r13 = 2*(x*z + w*y)
    
    r21 = 2*(x*y + w*z)
    r22 = 1 - 2*(x*x + z*z)
    r23 = 2*(y*z - w*x)
    
    r31 = 2*(x*z - w*y)
    r32 = 2*(y*z + w*x)
    r33 = 1 - 2*(x*x + y*y)
    
    # Translation components
    tx, ty, tz = pose.position.x, pose.position.y, pose.position.z
    
    # Return 4x4 transformation matrix as a list
    return [
        r11, r12, r13, tx,
        r21, r22, r23, ty,
        r31, r32, r33, tz,
        0.0, 0.0, 0.0, 1.0
    ]


def calculate_distance_3d(p1: Tuple[float, float, float], p2: Tuple[float, float, float]) -> float:
    """Calculate the Euclidean distance between two 3D points."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dz = p2[2] - p1[2]
    return math.sqrt(dx*dx + dy*dy + dz*dz)


def calculate_yaw_angle(from_point: Tuple[float, float, float], to_point: Tuple[float, float, float]) -> float:
    """Calculate the yaw angle from one point to another in the XY plane."""
    dx = to_point[0] - from_point[0]
    dy = to_point[1] - from_point[1]
    return math.atan2(dy, dx)


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max."""
    return max(min_val, min(value, max_val))


def lerp(start: float, end: float, t: float) -> float:
    """Linearly interpolate between start and end by t (0.0 to 1.0)."""
    return start + t * (end - start)


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    """Smooth step function for smooth interpolation."""
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def angle_difference(angle1: float, angle2: float) -> float:
    """Calculate the shortest angular difference between two angles in radians."""
    diff = angle2 - angle1
    while diff > math.pi:
        diff -= 2 * math.pi
    while diff < -math.pi:
        diff += 2 * math.pi
    return diff


def wrap_angle(angle: float) -> float:
    """Wrap an angle to the range [-π, π]."""
    while angle > math.pi:
        angle -= 2 * math.pi
    while angle <= -math.pi:
        angle += 2 * math.pi
    return angle