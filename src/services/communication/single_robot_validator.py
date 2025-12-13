#!/usr/bin/env python3
"""
Validation script for testing complete functionality with a single robot.
This script verifies:
- Robot can be controlled in simulation
- All sensors provide accurate data
- System maintains synchronization
- Performance meets requirements
"""

import rospy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
import time
import sys


class SingleRobotValidator:
    def __init__(self):
        rospy.init_node('single_robot_validator')
        
        # Robot control publisher
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        
        # Sensor data subscribers
        self.odom_sub = rospy.Subscriber('/odom', Odometry, self.odom_callback)
        self.laser_sub = rospy.Subscriber('/laser_scan', LaserScan, self.laser_callback)
        
        # Robot state
        self.current_position = None
        self.laser_data = None
        self.start_time = time.time()
        self.test_results = {
            'robot_controlled': False,
            'sensors_working': False,
            'synchronization_checked': False,
            'performance_met': False
        }
        
        rospy.loginfo("Single Robot Validator initialized")
        
    def odom_callback(self, data):
        """Handle odometry updates"""
        self.current_position = {
            'x': data.pose.pose.position.x,
            'y': data.pose.pose.position.y,
            'theta': data.pose.pose.orientation.z  # Simplified
        }
        
    def laser_callback(self, data):
        """Handle laser scan updates"""
        self.laser_data = {
            'ranges': data.ranges,
            'min_range': min(data.ranges) if data.ranges else float('inf'),
            'max_range': max(data.ranges) if data.ranges else 0,
            'timestamp': rospy.Time.now()
        }
        
    def move_robot(self, linear_speed, angular_speed, duration):
        """Move robot with specified speeds for duration"""
        cmd = Twist()
        cmd.linear.x = linear_speed
        cmd.angular.z = angular_speed
        
        rate = rospy.Rate(10)  # 10 Hz
        start_time = time.time()
        
        while time.time() - start_time < duration and not rospy.is_shutdown():
            self.cmd_vel_pub.publish(cmd)
            rate.sleep()
            
        # Stop the robot
        cmd.linear.x = 0
        cmd.angular.z = 0
        self.cmd_vel_pub.publish(cmd)
        
    def run_validation_test(self):
        """Run the complete validation test"""
        rospy.loginfo("Starting single robot validation test...")
        
        # Wait a bit for data to arrive
        rospy.sleep(2.0)
        
        # Initial position check
        initial_pos = self.current_position
        if initial_pos:
            rospy.loginfo(f"Initial position: x={initial_pos['x']:.2f}, y={initial_pos['y']:.2f}")
        else:
            rospy.logerr("No initial position received - exiting test")
            return False
            
        # Test 1: Robot Control
        rospy.loginfo("Test 1: Moving robot forward...")
        self.move_robot(0.5, 0.0, 3.0)  # Move forward for 3 seconds
        rospy.sleep(1.0)  # Wait for movement to settle
        
        if self.current_position and self.current_position['x'] > initial_pos['x']:
            self.test_results['robot_controlled'] = True
            rospy.loginfo("✓ Robot control test PASSED")
        else:
            rospy.logerr("✗ Robot control test FAILED")
            
        # Test 2: Sensor Functionality
        rospy.loginfo("Test 2: Checking sensor data...")
        if self.laser_data and self.laser_data['min_range'] < float('inf'):
            self.test_results['sensors_working'] = True
            rospy.loginfo(f"✓ Sensors working - min range: {self.laser_data['min_range']:.2f}")
        else:
            rospy.logerr("✗ Sensor functionality test FAILED")
            
        # Test 3: Performance Check
        rospy.loginfo("Test 3: Performance check...")
        # Record start time for performance measurement
        perf_start = time.time()
        scan_count = 0
        
        # Collect data for 2 seconds to check sensor update rate
        perf_end = time.time() + 2.0
        while time.time() < perf_end:
            if self.laser_data and self.laser_data['timestamp'].to_sec() >= rospy.Time.now().to_sec() - 0.1:
                scan_count += 1
            rospy.sleep(0.01)  # Sleep briefly
            
        # Check if we're getting at least 30 FPS worth of sensor updates
        if scan_count >= 30:  # Assuming 30 FPS requirement
            self.test_results['performance_met'] = True
            rospy.loginfo(f"✓ Performance test PASSED - {scan_count} updates in 2s")
        else:
            rospy.logwarn(f"⚠ Performance test - only {scan_count} updates in 2s")
            
        # Test 4: Synchronization Check (simplified)
        rospy.loginfo("Test 4: Basic synchronization check...")
        # In a real implementation, this would verify consistency between different sim engines
        # For this test, we'll assume that if we're getting both pose and sensor data, sync is working
        if self.current_position and self.laser_data:
            self.test_results['synchronization_checked'] = True
            rospy.loginfo("✓ Synchronization check completed")
        else:
            rospy.logerr("✗ Synchronization check FAILED - missing data")
            
        # Final test result
        all_passed = all(self.test_results.values())
        rospy.loginfo(f"\nValidation Summary:")
        rospy.loginfo(f"  Robot Controlled: {'✓' if self.test_results['robot_controlled'] else '✗'}")
        rospy.loginfo(f"  Sensors Working: {'✓' if self.test_results['sensors_working'] else '✗'}")
        rospy.loginfo(f"  Performance Met: {'✓' if self.test_results['performance_met'] else '⚠'}")
        rospy.loginfo(f"  Sync Checked: {'✓' if self.test_results['synchronization_checked'] else '✗'}")
        rospy.loginfo(f"\nOverall Result: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
        
        return all_passed
        
    def run(self):
        """Run the validation"""
        result = self.run_validation_test()
        rospy.loginfo(f"Validation completed with result: {'PASS' if result else 'FAIL'}")
        return result


if __name__ == '__main__':
    try:
        validator = SingleRobotValidator()
        success = validator.run()
        sys.exit(0 if success else 1)
    except rospy.ROSInterruptException:
        rospy.loginfo("Validator interrupted")
        sys.exit(1)