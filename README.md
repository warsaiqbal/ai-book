# Vision-Language-Action (VLA) Robotics System

This project implements a complete pipeline for translating human voice commands into robotic actions. The system integrates OpenAI Whisper for voice-to-text conversion, LLMs for cognitive planning of natural language to ROS 2 action sequences, and executes complex multi-step tasks combining navigation, computer vision, and manipulation.

## Architecture Overview

The VLA system is organized into several key components:

1. **Voice Processor**: Handles audio input and converts speech to text using OpenAI Whisper
2. **LLM Planner**: Uses large language models to transform natural language into robot action plans
3. **Perception System**: Detects and identifies objects using computer vision
4. **Navigation System**: Plans and executes robot movement through environments
5. **Manipulation System**: Controls robot arms and grippers to interact with objects
6. **Execution Manager**: Coordinates the execution of action plans and handles state management

## Prerequisites

- Ubuntu 22.04 LTS
- ROS 2 Humble Hawksbill installed
- Python 3.11
- Docker and Docker Compose
- OpenAI API key
- Compatible robot (physical or simulated)

## Installation

### 1. Set Up Environment
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

### 2. Configure Environment Variables
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
WHISPER_MODEL=large-v2  # Options: tiny, base, small, medium, large-v2
ROS_DOMAIN_ID=1
SIMULATION_MODE=true  # Set to false for real robot
DEFAULT_ROBOT_MODEL=humanoid_a
```

## Running the VLA System

### Start Required Services
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

### Run the Complete VLA Pipeline
```bash
# In the project root:
cd src/vla
python3 run_vla_system.py
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

## Project Structure

```
src/
├── vla/
│   ├── voice_processor/     # OpenAI Whisper integration
│   ├── llm_planner/         # LLM cognitive planning components
│   ├── perception/          # Computer vision for object detection
│   ├── navigation/          # Path planning and obstacle avoidance
│   ├── manipulation/        # Grasping and object manipulation
│   ├── execution/           # Execution management and state tracking
│   └── interfaces/          # ROS 2 interfaces and message definitions
├── shared/
│   ├── models/              # Shared data models (from data-model.md)
│   ├── utils/               # Utility functions
│   └── config/              # Configuration files
└── simulation/
    ├── envs/                # Simulation environments
    └── humanoid/            # Humanoid robot models
```

## Development

For development, check out the `specs/006-vla-robotics/` directory for detailed specifications and task lists.