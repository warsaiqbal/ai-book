"""
State management system for the VLA system.
This module provides a centralized way to manage states across different components.
"""
import asyncio
import json
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar, Generic, Type
from dataclasses import dataclass, field
from enum import Enum

from ..models.data_models import (
    RobotState, ActionPlan, VoiceCommand, 
    EnvironmentalMap, DetectedObject, ExecutionContext
)


class StateType(Enum):
    """Enum for different types of states."""
    ROBOT = "robot"
    ACTION_PLAN = "action_plan"
    VOICE_COMMAND = "voice_command"
    ENVIRONMENTAL_MAP = "environmental_map"
    DETECTED_OBJECT = "detected_object"
    EXECUTION_CONTEXT = "execution_context"


@dataclass
class StateUpdate:
    """Represents an update to a state."""
    state_type: StateType
    state_id: str
    old_value: Optional[Any]
    new_value: Any
    timestamp: datetime
    source: str = "system"


T = TypeVar('T')


class StateManager(Generic[T]):
    """
    Generic state manager that handles different types of states.
    Provides thread-safe access to state data with event notifications.
    """
    
    def __init__(self):
        self._states: Dict[str, T] = {}
        self._state_lock = threading.Lock()  # Lock for thread safety
        self._subscribers: Dict[StateType, List[callable]] = {}
        self._update_history: List[StateUpdate] = []
        self._history_lock = threading.Lock()
    
    def set_state(self, state_id: str, state: T, source: str = "system", 
                  state_type: Optional[StateType] = None) -> bool:
        """
        Set a state with the given ID.
        
        Args:
            state_id: Unique identifier for the state
            state: The state object
            source: Source of the state update
            state_type: Type of the state (optional, used for notifications)
            
        Returns:
            True if state was updated, False otherwise
        """
        with self._state_lock:
            old_state = self._states.get(state_id)
            
            # Determine state type if not provided
            if state_type is None:
                if isinstance(state, RobotState):
                    actual_state_type = StateType.ROBOT
                elif isinstance(state, ActionPlan):
                    actual_state_type = StateType.ACTION_PLAN
                elif isinstance(state, VoiceCommand):
                    actual_state_type = StateType.VOICE_COMMAND
                elif isinstance(state, EnvironmentalMap):
                    actual_state_type = StateType.ENVIRONMENTAL_MAP
                elif isinstance(state, DetectedObject):
                    actual_state_type = StateType.DETECTED_OBJECT
                elif isinstance(state, ExecutionContext):
                    actual_state_type = StateType.EXECUTION_CONTEXT
                else:
                    # We can't determine the type, use a generic approach
                    actual_state_type = StateType.ROBOT  # Default fallback
            else:
                actual_state_type = state_type
            
            # Store the state
            self._states[state_id] = state
            
            # Create and store the update record
            update = StateUpdate(
                state_type=actual_state_type,
                state_id=state_id,
                old_value=old_state,
                new_value=state,
                timestamp=datetime.now(),
                source=source
            )
            
            with self._history_lock:
                self._update_history.append(update)
            
            # Notify subscribers of the state change
            self._notify_subscribers(actual_state_type, update)
            
            return True
    
    def get_state(self, state_id: str) -> Optional[T]:
        """
        Get a state by its ID.
        
        Args:
            state_id: Unique identifier for the state
            
        Returns:
            The state object or None if not found
        """
        with self._state_lock:
            return self._states.get(state_id)
    
    def get_all_states(self, state_type: Optional[StateType] = None) -> Dict[str, T]:
        """
        Get all states, optionally filtered by type.
        
        Args:
            state_type: Optional state type to filter by
            
        Returns:
            Dictionary of all states matching the type, or all states if no type specified
        """
        with self._state_lock:
            if state_type is None:
                return self._states.copy()
            
            # For specific state types, we'd need to check the actual state objects
            # which is not efficient. In a real implementation, we'd maintain separate
            # dictionaries for each state type.
            filtered_states = {}
            for state_id, state in self._states.items():
                actual_state_type = self._determine_state_type(state)
                if actual_state_type == state_type:
                    filtered_states[state_id] = state
            return filtered_states
    
    def remove_state(self, state_id: str) -> bool:
        """
        Remove a state by its ID.
        
        Args:
            state_id: Unique identifier for the state
            
        Returns:
            True if state was removed, False if it didn't exist
        """
        with self._state_lock:
            if state_id in self._states:
                del self._states[state_id]
                return True
            return False
    
    def has_state(self, state_id: str) -> bool:
        """
        Check if a state with the given ID exists.
        
        Args:
            state_id: Unique identifier for the state
            
        Returns:
            True if state exists, False otherwise
        """
        with self._state_lock:
            return state_id in self._states
    
    def subscribe_to_state_changes(self, state_type: StateType, callback: callable):
        """
        Subscribe to state changes of a specific type.
        
        Args:
            state_type: Type of state to subscribe to
            callback: Function to call when state changes
        """
        if state_type not in self._subscribers:
            self._subscribers[state_type] = []
        
        self._subscribers[state_type].append(callback)
    
    def get_state_history(self, state_id: Optional[str] = None, 
                         state_type: Optional[StateType] = None) -> List[StateUpdate]:
        """
        Get the history of state updates, optionally filtered by ID or type.
        
        Args:
            state_id: Optional state ID to filter by
            state_type: Optional state type to filter by
            
        Returns:
            List of state updates
        """
        with self._history_lock:
            filtered_history = self._update_history
            
            if state_id:
                filtered_history = [update for update in filtered_history if update.state_id == state_id]
            
            if state_type:
                filtered_history = [update for update in filtered_history if update.state_type == state_type]
            
            return filtered_history
    
    def _determine_state_type(self, state: Any) -> StateType:
        """Determine the state type from the state object."""
        if isinstance(state, RobotState):
            return StateType.ROBOT
        elif isinstance(state, ActionPlan):
            return StateType.ACTION_PLAN
        elif isinstance(state, VoiceCommand):
            return StateType.VOICE_COMMAND
        elif isinstance(state, EnvironmentalMap):
            return StateType.ENVIRONMENTAL_MAP
        elif isinstance(state, DetectedObject):
            return StateType.DETECTED_OBJECT
        elif isinstance(state, ExecutionContext):
            return StateType.EXECUTION_CONTEXT
        else:
            return StateType.ROBOT  # Default fallback
    
    def _notify_subscribers(self, state_type: StateType, update: StateUpdate):
        """Notify subscribers of a state change."""
        if state_type in self._subscribers:
            for callback in self._subscribers[state_type]:
                try:
                    # Call the callback in a separate thread to avoid blocking
                    # In a real implementation, this might use asyncio or a more sophisticated
                    # event system
                    callback(update)
                except Exception as e:
                    # Log the error but continue notifying other subscribers
                    import logging
                    logging.error(f"Error in state change callback: {e}")


class GlobalStateManager:
    """
    Global state manager singleton that provides access to state managers
    for different types of states.
    """
    
    def __init__(self):
        self._robot_state_manager = StateManager[RobotState]()
        self._action_plan_manager = StateManager[ActionPlan]()
        self._voice_command_manager = StateManager[VoiceCommand]()
        self._environmental_map_manager = StateManager[EnvironmentalMap]()
        self._detected_object_manager = StateManager[DetectedObject]()
        self._execution_context_manager = StateManager[ExecutionContext]()
        self._lock = threading.Lock()
    
    def get_robot_state_manager(self) -> StateManager[RobotState]:
        """Get the robot state manager."""
        return self._robot_state_manager
    
    def get_action_plan_manager(self) -> StateManager[ActionPlan]:
        """Get the action plan manager."""
        return self._action_plan_manager
    
    def get_voice_command_manager(self) -> StateManager[VoiceCommand]:
        """Get the voice command manager."""
        return self._voice_command_manager
    
    def get_environmental_map_manager(self) -> StateManager[EnvironmentalMap]:
        """Get the environmental map manager."""
        return self._environmental_map_manager
    
    def get_detected_object_manager(self) -> StateManager[DetectedObject]:
        """Get the detected object manager."""
        return self._detected_object_manager
    
    def get_execution_context_manager(self) -> StateManager[ExecutionContext]:
        """Get the execution context manager."""
        return self._execution_context_manager
    
    def save_to_file(self, filepath: str):
        """
        Save all states to a file in JSON format.
        
        Args:
            filepath: Path to save the states
        """
        with self._lock:
            all_states = {
                "robot_states": {k: v.dict() for k, v in self._robot_state_manager._states.items()},
                "action_plans": {k: v.dict() for k, v in self._action_plan_manager._states.items()},
                "voice_commands": {k: v.dict() for k, v in self._voice_command_manager._states.items()},
                "environmental_maps": {k: v.dict() for k, v in self._environmental_map_manager._states.items()},
                "detected_objects": {k: v.dict() for k, v in self._detected_object_manager._states.items()},
                "execution_contexts": {k: v.dict() for k, v in self._execution_context_manager._states.items()},
            }
            
            with open(filepath, 'w') as f:
                json.dump(all_states, f, indent=2, default=str)
    
    def load_from_file(self, filepath: str):
        """
        Load states from a JSON file.
        
        Args:
            filepath: Path to load the states from
        """
        with self._lock:
            with open(filepath, 'r') as f:
                all_states = json.load(f)
            
            # Clear existing states
            self._robot_state_manager._states.clear()
            self._action_plan_manager._states.clear()
            self._voice_command_manager._states.clear()
            self._environmental_map_manager._states.clear()
            self._detected_object_manager._states.clear()
            self._execution_context_manager._states.clear()
            
            # Load states back into their respective managers
            for state_id, state_data in all_states.get("robot_states", {}).items():
                self._robot_state_manager.set_state(state_id, RobotState(**state_data))
            
            for state_id, state_data in all_states.get("action_plans", {}).items():
                self._action_plan_manager.set_state(state_id, ActionPlan(**state_data))
            
            for state_id, state_data in all_states.get("voice_commands", {}).items():
                self._voice_command_manager.set_state(state_id, VoiceCommand(**state_data))
            
            for state_id, state_data in all_states.get("environmental_maps", {}).items():
                self._environmental_map_manager.set_state(state_id, EnvironmentalMap(**state_data))
            
            for state_id, state_data in all_states.get("detected_objects", {}).items():
                self._detected_object_manager.set_state(state_id, DetectedObject(**state_data))
            
            for state_id, state_data in all_states.get("execution_contexts", {}).items():
                self._execution_context_manager.set_state(state_id, ExecutionContext(**state_data))


# Global state manager instance
_global_state_manager = None


def get_global_state_manager() -> GlobalStateManager:
    """
    Get the global state manager instance.
    
    Returns:
        GlobalStateManager instance
    """
    global _global_state_manager
    if _global_state_manager is None:
        _global_state_manager = GlobalStateManager()
    return _global_state_manager