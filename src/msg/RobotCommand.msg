# Command sent from AI agents or remote interfaces to control the robot
string command_type  # Type of command (move_to, grip, stop, etc.)
float64[] target_positions  # Target joint positions (in radians or meters)
float64[] target_velocities  # Target joint velocities (optional)
float64[] target_effort     # Target joint effort (optional)
float64 timeout             # Command timeout in seconds
string[] joints             # Names of joints to command (optional)