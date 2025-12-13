#include <gazebo/gazebo.hh>
#include <gazebo/sensors/sensors.hh>
#include <gazebo/physics/physics.hh>
#include <sdf/sdf.hh>
#include <ros/ros.h>
#include <sensor_msgs/LaserScan.h>
#include <thread>

namespace gazebo
{
  class LidarPlugin : public SensorPlugin
  {
    public: 
      void Load(sensors::SensorPtr _sensor, sdf::ElementPtr /*_sdf*/)
      {
        // Get the parent sensor
        this->parentSensor = std::dynamic_pointer_cast<sensors::RaySensor>(_sensor);
        
        if (!this->parentSensor)
        {
          gzerr << "LidarPlugin requires a Ray Sensor.\n";
          return;
        }
        
        // Initialize ROS if not already initialized
        if (!ros::isInitialized())
        {
          int argc = 0;
          char** argv = NULL;
          ros::init(argc, argv, "gazebo_lidar_plugin", 
                   ros::init_options::NoSigintHandler);
        }
        
        // Create ROS node
        this->rosNode.reset(new ros::NodeHandle("gazebo"));
        
        // Create publisher for laser scan data
        this->pub = this->rosNode->advertise<sensor_msgs::LaserScan>(
          "/laser_scan", 1);
        
        // Connect to sensor update event
        this->updateConnection = this->parentSensor->ConnectUpdated(
            std::bind(&LidarPlugin::OnUpdate, this));
        
        // Make sure the parent sensor is active
        this->parentSensor->SetActive(true);
      }

    public: 
      void OnUpdate()
      {
        // Get ranges from the ray sensor
        auto ranges = this->parentSensor->Ranges();
        
        // Create laser scan message
        sensor_msgs::LaserScan scan_msg;
        scan_msg.header.stamp = ros::Time::now();
        scan_msg.header.frame_id = "laser_frame";
        
        // Set laser scan parameters
        scan_msg.angle_min = this->parentSensor->AngleMin().Radian();
        scan_msg.angle_max = this->parentSensor->AngleMax().Radian();
        scan_msg.angle_increment = this->parentSensor->AngleResolution();
        scan_msg.time_increment = 0.0;
        scan_msg.scan_time = 0.033;  // 30Hz
        scan_msg.range_min = this->parentSensor->RangeMin();
        scan_msg.range_max = this->parentSensor->RangeMax();
        
        // Fill in the ranges
        scan_msg.ranges = ranges;
        
        // Publish the laser scan
        this->pub.publish(scan_msg);
      }

    private: 
      sensors::RaySensorPtr parentSensor;
      ros::NodeHandlePtr rosNode;
      ros::Publisher pub;
      event::ConnectionPtr updateConnection;
  };

  // Register this plugin with the simulator
  GZ_REGISTER_SENSOR_PLUGIN(LidarPlugin)
}