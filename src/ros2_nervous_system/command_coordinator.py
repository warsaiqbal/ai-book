"""
Coordination mechanisms for multiple Python agents to prevent conflicting commands
"""
import threading
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class CommandPriority(Enum):
    """Priority levels for commands"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class CommandInfo:
    """Information about a command sent by an agent"""
    agent_id: str
    command_type: str
    targets: List[str]  # Which joints/components this command affects
    priority: CommandPriority
    timestamp: float
    command_data: any  # The actual command message


class CommandCoordinator:
    """
    A coordination mechanism to prevent conflicting commands 
    from multiple agents trying to control the same robot components
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        self.active_commands: Dict[str, CommandInfo] = {}  # Key: target_component
        self.agent_priorities: Dict[str, CommandPriority] = {}
        self.command_queue: List[CommandInfo] = []
        
    def register_agent(self, agent_id: str, priority: CommandPriority = CommandPriority.NORMAL):
        """Register an agent with the coordinator"""
        with self._lock:
            self.agent_priorities[agent_id] = priority
    
    def can_execute_command(self, agent_id: str, targets: List[str], priority: CommandPriority) -> Tuple[bool, str]:
        """
        Check if a command can be executed without conflicting with active commands
        Returns (can_execute, reason)
        """
        with self._lock:
            # Check if any target is currently being controlled by a higher or equal priority agent
            for target in targets:
                if target in self.active_commands:
                    active_cmd = self.active_commands[target]
                    
                    # If the same agent is trying to control the same target again, allow it
                    if active_cmd.agent_id == agent_id:
                        continue
                    
                    # If the requesting agent has lower priority, deny
                    if priority.value < active_cmd.priority.value:
                        return False, f"Target {target} is controlled by higher priority agent {active_cmd.agent_id}"
                    
                    # If same priority, handle based on time or other factors
                    if priority.value == active_cmd.priority.value:
                        # For same priority, we could implement round-robin or other policies
                        # For now, deny to prevent conflicts
                        return False, f"Target {target} is already controlled by agent {active_cmd.agent_id} at same priority"
            
            return True, "Command can be executed"
    
    def submit_command(self, agent_id: str, command_type: str, targets: List[str], 
                      command_data: any, priority: CommandPriority = CommandPriority.NORMAL) -> bool:
        """
        Submit a command for execution after checking for conflicts
        """
        can_execute, reason = self.can_execute_command(agent_id, targets, priority)
        
        if not can_execute:
            print(f"Command from {agent_id} denied: {reason}")
            return False
        
        # Register the command as active
        with self._lock:
            command_info = CommandInfo(
                agent_id=agent_id,
                command_type=command_type,
                targets=targets,
                priority=priority,
                timestamp=time.time(),
                command_data=command_data
            )
            
            # Mark targets as actively controlled
            for target in targets:
                self.active_commands[target] = command_info
        
        print(f"Command from {agent_id} registered for targets: {targets}")
        return True
    
    def complete_command(self, agent_id: str, targets: List[str]):
        """Mark a command as completed and release control of targets"""
        with self._lock:
            for target in targets:
                if target in self.active_commands and self.active_commands[target].agent_id == agent_id:
                    del self.active_commands[target]
        
        print(f"Command completed for {agent_id} on targets: {targets}")
    
    def get_active_controller(self, target: str) -> Optional[str]:
        """Get the agent currently controlling a specific target"""
        with self._lock:
            if target in self.active_commands:
                return self.active_commands[target].agent_id
            return None

    def get_conflicting_targets(self, agent_id: str, targets: List[str]) -> List[str]:
        """Get a list of targets that would conflict with currently active commands"""
        conflicts = []
        with self._lock:
            for target in targets:
                if target in self.active_commands and self.active_commands[target].agent_id != agent_id:
                    conflicts.append(target)
        return conflicts


# Global coordinator instance
_command_coordinator = None
_coordinator_lock = threading.Lock()


def get_command_coordinator() -> CommandCoordinator:
    """Get or create the singleton command coordinator instance"""
    global _command_coordinator
    
    with _coordinator_lock:
        if _command_coordinator is None:
            _command_coordinator = CommandCoordinator()
        
        return _command_coordinator


def cleanup_coordinator():
    """Clean up the coordinator instance"""
    global _command_coordinator
    
    with _coordinator_lock:
        _command_coordinator = None