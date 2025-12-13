"""
Test suite for simulation environment loading and physics accuracy in the AI-Robot Brain project.

This module provides tests to validate that simulation environments are loaded correctly
and physics properties are accurately configured and behaving as expected.
"""

import unittest
import numpy as np
from unittest.mock import Mock, MagicMock, patch
from src.simulation.models.environment import SimulatedEnvironment, EnvironmentAsset
from src.simulation.models.robot import RobotModel
from src.simulation.models.sensor import Sensor, SensorType
from src.simulation.isaac_sim.environment_loader import IsaacSimEnvironmentLoader
from src.simulation.isaac_sim.physics_integrator import PhysicsIntegrator
from src.simulation.isaac_sim.robot_spawner import RobotSpawner
from src.utils.data_models import Vector3, Quaternion


class TestEnvironmentLoading(unittest.TestCase):
    """
    Test cases for simulation environment loading functionality.
    """
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a test environment with known properties
        self.test_environment = SimulatedEnvironment(
            id="test_env_1",
            name="Test Environment",
            description="A test environment for validation"
        )
        
        # Add some assets to the test environment
        test_asset = EnvironmentAsset(
            id="test_cube_1",
            name="Test Cube",
            asset_type="static",
            position=Vector3(1.0, 0.0, 0.0),
            asset_path="omniverse://localhost/NVIDIA/Assets/Isaac/Props/Chessboard/Chessboard.usd"
        )
        self.test_environment.add_asset(test_asset)
    
    @patch('omni.isaac.core.World')
    def test_environment_initialization(self, mock_world):
        """Test that environment loader initializes properly."""
        # Mock the Isaac Sim World
        mock_world_instance = Mock()
        mock_world.return_value = mock_world_instance
        
        # Create environment loader
        loader = IsaacSimEnvironmentLoader()
        loader.initialize_world()
        
        # Verify that the world was initialized
        self.assertIsNotNone(loader.world)
        self.assertEqual(loader.current_environment, None)
    
    @patch('omni.isaac.core.World')
    def test_load_environment_basic(self, mock_world):
        """Test that a basic environment can be loaded."""
        # Mock the Isaac Sim World and its methods
        mock_world_instance = Mock()
        mock_world.return_value = mock_world_instance
        mock_world_instance.get_physics_context.return_value = Mock()
        
        # Create environment loader and initialize
        loader = IsaacSimEnvironmentLoader()
        loader.initialize_world()
        
        # Load the test environment
        result = loader.load_environment(self.test_environment)
        
        # Verify the result is True (successful loading)
        self.assertTrue(result)
        self.assertEqual(loader.current_environment, self.test_environment)
    
    @patch('omni.isaac.core.World')
    def test_environment_with_physics_properties(self, mock_world):
        """Test that environment with physics properties is loaded correctly."""
        # Create an environment with physics properties
        env_with_physics = SimulatedEnvironment(
            id="physics_env_1",
            name="Physics Environment",
            description="Environment with specific physics properties"
        )
        
        # Set specific physics properties
        env_with_physics.physics_properties_obj.gravity = Vector3(0, 0, -8.0)  # Lower gravity
        env_with_physics.physics_properties_obj.solver_iterations = 256  # More iterations
        
        # Mock the Isaac Sim World and its methods
        mock_world_instance = Mock()
        mock_world.return_value = mock_world_instance
        mock_physics_context = Mock()
        mock_world_instance.get_physics_context.return_value = mock_physics_context
        
        # Create environment loader and initialize
        loader = IsaacSimEnvironmentLoader()
        loader.initialize_world()
        
        # Load the environment
        result = loader.load_environment(env_with_physics)
        
        # Verify the result is True
        self.assertTrue(result)
        
        # Verify that physics properties were applied
        mock_physics_context.set_gravity.assert_called_with([0, 0, -8.0])
        mock_physics_context.set_maximum_solver_velocity_iterations.assert_called_with(256)


class TestPhysicsAccuracy(unittest.TestCase):
    """
    Test cases for physics accuracy and behavior in the simulation.
    """
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.physics_integrator = PhysicsIntegrator()
    
    @patch('omni.isaac.core.World')
    def test_gravity_application(self, mock_world):
        """Test that gravity is correctly applied to the physics context."""
        # Mock physics context
        mock_world_instance = Mock()
        mock_world.return_value = mock_world_instance
        mock_physics_context = Mock()
        mock_world_instance.get_physics_context.return_value = mock_physics_context
        
        # Set the world in the integrator
        self.physics_integrator.set_world(mock_world_instance)
        
        # Define test environment with specific gravity
        test_env = SimulatedEnvironment(
            id="gravity_test_env",
            name="Gravity Test Environment"
        )
        test_env.physics_properties_obj.gravity = Vector3(0, 0, -9.81)
        
        # Integrate the physics
        result = self.physics_integrator.integrate_environment_physics(test_env)
        
        # Verify that the gravity was applied correctly
        self.assertTrue(result)
        mock_physics_context.set_gravity.assert_called_with([0, 0, -9.81])
    
    @patch('omni.isaac.core.World')
    def test_solver_settings_application(self, mock_world):
        """Test that solver settings are correctly applied."""
        # Mock physics context
        mock_world_instance = Mock()
        mock_world.return_value = mock_world_instance
        mock_physics_context = Mock()
        mock_world_instance.get_physics_context.return_value = mock_physics_context
        
        # Set the world in the integrator
        self.physics_integrator.set_world(mock_world_instance)
        
        # Define test environment with specific solver settings
        test_env = SimulatedEnvironment(
            id="solver_test_env",
            name="Solver Test Environment"
        )
        test_env.physics_properties_obj.solver_iterations = 192
        test_env.physics_properties_obj.solver_type = "tgs"  # Temporal Gauss-Seidel
        test_env.physics_properties_obj.enable_ccd = True  # Enable Continuous Collision Detection
        
        # Integrate the physics
        result = self.physics_integrator.integrate_environment_physics(test_env)
        
        # Verify that the settings were applied
        self.assertTrue(result)
        mock_physics_context.set_solver_type.assert_called_with("tgs")
        mock_physics_context.set_maximum_solver_velocity_iterations.assert_called_with(192)
        mock_physics_context.set_maximum_contact_position_iterations.assert_called_with(192)
        mock_physics_context.set_enable_ccd.assert_called_with(True)
    
    @patch('omni.isaac.core.World')
    def test_global_physics_parameters(self, mock_world):
        """Test setting global physics parameters."""
        # Mock physics context
        mock_world_instance = Mock()
        mock_world.return_value = mock_world_instance
        mock_physics_context = Mock()
        mock_world_instance.get_physics_context.return_value = mock_physics_context
        
        # Set the world in the integrator
        self.physics_integrator.set_world(mock_world_instance)
        
        # Apply global physics parameters
        result = self.physics_integrator.set_global_physics_parameters(
            gravity=(0, 0, -8.5),
            enable_ccd=True,
            solver_iterations=64
        )
        
        # Verify the parameters were applied
        self.assertTrue(result)
        mock_physics_context.set_gravity.assert_called_with([0, 0, -8.5])
        mock_physics_context.set_enable_ccd.assert_called_with(True)
        mock_physics_context.set_maximum_solver_velocity_iterations.assert_called_with(64)
        mock_physics_context.set_maximum_contact_position_iterations.assert_called_with(64)


class TestPhysicsValidation(unittest.TestCase):
    """
    Test cases for physics validation and configuration checking.
    """
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.physics_integrator = PhysicsIntegrator()
    
    @patch('omni.isaac.core.World')
    def test_physics_validation_no_world(self, mock_world):
        """Test physics validation when no world is set."""
        # Don't set a world in the integrator
        # Call validation method
        results = self.physics_integrator.validate_physics_setup()
        
        # Verify that the validation detected the missing world
        self.assertIn("World not set", results["issues"])
    
    @patch('omni.isaac.core.World')
    def test_physics_validation_valid_setup(self, mock_world):
        """Test physics validation with a valid setup."""
        # Mock physics context with typical values
        mock_world_instance = Mock()
        mock_world.return_value = mock_world_instance
        mock_physics_context = Mock()
        mock_physics_context.get_gravity.return_value = [0, 0, -9.81]
        mock_physics_context.enable_ccd = False
        mock_physics_context.enable_gpu_dynamics = True
        mock_world_instance.get_physics_context.return_value = mock_physics_context
        
        # Set the world in the integrator
        self.physics_integrator.set_world(mock_world_instance)
        
        # Perform validation
        results = self.physics_integrator.validate_physics_setup()
        
        # Verify the validation results
        self.assertTrue(results["gravity_set"])
        self.assertTrue(results["solver_configured"])
        self.assertFalse(results["ccd_enabled"])  # CCD is disabled
        self.assertTrue(results["gpu_dynamics"])  # GPU dynamics enabled
        self.assertEqual(len(results["issues"]), 0)  # No issues
    
    @patch('omni.isaac.core.World')
    def test_physics_validation_invalid_gravity(self, mock_world):
        """Test physics validation with invalid gravity value."""
        # Mock physics context with non-standard gravity
        mock_world_instance = Mock()
        mock_world.return_value = mock_world_instance
        mock_physics_context = Mock()
        mock_physics_context.get_gravity.return_value = [0, 0, -5.0]  # Non-standard gravity
        mock_physics_context.enable_ccd = False
        mock_physics_context.enable_gpu_dynamics = False
        mock_world_instance.get_physics_context.return_value = mock_physics_context
        
        # Set the world in the integrator
        self.physics_integrator.set_world(mock_world_instance)
        
        # Perform validation
        results = self.physics_integrator.validate_physics_setup()
        
        # Verify the validation results include the gravity issue
        self.assertFalse(results["gravity_set"])  # Gravity not standard
        self.assertTrue(results["solver_configured"])
        self.assertFalse(results["ccd_enabled"])
        self.assertFalse(results["gpu_dynamics"])
        self.assertGreater(len(results["issues"]), 0)  # Should have at least one issue
        self.assertTrue(any("Gravity z-component is -5.0" in issue for issue in results["issues"]))


class TestRobotIntegration(unittest.TestCase):
    """
    Test cases for robot integration in the physics environment.
    """
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.spawner = RobotSpawner()
        self.physics_integrator = PhysicsIntegrator()
    
    @patch('omni.isaac.core.World')
    @patch('omni.isaac.core.robots.Robot')
    def test_robot_spawn_with_physics_properties(self, mock_robot, mock_world):
        """Test spawning a robot with physics properties applied."""
        # Mock the Isaac Sim World and Robot
        mock_world_instance = Mock()
        mock_world.return_value = mock_world_instance
        mock_robot_instance = Mock()
        mock_robot.return_value = mock_robot_instance
        
        # Set up the spawner and physics integrator
        self.spawner.set_world(mock_world_instance)
        
        # Create a test robot
        test_robot = RobotModel(
            id="test_robot_1",
            name="Test Robot",
            urdf_path="./data/robot_models/bipedal_robot/bipedal.urdf",
            mass=50.0,  # 50 kg mass
        )
        
        # Mock the scene.add method
        mock_scene = Mock()
        mock_world_instance.scene = mock_scene
        mock_scene.add.return_value = mock_robot_instance
        
        # Add some joints to the robot for realistic testing
        from src.simulation.models.robot import JointModel
        test_joint = JointModel(
            name="test_joint",
            joint_type="revolute",
            parent_link="base_link",
            child_link="arm_link",
            limits_lower=-1.57,
            limits_upper=1.57
        )
        test_robot.add_joint(test_joint)
        
        # Try to spawn the robot
        result = self.spawner.spawn_robot(test_robot)
        
        # Verify the robot was spawned
        self.assertIsNotNone(result)
        mock_scene.add.assert_called()
        
        # Verify that the robot's properties would be configured
        # In a real implementation, this would check if joint limits, etc. were applied


class TestEnvironmentAssets(unittest.TestCase):
    """
    Test cases for environment asset handling and physics properties.
    """
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.loader = IsaacSimEnvironmentLoader()
    
    @patch('omni.isaac.core.World')
    def test_asset_with_physics_properties(self, mock_world):
        """Test that environment assets have appropriate physics properties applied."""
        # Mock the Isaac Sim World
        mock_world_instance = Mock()
        mock_world.return_value = mock_world_instance
        
        # Create an environment with assets that have physics properties
        env = SimulatedEnvironment(
            id="asset_physics_env",
            name="Asset Physics Environment"
        )
        
        # Add an asset with specific properties
        asset = EnvironmentAsset(
            id="test_table",
            name="Test Table",
            asset_type="static",
            position=Vector3(2.0, 0.0, 0.0),
            mass=10.0  # This property would affect physics
        )
        env.add_asset(asset)
        
        # Mock physics context
        mock_physics_context = Mock()
        mock_world_instance.get_physics_context.return_value = mock_physics_context
        
        # Initialize and load environment
        self.loader.initialize_world()
        result = self.loader.load_environment(env)
        
        # Verify the environment loaded successfully
        self.assertTrue(result)
        self.assertEqual(self.loader.current_environment, env)


def suite():
    """Create a test suite combining all test cases."""
    suite = unittest.TestSuite()
    
    # Add tests for environment loading
    suite.addTest(unittest.makeSuite(TestEnvironmentLoading))
    
    # Add tests for physics accuracy
    suite.addTest(unittest.makeSuite(TestPhysicsAccuracy))
    
    # Add tests for physics validation
    suite.addTest(unittest.makeSuite(TestPhysicsValidation))
    
    # Add tests for robot integration
    suite.addTest(unittest.makeSuite(TestRobotIntegration))
    
    # Add tests for environment assets
    suite.addTest(unittest.makeSuite(TestEnvironmentAssets))
    
    return suite


if __name__ == '__main__':
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())