# Quality of Service settings for ROS2 Nervous System
# This file defines the QoS profiles for different types of topics based on their requirements

from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSHistoryPolicy, QoSReliabilityPolicy


# Critical Control Topics
# Reliability: Reliable
# Durability: Volatile
# Deadline: 100ms
# Lifespan: 1s
# History: Keep last 1
CRITICAL_CONTROL_QOS = QoSProfile(
    reliability=QoSReliabilityPolicy.RELIABLE,
    durability=QoSDurabilityPolicy.VOLATILE,
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=1,
)

# Sensor Data Topics (for high-frequency sensors)
# Reliability: Best effort (for high-frequency sensors)
# Durability: Volatile
# History: Keep last 10
# Rate: Variable based on sensor frequency
SENSOR_DATA_QOS = QoSProfile(
    reliability=QoSReliabilityPolicy.BEST_EFFORT,
    durability=QoSDurabilityPolicy.VOLATILE,
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=10,
)

# Diagnostic Topics
# Reliability: Best effort
# Durability: Transient local
# History: Keep all
# Rate: 1Hz
DIAGNOSTIC_QOS = QoSProfile(
    reliability=QoSReliabilityPolicy.BEST_EFFORT,
    durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
    history=QoSHistoryPolicy.KEEP_ALL,
)

# Default QoS for general topics
DEFAULT_QOS = QoSProfile(
    reliability=QoSReliabilityPolicy.RELIABLE,
    durability=QoSDurabilityPolicy.VOLATILE,
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=10,
)


def get_qos_profile_for_topic(topic_name: str) -> QoSProfile:
    """
    Get the appropriate QoS profile for a given topic name.
    
    Args:
        topic_name: Name of the topic
        
    Returns:
        QoSProfile appropriate for the topic
    """
    if topic_name in ['/robot_command', '/robot_state']:
        return CRITICAL_CONTROL_QOS
    elif 'sensor' in topic_name or 'imu' in topic_name or 'lidar' in topic_name:
        return SENSOR_DATA_QOS
    elif topic_name == '/diagnostics':
        return DIAGNOSTIC_QOS
    else:
        return DEFAULT_QOS