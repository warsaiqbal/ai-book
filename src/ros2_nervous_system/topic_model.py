from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class Topic:
    """
    Represents a ROS topic - a named bus over which nodes exchange messages,
    enabling publisher-subscriber communication patterns.
    """
    id: str
    name: str
    message_type: str
    publisher_count: int = 0
    subscriber_count: int = 0
    bandwidth_usage: float = 0.0  # in bytes/second
    qos_profile: Optional[dict] = None  # Quality of Service settings
    creation_time: datetime = None
    
    def __post_init__(self):
        if self.creation_time is None:
            self.creation_time = datetime.now()
        if self.qos_profile is None:
            # Default QoS profile for ROS topics
            self.qos_profile = {
                'reliability': 'reliable',  # or 'best_effort'
                'durability': 'volatile',   # or 'transient_local'
                'history': 'keep_last',     # or 'keep_all'
                'depth': 10
            }
    
    @property
    def is_active(self) -> bool:
        """Check if topic has active publishers or subscribers"""
        return self.publisher_count > 0 or self.subscriber_count > 0
    
    def add_publisher(self) -> None:
        """Increment publisher count when a node starts publishing to this topic"""
        self.publisher_count += 1
    
    def remove_publisher(self) -> None:
        """Decrement publisher count when a node stops publishing to this topic"""
        if self.publisher_count > 0:
            self.publisher_count -= 1
    
    def add_subscriber(self) -> None:
        """Increment subscriber count when a node starts subscribing to this topic"""
        self.subscriber_count += 1
    
    def remove_subscriber(self) -> None:
        """Decrement subscriber count when a node stops subscribing to this topic"""
        if self.subscriber_count > 0:
            self.subscriber_count -= 1
    
    def update_bandwidth_usage(self, bytes_per_second: float) -> None:
        """Update the bandwidth usage for this topic"""
        self.bandwidth_usage = bytes_per_second
    
    def validate_topic_name(self) -> bool:
        """
        Validate that the topic name follows ROS naming conventions
        - Must start with a letter or underscore
        - Can only contain alphanumeric characters and underscores
        """
        import re
        # ROS topic names typically start with / and contain alphanumeric chars and underscores
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_/]*$|^[a-zA-Z0-9_/]+$'
        return bool(re.match(pattern, self.name.lstrip('/')))
    
    def validate_qos_settings(self) -> bool:
        """Validate that QoS settings are compatible between publishers and subscribers"""
        valid_reliability = ['reliable', 'best_effort']
        valid_durability = ['volatile', 'transient_local']
        valid_history = ['keep_last', 'keep_all']
        
        return (
            self.qos_profile['reliability'] in valid_reliability and
            self.qos_profile['durability'] in valid_durability and
            self.qos_profile['history'] in valid_history
        )