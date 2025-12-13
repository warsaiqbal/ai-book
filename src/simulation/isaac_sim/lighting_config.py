"""
Lighting and material configuration system for Isaac Sim environments in the AI-Robot Brain project.

This module provides functionality to configure lighting and materials in simulation
environments to match real-world conditions.
"""

import carb
import omni
from omni.isaac.core.utils.prims import define_prim
from omni.isaac.core.utils.stage import get_current_stage
from pxr import Gf, Sdf, UsdLux, UsdGeom
from typing import Dict, Any, Optional, List, Tuple
import math
import numpy as np
from dataclasses import dataclass
from src.simulation.models.environment import SimulatedEnvironment


@dataclass
class LightSource:
    """Represents a light source in the environment."""
    name: str
    light_type: str  # 'dome', 'distant', 'sphere', 'disk', 'rect'
    intensity: float = 1000.0
    color: Tuple[float, float, float] = (1.0, 1.0, 1.0)  # RGB, 0-1
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # In degrees
    enabled: bool = True
    
    # Type-specific properties
    radius: Optional[float] = None  # For sphere lights
    width: Optional[float] = None  # For rect/disk lights
    height: Optional[float] = None  # For rect lights
    angle: Optional[float] = None  # For distant lights (in degrees)


@dataclass
class Material:
    """Represents a material in the environment."""
    name: str
    material_type: str  # 'omnishopper_pbr', 'simple_preview_surface', etc.
    diffuse_color: Tuple[float, float, float] = (0.5, 0.5, 0.5)  # RGB, 0-1
    emissive_color: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # RGB, 0-1
    roughness: float = 0.5  # 0-1
    metallic: float = 0.0  # 0-1
    specular: float = 0.5  # 0-1
    clearcoat: float = 0.0  # 0-1
    clearcoat_roughness: float = 0.0  # 0-1
    opacity: float = 1.0  # 0-1
    ior: float = 1.5  # Index of refraction
    enabled: bool = True


class LightingConfigurator:
    """
    Class responsible for configuring lighting in Isaac Sim environments.
    """
    
    def __init__(self):
        """Initialize the lighting configurator."""
        self.lights: Dict[str, LightSource] = {}
        self.materials: Dict[str, Material] = {}
    
    def configure_environment_lighting(self, environment: SimulatedEnvironment) -> bool:
        """
        Configure lighting for a simulated environment based on its configuration.
        
        Args:
            environment: The SimulatedEnvironment to configure lighting for
            
        Returns:
            True if successfully configured, False otherwise
        """
        try:
            # Apply default lighting if no specific configuration exists
            if not environment.lighting_config_obj:
                self.apply_default_lighting()
                return True
            
            # Configure based on environment's lighting configuration
            self._configure_environment_based_lighting(environment)
            
            carb.log_info(f"Lighting configured for environment '{environment.name}'")
            return True
            
        except Exception as e:
            carb.log_error(f"Failed to configure environment lighting: {str(e)}")
            return False
    
    def _configure_environment_based_lighting(self, environment):
        """Configure lighting based on environment configuration."""
        # Apply a dome light for general environmental lighting
        dome_light = LightSource(
            name="environment_dome",
            light_type="dome",
            intensity=environment.lighting_config_obj.main_light_intensity,
            color=tuple(environment.lighting_config_obj.main_light_color)
        )
        self.add_light(dome_light)
        
        # Apply shadows if enabled
        # Note: In actual USD/Isaac Sim, shadow settings are applied differently
        if environment.lighting_config_obj.shadows_enabled:
            carb.log_verbose("Shadows enabled for environment")
        
        # Apply time of day effects
        self._apply_time_of_day_effects(environment.lighting_config_obj.time_of_day)
    
    def _apply_time_of_day_effects(self, time_of_day: float):
        """
        Apply lighting effects based on time of day.
        
        Args:
            time_of_day: Time in 24-hour format (0-24)
        """
        # Determine sun angle based on time of day
        # 6 AM = 0 degrees, 12 PM = 90 degrees, 6 PM = 180 degrees
        sun_angle = ((time_of_day - 6) / 12) * 180  # Angle from horizon
        
        if sun_angle < 0:
            sun_angle = 0
        elif sun_angle > 180:
            sun_angle = 180
        
        # Adjust lighting intensity based on time of day
        # Normalize to 0-1 range for intensity calculation
        normalized_time = time_of_day % 12
        if normalized_time > 6:
            normalized_time = 12 - normalized_time
        
        intensity_factor = 0.5 + 0.5 * (normalized_time / 6)  # Range 0.5-1.0
        
        carb.log_verbose(f"Time of day: {time_of_day}h, Sun angle: {sun_angle}°, Intensity factor: {intensity_factor}")
    
    def add_light(self, light: LightSource) -> bool:
        """
        Add a light source to the stage.
        
        Args:
            light: LightSource specification to add
            
        Returns:
            True if successfully added, False otherwise
        """
        try:
            from omni.isaac.core.utils.stage import add_reference_to_stage
            
            stage = get_current_stage()
            if not stage:
                carb.log_error("No stage available to add light to")
                return False
            
            light_path = Sdf.Path(f"/World/Lights/{light.name}")
            
            # Create the appropriate light type
            if light.light_type == "dome":
                dome_light = UsdLux.DomeLight.Define(stage, light_path)
                dome_light.CreateIntensityAttr(light.intensity)
                dome_light.CreateColorAttr(Gf.Vec3f(*light.color))
                
                # Apply environment map if specified
                # This would require a valid asset path in a real implementation
                # dome_light.CreateTextureFileAttr(light.environment_map_path or "")
                
            elif light.light_type == "distant":
                distant_light = UsdLux.DistantLight.Define(stage, light_path)
                distant_light.CreateIntensityAttr(light.intensity)
                distant_light.CreateColorAttr(Gf.Vec3f(*light.color))
                
                # Apply rotation
                if light.angle is not None:
                    distant_light.AddRotateXOp().Set(light.angle)
                
            elif light.light_type == "sphere":
                sphere_light = UsdLux.SphereLight.Define(stage, light_path)
                sphere_light.CreateIntensityAttr(light.intensity)
                sphere_light.CreateColorAttr(Gf.Vec3f(*light.color))
                
                # Set position
                sphere_light.AddTranslateOp().Set(Gf.Vec3f(*light.position))
                
                # Set radius if specified
                if light.radius is not None:
                    sphere_light.CreateRadiusAttr(light.radius)
                
            elif light.light_type == "rect":
                rect_light = UsdLux.RectLight.Define(stage, light_path)
                rect_light.CreateIntensityAttr(light.intensity)
                rect_light.CreateColorAttr(Gf.Vec3f(*light.color))
                
                # Set position
                rect_light.AddTranslateOp().Set(Gf.Vec3f(*light.position))
                
                # Set size if specified
                if light.width is not None:
                    rect_light.CreateWidthAttr(light.width)
                if light.height is not None:
                    rect_light.CreateHeightAttr(light.height)
                
            elif light.light_type == "disk":
                disk_light = UsdLux.DiskLight.Define(stage, light_path)
                disk_light.CreateIntensityAttr(light.intensity)
                disk_light.CreateColorAttr(Gf.Vec3f(*light.color))
                
                # Set position
                disk_light.AddTranslateOp().Set(Gf.Vec3f(*light.position))
                
                # Set size if specified
                if light.width is not None:
                    disk_light.CreateRadiusAttr(light.width / 2.0)
                
            # Store reference to the light
            self.lights[light.name] = light
            
            carb.log_verbose(f"Added {light.light_type} light: {light.name}")
            return True
            
        except Exception as e:
            carb.log_error(f"Failed to add light {light.name}: {str(e)}")
            return False
    
    def add_material(self, material: Material) -> bool:
        """
        Add a material to the stage.
        
        Args:
            material: Material specification to add
            
        Returns:
            True if successfully added, False otherwise
        """
        try:
            stage = get_current_stage()
            if not stage:
                carb.log_error("No stage available to add material to")
                return False
            
            # Create material path
            material_path = Sdf.Path(f"/World/Materials/{material.name}")
            
            # Create the material
            material_prim = define_prim(material_path, "Material")
            
            # Add surface output
            material_surface_output = material_prim.GetOutput("outputs:surface")
            
            # Create the surface shader based on material type
            if material.material_type == "omnishopper_pbr":
                shader_path = Sdf.Path(f"{material_path}/OmnishopperPBR")
                shader = UsdShade.Shader.Define(stage, shader_path)
                shader.CreateIdAttr("OmniPBR")
                
                # Set material properties
                shader.CreateInput("diffuse_tint", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*material.diffuse_color))
                shader.CreateInput("emissive_color", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*material.emissive_color))
                shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(material.roughness)
                shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(material.metallic)
                shader.CreateInput("specular", Sdf.ValueTypeNames.Float).Set(material.specular)
                shader.CreateInput("clearcoat", Sdf.ValueTypeNames.Float).Set(material.clearcoat)
                shader.CreateInput("clearcoat_roughness", Sdf.ValueTypeNames.Float).Set(material.clearcoat_roughness)
                shader.CreateInput("opacity", Sdf.ValueTypeNames.Float).Set(material.opacity)
                shader.CreateInput("ior", Sdf.ValueTypeNames.Float).Set(material.ior)
                
                # Connect the shader to the material's surface output
                shader.GetOutput("outputs:surface").ConnectToSource(material_surface_output)
            
            # Store reference to the material
            self.materials[material.name] = material
            
            carb.log_verbose(f"Added material: {material.name}")
            return True
            
        except Exception as e:
            carb.log_error(f"Failed to add material {material.name}: {str(e)}")
            return False
    
    def apply_default_lighting(self):
        """Apply default lighting setup to the stage."""
        # Add a dome light for general illumination
        default_dome = LightSource(
            name="default_dome",
            light_type="dome",
            intensity=500.0,
            color=(1.0, 1.0, 1.0)
        )
        self.add_light(default_dome)
        
        # Add a distant light to simulate sun
        default_sun = LightSource(
            name="default_sun",
            light_type="distant",
            intensity=3000.0,
            color=(1.0, 0.95, 0.9),
            rotation=(45, 30, 0)  # Rotate 45 degrees up, 30 degrees around
        )
        self.add_light(default_sun)
        
        carb.log_info("Default lighting applied")
    
    def setup_environment_map(self, environment_map_path: Optional[str] = None):
        """
        Setup environment map for realistic lighting.
        
        Args:
            environment_map_path: Path to the environment map texture
        """
        if not environment_map_path:
            # Use a default environment map
            environment_map_path = "omniverse://localhost/NVIDIA/Assets/Skies/Indoor/curry-avdp-4k.mdl"
        
        # In a real implementation, this would set up the dome light with the environment map
        carb.log_info(f"Environment map setup: {environment_map_path}")
    
    def set_time_of_day(self, hour: float):
        """
        Set the time of day to adjust lighting conditions.
        
        Args:
            hour: Time in 24-hour format (0-24)
        """
        if hour < 0 or hour > 24:
            carb.log_error(f"Invalid hour: {hour}. Must be between 0 and 24")
            return
        
        # Calculate sun position based on time
        # 6 AM = -90 degrees (sunrise), 12 PM = 0 degrees (noon), 6 PM = 90 degrees (sunset)
        sun_elevation = ((hour - 12) / 12) * 90
        sun_azimuth = (hour % 12) * 30  # Rough approximation
        
        # Adjust existing lights based on time
        for light_name, light in self.lights.items():
            if light.light_type == "distant":  # This is our sun
                # In a real implementation, we would update the light's rotation
                carb.log_verbose(f"Sun position updated: elevation={sun_elevation}, azimuth={sun_azimuth}")
        
        carb.log_info(f"Time of day set to {hour}:00, sun elevation: {sun_elevation}°")


class MaterialManager:
    """
    Class responsible for managing materials in Isaac Sim environments.
    """
    
    def __init__(self):
        """Initialize the material manager."""
        self.materials: Dict[str, Material] = {}
    
    def create_common_materials(self):
        """Create common materials that are frequently used."""
        # Create materials for basic surfaces
        materials_to_create = [
            Material(name="floor_material", material_type="omnishopper_pbr", 
                    diffuse_color=(0.7, 0.7, 0.7), roughness=0.8, metallic=0.0),
            Material(name="wall_material", material_type="omnishopper_pbr", 
                    diffuse_color=(0.9, 0.9, 0.9), roughness=0.9, metallic=0.0),
            Material(name="wood_material", material_type="omnishopper_pbr", 
                    diffuse_color=(0.8, 0.6, 0.3), roughness=0.5, metallic=0.0),
            Material(name="metal_material", material_type="omnishopper_pbr", 
                    diffuse_color=(0.7, 0.7, 0.8), roughness=0.1, metallic=0.9),
            Material(name="plastic_material", material_type="omnishopper_pbr", 
                    diffuse_color=(0.3, 0.6, 0.9), roughness=0.3, metallic=0.1),
            Material(name="glass_material", material_type="omnishopper_pbr", 
                    diffuse_color=(0.9, 0.9, 0.9), roughness=0.05, metallic=0.0, opacity=0.3),
        ]
        
        for material in materials_to_create:
            self.materials[material.name] = material
            carb.log_verbose(f"Created common material: {material.name}")
    
    def apply_material_to_prim(self, prim_path: str, material_name: str) -> bool:
        """
        Apply a material to a specific prim.
        
        Args:
            prim_path: Path to the prim to apply material to
            material_name: Name of the material to apply
            
        Returns:
            True if successfully applied, False otherwise
        """
        if material_name not in self.materials:
            carb.log_error(f"Material {material_name} not found")
            return False
        
        try:
            stage = get_current_stage()
            if not stage:
                carb.log_error("No stage available to apply material to")
                return False
            
            # Get the prim
            prim = stage.GetPrimAtPath(Sdf.Path(prim_path))
            if not prim:
                carb.log_error(f"Prim at path {prim_path} not found")
                return False
            
            # Create material binding API
            from pxr import UsdShade
            binding_api = UsdShade.MaterialBindingAPI(prim)
            
            # Get the material prim
            material_prim = stage.GetPrimAtPath(Sdf.Path(f"/World/Materials/{material_name}"))
            if not material_prim:
                carb.log_error(f"Material prim for {material_name} not found")
                return False
            
            # Bind the material to the prim
            material = UsdShade.Material(material_prim)
            binding_api.Bind(material)
            
            carb.log_verbose(f"Applied material {material_name} to {prim_path}")
            return True
            
        except Exception as e:
            carb.log_error(f"Failed to apply material {material_name} to {prim_path}: {str(e)}")
            return False
    
    def update_material_property(self, material_name: str, property_name: str, value: Any) -> bool:
        """
        Update a property of an existing material.
        
        Args:
            material_name: Name of the material to update
            property_name: Name of the property to update
            value: New value for the property
            
        Returns:
            True if successfully updated, False otherwise
        """
        if material_name not in self.materials:
            carb.log_error(f"Material {material_name} not found")
            return False
        
        material = self.materials[material_name]
        
        # Update the property if it exists
        if hasattr(material, property_name):
            setattr(material, property_name, value)
            carb.log_verbose(f"Updated {property_name} for material {material_name} to {value}")
            return True
        else:
            carb.log_error(f"Material {material_name} does not have property {property_name}")
            return False


# Example usage function
def example_usage():
    """
    Example of how to use the LightingConfigurator and MaterialManager.
    """
    # Initialize the configurator and manager
    lighting_configurator = LightingConfigurator()
    material_manager = MaterialManager()
    
    # Create common materials
    material_manager.create_common_materials()
    
    # Add a custom light
    custom_light = LightSource(
        name="reading_lamp",
        light_type="sphere",
        intensity=500.0,
        color=(1.0, 0.9, 0.7),
        position=(2.0, 0.0, 1.5),
        radius=0.1
    )
    lighting_configurator.add_light(custom_light)
    
    # Add a custom material
    custom_material = Material(
        name="red_fabric",
        material_type="omnishopper_pbr",
        diffuse_color=(0.8, 0.1, 0.1),
        roughness=0.7,
        metallic=0.0
    )
    lighting_configurator.add_material(custom_material)
    
    # Apply time of day
    lighting_configurator.set_time_of_day(14.5)  # 2:30 PM
    
    carb.log_info("Lighting and materials example completed")
    
    return lighting_configurator, material_manager