# Sensor data from robot sensors
string sensor_type         # Type of sensor (imu, camera, lidar, etc.)
string sensor_name         # Name of the specific sensor
float64[] data             # Sensor data values
builtin_interfaces/Time timestamp  # Timestamp of the measurement
float64 frame_rate         # Rate at which sensor is publishing data
string frame_id            # TF frame of the sensor