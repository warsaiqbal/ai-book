# Current state of the robot reported by state publisher
string robot_name          # Name of the robot
float64[] joint_positions  # Current joint positions (in radians or meters)
float64[] joint_velocities # Current joint velocities
float64[] joint_effort     # Current joint efforts
float64[] cartesian_pose   # End-effector pose [x, y, z, rx, ry, rz]
string[] joint_names       # Names of joints in the arrays
builtin_interfaces/Time timestamp  # Timestamp of the state measurement