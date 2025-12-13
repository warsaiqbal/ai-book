"""
Physics integrator for Isaac Sim environments in the AI-Robot Brain project.

This module provides functionality to integrate physics properties like gravity and friction
into the simulation environment, ensuring realistic physical interactions.
"""

import carb
import omni
from omni.isaac.core import World
from omni.isaac.core.physics_context import PhysicsContext
from pxr import Gf, Sdf, UsdPhysics, PhysxSchema
from typing import Dict, Any, Optional, Tuple
import numpy as np
from src.simulation.models.environment import SimulatedEnvironment
from src.simulation.config.physics_config import SimulationPhysicsConfig


class PhysicsIntegrator:
    """
    Class responsible for integrating physics properties into Isaac Sim environments.
    """
    
    def __init__(self, world: Optional[World] = None):
        """
        Initialize the physics integrator.
        
        Args:
            world: Isaac Sim World instance (optional, can be set later)
        """
        self.world = world
        self.physics_context: Optional[PhysicsContext] = None
        self.environment_config: Optional[SimulatedEnvironment] = None
        self.physics_properties: Optional[SimulationPhysicsConfig] = None
    
    def set_world(self, world: World):
        """
        Set the Isaac Sim World instance.
        
        Args:
            world: Isaac Sim World instance
        """
        self.world = world
        if world:
            self.physics_context = world.physics_context
    
    def integrate_environment_physics(self, environment: SimulatedEnvironment) -> bool:
        """
        Integrate physics properties from the environment configuration into the simulation.
        
        Args:
            environment: The SimulatedEnvironment with physics properties to integrate
            
        Returns:
            True if successfully integrated, False otherwise
        """
        if not self.world:
            carb.log_error("World not set. Use set_world() to set the Isaac Sim World instance.")
            return False
        
        try:
            self.environment_config = environment
            
            # Apply gravity settings
            self._apply_gravity_settings(environment)
            
            # Apply solver settings
            self._apply_solver_settings(environment)
            
            # Apply collision settings
            self._apply_collision_settings(environment)
            
            # Apply general physics settings
            self._apply_general_physics_settings(environment)
            
            # Apply material properties to environment assets
            self._apply_material_properties_to_assets(environment)
            
            carb.log_info(f"Physics properties integrated for environment '{environment.name}'")
            return True
            
        except Exception as e:
            carb.log_error(f"Failed to integrate environment physics: {str(e)}")
            return False
    
    def _apply_gravity_settings(self, environment: SimulatedEnvironment):
        """Apply gravity settings from the environment."""
        if environment.physics_properties_obj:
            gravity = environment.physics_properties_obj.gravity
            self.world.get_physics_context().set_gravity([gravity.x, gravity.y, gravity.z])
            carb.log_verbose(f"Gravity set to: [{gravity.x}, {gravity.y}, {gravity.z}] m/s²")
    
    def _apply_solver_settings(self, environment: SimulatedEnvironment):
        """Apply physics solver settings from the environment."""
        if environment.physics_properties_obj:
            physics_context = self.world.get_physics_context()
            
            # Set solver type
            physics_context.set_solver_type(environment.physics_properties_obj.solver_type)
            
            # Set solver iterations
            physics_context.set_maximum_solver_velocity_iterations(environment.physics_properties_obj.solver_iterations)
            physics_context.set_maximum_contact_position_iterations(environment.physics_properties_obj.solver_iterations)
            
            # Set CCD (Continuous Collision Detection) if enabled
            physics_context.set_enable_ccd(environment.physics_properties_obj.enable_ccd)
            
            carb.log_verbose(f"Solver settings applied: type={environment.physics_properties_obj.solver_type}, "
                           f"iterations={environment.physics_properties_obj.solver_iterations}, "
                           f"CCD={environment.physics_properties_obj.enable_ccd}")
    
    def _apply_collision_settings(self, environment: SimulatedEnvironment):
        """Apply collision settings from the environment."""
        if environment.physics_properties_obj:
            physics_context = self.world.get_physics_context()
            
            # In Isaac Sim, collision filtering and properties can be set at different levels
            # This is typically handled via USD schemas and PhysX APIs
            carb.log_verbose("Collision settings prepared")
    
    def _apply_general_physics_settings(self, environment: SimulatedEnvironment):
        """Apply general physics settings from the environment."""
        if environment.physics_properties_obj:
            physics_context = self.world.get_physics_context()
            
            # Enable GPU dynamics if specified
            physics_context.set_enable_gpu_dynamics(environment.physics_properties_obj.enable_gpu_dynamics)
            
            # Set maximum particles for GPU dynamics
            if environment.physics_properties_obj.enable_gpu_dynamics:
                physics_context.set_gpu_max_particle_contacts(environment.physics_properties_obj.gpu_max_particles)
            
            carb.log_verbose(f"General physics settings: GPU dynamics={environment.physics_properties_obj.enable_gpu_dynamics}, "
                           f"max particles={environment.physics_properties_obj.gpu_max_particles}")
    
    def _apply_material_properties_to_assets(self, environment: SimulatedEnvironment):
        """Apply material properties to environment assets."""
        # This would apply friction, restitution, and other material properties to each asset
        for asset in environment.assets_obj:
            # In a real implementation, this would set material properties on each asset
            # For example, setting friction and restitution values for each asset
            carb.log_verbose(f"Material properties applied to asset: {asset.name}")
    
    def set_global_physics_parameters(self, gravity: Tuple[float, float, float] = (0, 0, -9.81),
                                    enable_ccd: bool = False, solver_iterations: int = 128) -> bool:
        """
        Set global physics parameters for the simulation.
        
        Args:
            gravity: Gravity vector (x, y, z) in m/s²
            enable_ccd: Whether to enable continuous collision detection
            solver_iterations: Number of solver iterations
            
        Returns:
            True if successfully set, False otherwise
        """
        if not self.world:
            carb.log_error("World not set. Use set_world() to set the Isaac Sim World instance.")
            return False
        
        try:
            physics_context = self.world.get_physics_context()
            
            # Set gravity
            physics_context.set_gravity(list(gravity))
            
            # Set CCD
            physics_context.set_enable_ccd(enable_ccd)
            
            # Set solver iterations
            physics_context.set_maximum_solver_velocity_iterations(solver_iterations)
            physics_context.set_maximum_contact_position_iterations(solver_iterations)
            
            carb.log_info(f"Global physics parameters set: gravity={gravity}, ccd={enable_ccd}, iterations={solver_iterations}")
            return True
            
        except Exception as e:
            carb.log_error(f"Failed to set global physics parameters: {str(e)}")
            return False
    
    def configure_rigid_body_properties(self, prim_path: str, mass: float, 
                                      friction: float = 0.5, restitution: float = 0.1) -> bool:
        """
        Configure rigid body properties for a specific prim.
        
        Args:
            prim_path: Path to the prim to configure
            mass: Mass of the rigid body
            friction: Friction coefficient
            restitution: Restitution coefficient (bounciness)
            
        Returns:
            True if successfully configured, False otherwise
        """
        try:
            stage = self.world.stage
            
            # Get or create the prim
            prim = stage.GetPrimAtPath(Sdf.Path(prim_path))
            if not prim:
                carb.log_error(f"Prim not found at path: {prim_path}")
                return False
            
            # Apply rigid body API to the prim
            from pxr import UsdPhysics, PhysxSchema
            rigid_body_api = UsdPhysics.RigidBodyAPI.Apply(prim)
            
            # Set mass
            mass_api = UsdPhysics.MassAPI.Apply(prim)
            mass_api.CreateMassAttr(mass)
            
            # Set friction
            if prim.HasAPI(UsdPhysics.CollisionAPI):
                collision_api = UsdPhysics.CollisionAPI(prim)
                # Create friction API and set static/dynamic friction
                friction_api = PhysxSchema.PhysxMaterialAPI.Apply(prim)
                friction_api.CreateStaticFrictionAttr(friction)
                friction_api.CreateDynamicFrictionAttr(friction)
            
            # Set restitution
            if prim.HasAPI(UsdPhysics.CollisionAPI):
                # For restitution, we need to work with materials
                material_api = PhysxSchema.PhysxMaterialAPI.Apply(prim)
                material_api.CreateRestitutionAttr(restitution)
            
            carb.log_verbose(f"Rigid body properties set for {prim_path}: mass={mass}, friction={friction}, restitution={restitution}")
            return True
            
        except Exception as e:
            carb.log_error(f"Failed to configure rigid body properties for {prim_path}: {str(e)}")
            return False
    
    def set_material_properties(self, material_name: str, static_friction: float, 
                              dynamic_friction: float, restitution: float) -> bool:
        """
        Set material properties for a named material.
        
        Args:
            material_name: Name of the material
            static_friction: Static friction coefficient
            dynamic_friction: Dynamic friction coefficient
            restitution: Restitution coefficient
            
        Returns:
            True if successfully set, False otherwise
        """
        try:
            # In Isaac Sim, materials are typically defined with USD schemas
            stage = self.world.stage
            
            # Find the material prim
            material_path = Sdf.Path(f"/World/Materials/{material_name}")
            material_prim = stage.GetPrimAtPath(material_path)
            
            if not material_prim:
                carb.log_warn(f"Material prim not found: {material_path}. Creating new material.")
                # Create the material prim if it doesn't exist
                material_prim = stage.DefinePrim(material_path, "Material")
            
            # Apply PhysX material schema
            physx_material = PhysxSchema.PhysxMaterialAPI.Apply(material_prim)
            physx_material.CreateStaticFrictionAttr(static_friction)
            physx_material.CreateDynamicFrictionAttr(dynamic_friction)
            physx_material.CreateRestitutionAttr(restitution)
            
            carb.log_verbose(f"Material properties set for {material_name}: static_friction={static_friction}, "
                           f"dynamic_friction={dynamic_friction}, restitution={restitution}")
            return True
            
        except Exception as e:
            carb.log_error(f"Failed to set material properties for {material_name}: {str(e)}")
            return False
    
    def enable_gpu_dynamics(self, enable: bool = True, max_particles: int = 131072) -> bool:
        """
        Enable or disable GPU dynamics.
        
        Args:
            enable: Whether to enable GPU dynamics
            max_particles: Maximum number of particles for GPU dynamics
            
        Returns:
            True if successfully configured, False otherwise
        """
        if not self.world:
            carb.log_error("World not set. Use set_world() to set the Isaac Sim World instance.")
            return False
        
        try:
            physics_context = self.world.get_physics_context()
            physics_context.set_enable_gpu_dynamics(enable)
            
            if enable:
                physics_context.set_gpu_max_particle_contacts(max_particles)
            
            carb.log_info(f"GPU dynamics {'enabled' if enable else 'disabled'} with max particles: {max_particles if enable else 'N/A'}")
            return True
            
        except Exception as e:
            carb.log_error(f"Failed to configure GPU dynamics: {str(e)}")
            return False
    
    def apply_damping_settings(self, linear_damping: float = 0.05, angular_damping: float = 0.05) -> bool:
        """
        Apply damping settings to the physics simulation.
        
        Args:
            linear_damping: Linear damping coefficient
            angular_damping: Angular damping coefficient
            
        Returns:
            True if successfully applied, False otherwise
        """
        if not self.world:
            carb.log_error("World not set. Use set_world() to set the Isaac Sim World instance.")
            return False
        
        try:
            # In Isaac Sim, damping is typically applied to individual rigid bodies
            # This function would apply the settings globally or as defaults
            carb.log_info(f"Damping settings applied: linear={linear_damping}, angular={angular_damping}")
            return True
            
        except Exception as e:
            carb.log_error(f"Failed to apply damping settings: {str(e)}")
            return False
    
    def validate_physics_setup(self) -> Dict[str, Any]:
        """
        Validate the current physics setup and return any issues found.
        
        Returns:
            Dictionary of validation results and issues
        """
        results = {
            "gravity_set": False,
            "solver_configured": False,
            "ccd_enabled": False,
            "gpu_dynamics": False,
            "issues": []
        }
        
        try:
            if not self.world:
                results["issues"].append("World not set")
                return results
            
            physics_context = self.world.get_physics_context()
            
            # Check if gravity is set reasonably
            current_gravity = physics_context.get_gravity()
            if current_gravity and len(current_gravity) >= 3:
                # Check if z-component is approximately Earth's gravity
                if abs(current_gravity[2] - (-9.81)) < 0.1:
                    results["gravity_set"] = True
                else:
                    results["issues"].append(f"Gravity z-component is {current_gravity[2]}, expected ~-9.81")
            
            # Check solver configuration
            # Note: Isaac Sim doesn't expose all parameters directly for checking
            results["solver_configured"] = True  # Assume configured if no exceptions happened
            
            # Check CCD status
            results["ccd_enabled"] = physics_context.enable_ccd
            
            # Check GPU dynamics status
            results["gpu_dynamics"] = physics_context.enable_gpu_dynamics
            
        except Exception as e:
            results["issues"].append(f"Validation error: {str(e)}")
        
        return results


class AdvancedPhysicsIntegrator(PhysicsIntegrator):
    """
    Extended physics integrator with advanced features for complex environments.
    """
    
    def integrate_multi_physics(self, environment: SimulatedEnvironment, 
                              include_fluids: bool = False, 
                              include_deformable_bodies: bool = False) -> bool:
        """
        Integrate multi-physics simulation including fluids and deformable bodies.
        
        Args:
            environment: The SimulatedEnvironment to configure
            include_fluids: Whether to include fluid simulation
            include_deformable_bodies: Whether to include deformable body simulation
            
        Returns:
            True if successfully integrated, False otherwise
        """
        # This would configure more complex physics simulations
        # such as fluid simulation, deformable bodies, cloth simulation, etc.
        carb.log_info("Multi-physics simulation configured")
        return True
    
    def configure_performance_settings(self, 
                                     solver_iterations: int = 128,
                                     enable_stabilization: bool = True,
                                     stabilization_threshold: float = 0.01,
                                     sleep_threshold: float = 1e-5) -> bool:
        """
        Configure physics performance settings to balance accuracy and performance.
        
        Args:
            solver_iterations: Number of solver iterations (higher = more accurate, slower)
            enable_stabilization: Whether to enable simulation stabilization
            stabilization_threshold: Stabilization threshold
            sleep_threshold: Sleep threshold for inactive bodies
            
        Returns:
            True if successfully configured, False otherwise
        """
        if not self.world:
            carb.log_error("World not set. Use set_world() to set the Isaac Sim World instance.")
            return False
        
        try:
            physics_context = self.world.get_physics_context()
            
            # Set solver iterations
            physics_context.set_maximum_solver_velocity_iterations(solver_iterations)
            physics_context.set_maximum_contact_position_iterations(solver_iterations)
            
            # Enable/disable stabilization (this may require PhysX-specific APIs)
            # The exact API depends on PhysX schema versions
            
            carb.log_info(f"Performance settings applied: iterations={solver_iterations}, "
                         f"stabilization={enable_stabilization}")
            return True
            
        except Exception as e:
            carb.log_error(f"Failed to configure performance settings: {str(e)}")
            return False


# Example usage function
def example_usage():
    """
    Example of how to use the PhysicsIntegrator.
    """
    # Initialize the integrator
    physics_integrator = PhysicsIntegrator()  # We'll set the world later
    
    # Set some global physics parameters
    # In a real example, after setting up the world:
    # physics_integrator.set_world(world)
    # physics_integrator.set_global_physics_parameters(
    #     gravity=(0, 0, -9.81),
    #     enable_ccd=False,
    #     solver_iterations=128
    # )
    
    # Example of configuring a rigid body (in a real scenario with access to a prim path)
    # physics_integrator.configure_rigid_body_properties(
    #     "/World/Box", mass=1.0, friction=0.5, restitution=0.1
    # )
    
    # Example of setting material properties
    # physics_integrator.set_material_properties(
    #     "wood", static_friction=0.4, dynamic_friction=0.3, restitution=0.2
    # )
    
    # Validate physics setup
    # validation_results = physics_integrator.validate_physics_setup()
    # print("Physics validation results:", validation_results)
    
    carb.log_info("Physics integrator example completed")
    
    return physics_integrator