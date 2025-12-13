from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional


@dataclass
class PythonAgent:
    """
    Represents an AI-based component written in Python that uses rclpy 
    to interface with ROS controllers.
    """
    id: str
    name: str
    algorithm_type: str  # Type of AI algorithm (e.g., reinforcement_learning, classical_control)
    status: str = 'inactive'  # Current operational status (active, inactive, paused)
    last_decision_time: Optional[datetime] = None
    subscribed_topics: List[str] = None  # List of ROS topics the agent subscribes to
    published_topics: List[str] = None  # List of ROS topics the agent publishes to
    connected_services: List[str] = None  # List of ROS services the agent can call
    performance_metrics: Dict[str, float] = None  # Dictionary of performance metrics
    creation_time: datetime = None
    
    def __post_init__(self):
        if self.creation_time is None:
            self.creation_time = datetime.now()
        if self.subscribed_topics is None:
            self.subscribed_topics = []
        if self.published_topics is None:
            self.published_topics = []
        if self.connected_services is None:
            self.connected_services = []
        if self.performance_metrics is None:
            self.performance_metrics = {}
    
    def activate_agent(self) -> None:
        """Set the agent status to active"""
        self.status = 'active'
        self.last_decision_time = datetime.now()
    
    def deactivate_agent(self) -> None:
        """Set the agent status to inactive"""
        self.status = 'inactive'
    
    def pause_agent(self) -> None:
        """Set the agent status to paused"""
        self.status = 'paused'
    
    def subscribe_to_topic(self, topic_name: str) -> None:
        """Add a topic to the list of subscribed topics"""
        if topic_name not in self.subscribed_topics:
            self.subscribed_topics.append(topic_name)
    
    def publish_to_topic(self, topic_name: str) -> None:
        """Add a topic to the list of published topics"""
        if topic_name not in self.published_topics:
            self.published_topics.append(topic_name)
    
    def connect_to_service(self, service_name: str) -> None:
        """Add a service to the list of connected services"""
        if service_name not in self.connected_services:
            self.connected_services.append(service_name)
    
    def update_performance_metric(self, metric_name: str, value: float) -> None:
        """Update a performance metric"""
        self.performance_metrics[metric_name] = value
    
    def validate_agent_type(self) -> bool:
        """Validate that algorithm type is a supported AI approach"""
        supported_types = [
            'reinforcement_learning', 'classical_control', 'model_predictive_control',
            'neural_network', 'rule_based', 'fuzzy_logic', 'genetic_algorithm'
        ]
        return self.algorithm_type in supported_types
    
    @property
    def is_valid(self) -> bool:
        """Check if this agent meets all validation requirements"""
        return (
            self.validate_agent_type() and
            self.status in ['active', 'inactive', 'paused']
        )
    
    @property
    def is_active(self) -> bool:
        """Check if the agent is currently active"""
        return self.status == 'active'