#!/usr/bin/env python3
"""
Middleware communication system for synchronizing states between Gazebo physics simulation and Unity rendering.
This service handles the transfer of state information between the two simulation engines.
"""

import rospy
from std_msgs.msg import String
import tf2_ros
import tf2_geometry_msgs
from geometry_msgs.msg import TransformStamped, Point, Pose
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan, PointCloud2
import socket
import json
import threading
import time
from typing import Dict, Any, Optional


class GazeboUnitySyncService:
    """
    Service to synchronize state between Gazebo and Unity
    """
    def __init__(self):
        rospy.init_node('gazebo_unity_sync_service')
        
        # Initialize state store
        self.simulation_state = {
            'robots': {},
            'environment': {},
            'sensors': {},
            'timestamp': 0
        }
        
        # Set up ROS subscribers for Gazebo data
        self.odom_sub = rospy.Subscriber('/odom', Odometry, self.odom_callback)
        self.laser_sub = rospy.Subscriber('/laser_scan', LaserScan, self.laser_callback)
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer)
        
        # Set up publishers for Unity
        self.unity_pub = rospy.Publisher('/unity_commands', String, queue_size=10)
        
        # Set up network communication with Unity
        self.unity_socket = None
        self.setup_unity_connection()
        
        # Synchronization parameters
        self.sync_rate = rospy.Rate(30)  # 30 Hz sync rate
        self.last_sync_time = time.time()
        
        rospy.loginfo("Gazebo-Unity synchronization service initialized")

    def setup_unity_connection(self):
        """Set up network connection to Unity application"""
        try:
            self.unity_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Connect to Unity (assuming it's listening on localhost:8080)
            self.unity_socket.connect(('localhost', 8080))
            rospy.loginfo("Connected to Unity application")
        except Exception as e:
            rospy.logerr(f"Failed to connect to Unity: {e}")
            self.unity_socket = None

    def odom_callback(self, data: Odometry):
        """Handle robot odometry data from Gazebo"""
        robot_id = data.header.frame_id
        if robot_id not in self.simulation_state['robots']:
            self.simulation_state['robots'][robot_id] = {}
            
        self.simulation_state['robots'][robot_id].update({
            'position': {
                'x': data.pose.pose.position.x,
                'y': data.pose.pose.position.y,
                'z': data.pose.pose.position.z
            },
            'orientation': {
                'x': data.pose.pose.orientation.x,
                'y': data.pose.pose.orientation.y,
                'z': data.pose.pose.orientation.z,
                'w': data.pose.pose.orientation.w
            },
            'velocity': {
                'linear': {
                    'x': data.twist.twist.linear.x,
                    'y': data.twist.twist.linear.y,
                    'z': data.twist.twist.linear.z
                },
                'angular': {
                    'x': data.twist.twist.angular.x,
                    'y': data.twist.twist.angular.y,
                    'z': data.twist.twist.angular.z
                }
            },
            'timestamp': rospy.Time.now().to_sec()
        })

    def laser_callback(self, data: LaserScan):
        """Handle LiDAR data from Gazebo"""
        sensor_id = data.header.frame_id
        if sensor_id not in self.simulation_state['sensors']:
            self.simulation_state['sensors'][sensor_id] = {}
            
        self.simulation_state['sensors'][sensor_id].update({
            'type': 'lidar',
            'ranges': list(data.ranges),
            'intensities': list(data.intensities),
            'angle_min': data.angle_min,
            'angle_max': data.angle_max,
            'angle_increment': data.angle_increment,
            'range_min': data.range_min,
            'range_max': data.range_max,
            'timestamp': rospy.Time.now().to_sec()
        })

    def sync_to_unity(self):
        """Send state data to Unity"""
        if self.unity_socket is None:
            return
            
        try:
            # Prepare state data for Unity
            state_data = {
                'timestamp': time.time(),
                'robots': self.simulation_state['robots'],
                'environment': self.simulation_state['environment'],
                'sensors': self.simulation_state['sensors']
            }
            
            # Serialize and send data
            json_data = json.dumps(state_data)
            self.unity_socket.send(json_data.encode('utf-8'))
            
            # Log synchronization
            rospy.logdebug("State synchronized to Unity")
            
        except Exception as e:
            rospy.logerr(f"Error sending data to Unity: {e}")

    def run(self):
        """Main service loop"""
        rospy.loginfo("Starting Gazebo-Unity synchronization service")
        
        while not rospy.is_shutdown():
            # Sync state to Unity
            self.sync_to_unity()
            
            # Sleep according to sync rate
            self.sync_rate.sleep()

            # Update timestamp
            self.simulation_state['timestamp'] = time.time()


if __name__ == '__main__':
    try:
        sync_service = GazeboUnitySyncService()
        sync_service.run()
    except rospy.ROSInterruptException:
        rospy.loginfo("Gazebo-Unity sync service terminated")