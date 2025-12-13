"""
Logging and monitoring system for the Vision-Language-Action (VLA) robotics project.

This module provides centralized logging and monitoring capabilities for all
components of the VLA system. It includes structured logging, performance
monitoring, and health checks for the various system components.
"""

import logging
import logging.config
import os
import sys
import time
import json
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import psutil
import GPUtil
from pathlib import Path


class LogLevel(Enum):
    """Enumeration of logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ComponentType(Enum):
    """Enumeration of system component types."""
    VOICE_INTERFACE = "voice_interface"
    COGNITIVE_PLANNING = "cognitive_planning"
    EXECUTION = "execution"
    PERCEPTION = "perception"
    SIMULATION = "simulation"
    ROS_NODE = "ros_node"
    LLM_INTEGRATION = "llm_integration"
    SYSTEM = "system"


@dataclass
class LogRecord:
    """Structured log record with standardized fields."""
    timestamp: float
    level: str
    component: str
    event: str
    message: str
    details: Dict[str, Any]
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    robot_id: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class PerformanceMetric:
    """Performance metric record."""
    name: str
    value: float
    unit: str
    timestamp: float
    component: str
    robot_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp,
            "component": self.component,
            "robot_id": self.robot_id,
            "session_id": self.session_id,
            "metadata": self.metadata or {}
        }


@dataclass
class HealthStatus:
    """System health status report."""
    component: str
    status: str  # "healthy", "degraded", "unhealthy", "unknown"
    timestamp: float
    details: Dict[str, Any]
    robot_id: Optional[str] = None
    uptime: Optional[float] = None  # seconds
    error_count: int = 0
    warning_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


class VLAEventLogger:
    """
    Centralized event logger for the VLA system with structured logging.
    """
    
    def __init__(self, log_dir: str = "./logs", level: LogLevel = LogLevel.INFO):
        """
        Initialize the VLA event logger.
        
        Args:
            log_dir: Directory to store log files
            level: Minimum logging level to record
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.level = level
        self.logger = self._setup_logger()
        self.component_loggers: Dict[str, logging.Logger] = {}
        self.session_id = self._generate_session_id()
        
        # Performance tracking
        self.metrics: List[PerformanceMetric] = []
        self.metric_lock = threading.Lock()
        
        # Health tracking
        self.health_status: Dict[str, HealthStatus] = {}
        self.health_lock = threading.Lock()
    
    def _setup_logger(self) -> logging.Logger:
        """Set up the main logger with file and console handlers."""
        logger = logging.getLogger("vla_system")
        logger.setLevel(getattr(logging, self.level.value))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatters
        json_formatter = logging.Formatter('%(message)s')
        console_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, self.level.value))
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler
        log_file = self.log_dir / f"vla_system_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, self.level.value))
        file_handler.setFormatter(json_formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        import uuid
        return str(uuid.uuid4())
    
    def get_component_logger(self, component_type: ComponentType) -> logging.Logger:
        """
        Get a logger for a specific component type.
        
        Args:
            component_type: Type of the component
            
        Returns:
            Logger instance for the component
        """
        if component_type.value not in self.component_loggers:
            component_logger = logging.getLogger(f"vla_system.{component_type.value}")
            component_logger.setLevel(getattr(logging, self.level.value))
            
            # Use the same handlers as the main logger
            for handler in self.logger.handlers:
                component_logger.addHandler(handler)
            
            # Prevent propagation to avoid duplicate logs
            component_logger.propagate = False
            self.component_loggers[component_type.value] = component_logger
        
        return self.component_loggers[component_type.value]
    
    def log_event(self, 
                  level: LogLevel, 
                  component: ComponentType, 
                  event: str, 
                  message: str, 
                  details: Dict[str, Any] = None,
                  user_id: Optional[str] = None,
                  robot_id: Optional[str] = None,
                  trace_id: Optional[str] = None) -> None:
        """
        Log an event with structured information.
        
        Args:
            level: Log level
            component: Component that generated the event
            event: Event type (e.g., "voice_command_received", "action_planned")
            message: Human-readable message
            details: Additional structured details
            user_id: ID of the user involved
            robot_id: ID of the robot involved
            trace_id: Trace ID for distributed tracing
        """
        log_record = LogRecord(
            timestamp=time.time(),
            level=level.value,
            component=component.value,
            event=event,
            message=message,
            details=details or {},
            user_id=user_id,
            session_id=self.session_id,
            robot_id=robot_id,
            trace_id=trace_id,
            span_id=None
        )
        
        component_logger = self.get_component_logger(component)
        component_logger.log(
            getattr(logging, level.value),
            log_record.to_json()
        )
    
    def log_debug(self, component: ComponentType, event: str, message: str, **kwargs):
        """Log a debug level event."""
        self.log_event(LogLevel.DEBUG, component, event, message, kwargs)
    
    def log_info(self, component: ComponentType, event: str, message: str, **kwargs):
        """Log an info level event."""
        self.log_event(LogLevel.INFO, component, event, message, kwargs)
    
    def log_warning(self, component: ComponentType, event: str, message: str, **kwargs):
        """Log a warning level event."""
        self.log_event(LogLevel.WARNING, component, event, message, kwargs)
    
    def log_error(self, component: ComponentType, event: str, message: str, **kwargs):
        """Log an error level event."""
        self.log_event(LogLevel.ERROR, component, event, message, kwargs)
    
    def log_critical(self, component: ComponentType, event: str, message: str, **kwargs):
        """Log a critical level event."""
        self.log_event(LogLevel.CRITICAL, component, event, message, kwargs)
    
    def record_metric(self, name: str, value: float, unit: str, component: ComponentType,
                      robot_id: Optional[str] = None, metadata: Dict[str, Any] = None) -> None:
        """
        Record a performance metric.
        
        Args:
            name: Name of the metric
            value: Value of the metric
            unit: Unit of the metric
            component: Component associated with the metric
            robot_id: ID of the robot (if applicable)
            metadata: Additional metadata about the metric
        """
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=time.time(),
            component=component.value,
            robot_id=robot_id,
            session_id=self.session_id,
            metadata=metadata
        )
        
        with self.metric_lock:
            self.metrics.append(metric)
    
    def get_recent_metrics(self, name: str = None, component: str = None, 
                          hours: float = 1.0) -> List[PerformanceMetric]:
        """
        Get recent metrics, optionally filtered by name, component, or time window.
        
        Args:
            name: Name of the metric to filter by
            component: Component to filter by
            hours: Time window in hours to look back
            
        Returns:
            List of matching metrics
        """
        cutoff_time = time.time() - (hours * 3600)
        
        with self.metric_lock:
            filtered_metrics = [
                m for m in self.metrics
                if m.timestamp >= cutoff_time and
                (name is None or m.name == name) and
                (component is None or m.component == component)
            ]
        
        return filtered_metrics
    
    def update_health_status(self, component: str, status: str, details: Dict[str, Any],
                             robot_id: Optional[str] = None) -> None:
        """
        Update the health status of a component.
        
        Args:
            component: Name of the component
            status: Health status ("healthy", "degraded", "unhealthy", "unknown")
            details: Additional details about the health status
            robot_id: ID of the robot (if applicable)
        """
        health_status = HealthStatus(
            component=component,
            status=status,
            timestamp=time.time(),
            details=details,
            robot_id=robot_id
        )
        
        with self.health_lock:
            self.health_status[component] = health_status
    
    def get_health_status(self, component: str) -> Optional[HealthStatus]:
        """
        Get the health status of a specific component.
        
        Args:
            component: Name of the component
            
        Returns:
            Health status of the component or None if not found
        """
        with self.health_lock:
            return self.health_status.get(component)
    
    def get_all_health_status(self) -> Dict[str, HealthStatus]:
        """
        Get health status for all components.
        
        Returns:
            Dictionary mapping component names to their health status
        """
        with self.health_lock:
            return self.health_status.copy()
    
    def check_system_health(self) -> Dict[str, Any]:
        """
        Perform a comprehensive system health check.
        
        Returns:
            Dictionary with overall health status and details for each component
        """
        # Gather system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        
        # Check if GPUs are available and their utilization
        gpu_info = []
        try:
            gpus = GPUtil.getGPUs()
            for gpu in gpus:
                gpu_info.append({
                    'id': gpu.id,
                    'name': gpu.name,
                    'load': gpu.load * 100,
                    'memory_util': gpu.memoryUtil * 100,
                    'temperature': gpu.temperature
                })
        except:
            # GPU utilities not available
            gpu_info = [{'available': False}]
        
        system_health = {
            'timestamp': time.time(),
            'system_metrics': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_usage_percent': disk_usage,
                'gpu_info': gpu_info
            },
            'component_health': self.get_all_health_status(),
            'overall_status': 'healthy'  # Determined based on individual component status
        }
        
        # Determine overall status based on critical components
        critical_components = ['voice_interface', 'cognitive_planning', 'execution']
        unhealthy_count = 0
        
        for comp_name, comp_health in system_health['component_health'].items():
            if comp_health.status == 'unhealthy':
                if comp_name in critical_components:
                    system_health['overall_status'] = 'critical'
                    break
                else:
                    unhealthy_count += 1
                    
        if system_health['overall_status'] == 'healthy' and unhealthy_count > 0:
            system_health['overall_status'] = 'degraded'
        
        return system_health


class MonitoringDashboard:
    """
    Simple monitoring dashboard that aggregates metrics for visualization.
    """
    
    def __init__(self, logger: VLAEventLogger):
        """
        Initialize the monitoring dashboard.
        
        Args:
            logger: VLAEventLogger instance to get metrics from
        """
        self.logger = logger
        self.metrics_callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self.dashboard_data: Dict[str, Any] = {}
        self.refresh_interval = 5  # seconds
        self.monitoring_thread = None
        self.monitoring_active = False
    
    def start_monitoring(self):
        """Start the monitoring thread."""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """Stop the monitoring thread."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
    
    def _monitoring_loop(self):
        """Main monitoring loop that periodically collects metrics."""
        while self.monitoring_active:
            try:
                # Collect all metrics
                self.dashboard_data = self._collect_dashboard_data()
                
                # Notify any registered callbacks
                for callback in self.metrics_callbacks:
                    try:
                        callback(self.dashboard_data)
                    except Exception as e:
                        self.logger.log_error(
                            ComponentType.SYSTEM,
                            "dashboard_callback_error",
                            f"Error in dashboard callback: {str(e)}"
                        )
                
                time.sleep(self.refresh_interval)
                
            except Exception as e:
                self.logger.log_error(
                    ComponentType.SYSTEM,
                    "monitoring_loop_error",
                    f"Error in monitoring loop: {str(e)}"
                )
                time.sleep(self.refresh_interval)
    
    def _collect_dashboard_data(self) -> Dict[str, Any]:
        """Collect data for the dashboard."""
        system_health = self.logger.check_system_health()
        
        # Get recent performance metrics
        recent_metrics = self.logger.get_recent_metrics(hours=0.1)  # Last 6 minutes
        
        # Organize metrics by component
        component_metrics = {}
        for metric in recent_metrics:
            if metric.component not in component_metrics:
                component_metrics[metric.component] = []
            component_metrics[metric.component].append({
                'name': metric.name,
                'value': metric.value,
                'unit': metric.unit,
                'timestamp': metric.timestamp,
                'metadata': metric.metadata
            })
        
        return {
            'system_health': system_health,
            'component_metrics': component_metrics,
            'timestamp': time.time()
        }
    
    def add_metrics_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Add a callback to be notified when metrics are updated.
        
        Args:
            callback: Function that takes dashboard data as argument
        """
        self.metrics_callbacks.append(callback)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get the current dashboard data.
        
        Returns:
            Current dashboard data
        """
        return self.dashboard_data.copy()


# Global logger instance
_vla_logger: Optional[VLAEventLogger] = None


def get_logger() -> VLAEventLogger:
    """
    Get the global VLA event logger instance.
    
    Returns:
        Global logger instance
    """
    global _vla_logger
    if _vla_logger is None:
        _vla_logger = VLAEventLogger()
    return _vla_logger


def setup_logging(level: LogLevel = LogLevel.INFO, log_dir: str = "./logs") -> VLAEventLogger:
    """
    Set up the VLA logging system.
    
    Args:
        level: Minimum logging level
        log_dir: Directory to store logs
        
    Returns:
        Configured logger instance
    """
    global _vla_logger
    _vla_logger = VLAEventLogger(log_dir=log_dir, level=level)
    return _vla_logger


# Convenience functions for common logging tasks
def log_voice_event(event: str, message: str, **kwargs):
    """Log an event from the voice interface component."""
    logger = get_logger()
    logger.log_info(ComponentType.VOICE_INTERFACE, event, message, **kwargs)


def log_planning_event(event: str, message: str, **kwargs):
    """Log an event from the cognitive planning component."""
    logger = get_logger()
    logger.log_info(ComponentType.COGNITIVE_PLANNING, event, message, **kwargs)


def log_execution_event(event: str, message: str, **kwargs):
    """Log an event from the execution component."""
    logger = get_logger()
    logger.log_info(ComponentType.EXECUTION, event, message, **kwargs)


def log_perception_event(event: str, message: str, **kwargs):
    """Log an event from the perception component."""
    logger = get_logger()
    logger.log_info(ComponentType.PERCEPTION, event, message, **kwargs)


def log_system_event(event: str, message: str, **kwargs):
    """Log an event from the system component."""
    logger = get_logger()
    logger.log_info(ComponentType.SYSTEM, event, message, **kwargs)


# Example usage
def example_usage():
    """
    Example of how to use the VLA logging and monitoring system.
    """
    # Initialize logger
    logger = setup_logging(LogLevel.INFO)
    
    # Log some events
    logger.log_info(ComponentType.VOICE_INTERFACE, "voice_command_received", 
                   "Received voice command from user", 
                   user_id="user_123", 
                   command_text="Move to the kitchen")
    
    logger.log_info(ComponentType.COGNITIVE_PLANNING, "plan_generated", 
                   "Generated action plan from natural language command",
                   plan_steps=5,
                   estimated_duration=120.5)
    
    # Record performance metrics
    logger.record_metric("voice_transcription_accuracy", 0.92, "ratio", 
                        ComponentType.VOICE_INTERFACE)
    logger.record_metric("planning_response_time", 1.2, "seconds", 
                        ComponentType.COGNITIVE_PLANNING)
    
    # Update health status
    logger.update_health_status("voice_interface", "healthy", {
        "last_command_time": time.time(),
        "active_sessions": 1
    })
    
    # Check system health
    health = logger.check_system_health()
    print("System health:", json.dumps(health, indent=2))
    
    # Set up monitoring dashboard
    dashboard = MonitoringDashboard(logger)
    dashboard.start_monitoring()
    
    # Run for a few seconds to collect metrics
    time.sleep(10)
    
    # Stop monitoring
    dashboard.stop_monitoring()
    
    print("Example usage completed")


if __name__ == "__main__":
    example_usage()