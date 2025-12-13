# Quickstart Guide: Vision-Language-Action (VLA) Robotics

## Overview
This guide will help you set up and run the Vision-Language-Action (VLA) system for robotics applications. The VLA system enables robots to receive voice commands, plan actions using LLMs, and execute complex tasks involving navigation, perception, and manipulation.

## Prerequisites
- Ubuntu 22.04 LTS
- ROS 2 Humble Hawksbill installed
- Python 3.11
- Docker and Docker Compose
- OpenAI API key
- Compatible robot (physical or simulated)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/vla-robotics.git
cd vla-robotics
git checkout 006-vla-robotics
```

### 2. Set Up Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Set up ROS 2 workspace
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

### 3. Configure Environment Variables
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
WHISPER_MODEL=large-v2  # Options: tiny, base, small, medium, large-v2
ROS_DOMAIN_ID=1
SIMULATION_MODE=true  # Set to false for real robot
DEFAULT_ROBOT_MODEL=humanoid_a
```

## Running the VLA System

### 1. Start Required Services
```bash
# In separate terminals, start each service:

# Start ROS 2 core
ros2 daemon start

# Start the voice processing service
cd src/vla/voice_processor
python3 -m voice_service --model large-v2

# Start the LLM planning service
cd src/vla/llm_planner
python3 -m planning_service --model gpt-4-turbo

# Start the perception service
cd src/vla/perception
python3 -m vision_service

# Start the navigation service
cd src/vla/navigation
python3 -m navigation_service

# Start the manipulation service
cd src/vla/manipulation
python3 -m manipulation_service
```

### 2. Start the Simulation (if using simulation mode)
```bash
# Start the simulation environment
cd simulation/humanoid
python3 start_simulation.py --robot humanoid_a
```

### 3. Run the Complete VLA Pipeline
```bash
# In the project root:
cd src/vla
python3 run_vla_system.py
```

## Testing the System

### Basic Voice Command
1. Ensure all services are running
2. Use the test client:
```bash
cd src/vla
python3 test_voice_command.py --command "Move forward 2 meters"
```

### End-to-End Test
Run the complete test scenario:
```bash
cd src/vla
python3 test_end_to_end.py --scenario "go_to_kitchen_and_pick_up_cup"
```

## API Usage Examples

### Processing a Voice Command
```bash
curl -X POST http://localhost:8000/voice-command/process \
  -H "Content-Type: application/json" \
  -d '{
    "audio_data": "base64_encoded_audio_data",
    "audio_format": "wav",
    "language": "en-US"
  }'
```

### Generating an Action Plan
```bash
curl -X POST http://localhost:8000/plan/generate \
  -H "Content-Type: application/json" \
  -d '{
    "command_text": "Go to the kitchen and bring me a cup",
    "environment_map_id": "map_001",
    "robot_capabilities": ["NAVIGATION", "MANIPULATION", "PERCEPTION"]
  }'
```

### Executing a Plan
```bash
curl -X PUT http://localhost:8000/plan/{plan_id}/execute
```

## Module Structure

The VLA system is organized into several key components:

1. **Voice Processor**: Handles audio input and converts speech to text using OpenAI Whisper
2. **LLM Planner**: Uses large language models to transform natural language into robot action plans
3. **Perception System**: Detects and identifies objects using computer vision
4. **Navigation System**: Plans and executes robot movement through environments
5. **Manipulation System**: Controls robot arms and grippers to interact with objects
6. **Execution Manager**: Coordinates the execution of action plans and handles state management

## Troubleshooting

### Common Issues

**Issue**: "Whisper model not loading"
- Check your internet connection during first run
- Verify sufficient disk space (models require several GB)

**Issue**: "ROS 2 services not connecting"
- Ensure ROS_DOMAIN_ID is consistent across all terminals
- Source the ROS setup in each terminal: `source /opt/ros/humble/setup.bash`

**Issue**: "LLM requests timing out"
- Verify your OpenAI API key is valid
- Check internet connectivity and API rate limits

### Logs and Debugging
- Service logs are written to `logs/` directory
- ROS 2 logs are available via: `ros2 launch vla_system logging.launch.py`
- Enable debug mode: `export VLA_DEBUG=true` before running services

## Next Steps

1. Customize the system for your specific robot platform
2. Fine-tune the LLM prompts for domain-specific language
3. Train computer vision models for objects in your environment
4. Integrate with your existing ROS 2 ecosystem