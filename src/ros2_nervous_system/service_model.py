from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Service:
    """
    Represents a ROS service - a synchronous request-response communication 
    pattern between nodes for direct interaction.
    """
    id: str
    name: str
    service_type: str
    node_id: str  # ID of the node providing this service
    request_count: int = 0
    success_rate: float = 100.0  # Percentage of successful requests
    average_response_time: float = 0.0  # Average time to respond to requests in seconds
    creation_time: datetime = None
    
    def __post_init__(self):
        if self.creation_time is None:
            self.creation_time = datetime.now()
    
    def record_request(self, success: bool, response_time: float) -> None:
        """Record a service request and its outcome"""
        self.request_count += 1
        
        # Update success rate (simple moving average approach)
        total_successes = (self.success_rate / 100.0) * (self.request_count - 1)
        if success:
            total_successes += 1
        self.success_rate = (total_successes / self.request_count) * 100.0
        
        # Update average response time (simple moving average approach)
        prev_total_time = self.average_response_time * (self.request_count - 1)
        self.average_response_time = (prev_total_time + response_time) / self.request_count
    
    def validate_service_name(self) -> bool:
        """
        Validate that the service name follows ROS naming conventions
        - Must start with a letter or underscore
        - Can only contain alphanumeric characters and underscores
        """
        import re
        # ROS service names typically start with / and contain alphanumeric chars and underscores
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_/]*$|^[a-zA-Z0-9_/]+$'
        return bool(re.match(pattern, self.name.lstrip('/')))
    
    def validate_service_type(self) -> bool:
        """Validate that service type is a valid ROS 2 service type"""
        # Basic validation - in practice, this would check against registered service types
        valid_service_type_pattern = r'^[a-zA-Z][a-zA-Z0-9_]*(\/[a-zA-Z][a-zA-Z0-9_]*){2}$'
        return bool(re.match(valid_service_type_pattern, self.service_type))
    
    @property
    def is_valid(self) -> bool:
        """Check if this service meets all validation requirements"""
        return (
            self.validate_service_name() and 
            self.validate_service_type() and 
            0 <= self.success_rate <= 100
        )