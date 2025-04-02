# RoverX - Autonomous Rescue Rover for Disaster Zones

## Problem Statement (Programming Category)

- An advanced autonomous rover system designed for disaster response and survivor rescue operations. The system features intelligent navigation, multi-sensor survivor detection, and sophisticated power management.

## Features

### 1. Advanced Navigation System

- Zigzag pattern movement for efficient area coverage
- Obstacle avoidance using ultrasonic sensors
- Smooth path planning with Bezier curves
- Dynamic path optimization based on battery level
- Natural movement patterns with gradual direction changes
- Safe distance maintenance from obstacles

### 2. Enhanced Survivor Detection

- Multi-sensor fusion system combining:
  - Ultrasonic sensors
  - Infrared sensors
  - RFID detection
  - Accelerometer data
- Confidence-based survivor detection
- Priority-based survivor rescue
- Real-time sensor data processing
- Historical detection tracking

### 3. Intelligent Power Management

- Dynamic power consumption optimization
- Battery life estimation
- Temperature monitoring
- Automatic charging station navigation
- Power state management:
  - Normal operation
  - Low power mode
  - Critical power mode
  - Recharging mode
- Smart power consumption based on:
  - Movement state
  - Sensor activity
  - Communication needs

### 4. Safety Features

- Obstacle detection and avoidance
- Battery level monitoring
- Temperature monitoring
- Communication loss handling
- Emergency stop functionality
- Safe distance maintenance

### 5. State Management

- Comprehensive state machine for different operations:
  - Idle state
  - Searching state
  - Moving to survivor
  - Delivering aid
  - Returning to charge
  - Recharging state

### 6. Webots Simulation

- Realistic 3D simulation environment
- Accurate sensor modeling:
  - Ultrasonic sensors with noise simulation
  - Infrared sensors with reflection modeling
  - RFID reader simulation
  - Accelerometer with realistic physics
- Physics-based movement simulation
- Custom world with disaster zone scenarios
- Survivor and obstacle placement tools
- Real-time visualization and debugging

## Demonstration Video Drive Link

- 1.RoverX Website - https://drive.google.com/file/d/1QDxrpTsP2taXGyTrlcTPvB1eATQ2bb2M/view?usp=drive_link

- 2.RoverX Webot Autosim - https://drive.google.com/file/d/1W61on6CRjrmLkK1djHMKSblJ9LU5VtAI/view?usp=drive_link

- 3.RoverX Webot Manualsim - https://drive.google.com/file/d/1fZtAmIrs1LpJZpAhWcZpABmmaNd5C1-X/view?usp=drive_link

## Technical Requirements

### Dependencies

```
flask==2.0.1
flask-socketio==5.1.1
python-dotenv==0.19.0
requests==2.26.0
colorama==0.4.4
gunicorn==20.1.0
python-engineio==4.2.1
python-socketio==5.4.0
webots==2023b
```

### API Integration

- Base URL: https://roverdata2-production.up.railway.app
- Session management for API calls
- Real-time data transmission

## Setup and Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/RoverX.git
cd RoverX
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install Webots:

- Download and install Webots from [https://cyberbotics.com/](https://cyberbotics.com/)
- Set up Webots environment variables
- Install Webots Python controller

4. Run the application:

```bash
python app.py
```

## Configuration

### Navigation Parameters

- Obstacle threshold: 50cm
- Safe distance: 100cm
- Search pattern width: 200cm
- Search pattern length: 300cm
- Turn interval: 5 seconds

### Power Management Parameters

- Recharge start: 5% battery
- Recharge stop: 80% battery
- Communication loss: 10% battery
- Low power mode: 20% battery
- Temperature warning: 45°C
- Temperature critical: 60°C

### Sensor Thresholds

- Ultrasonic: 200cm
- IR reflection: 0.7
- RFID signal: 0.5
- Accelerometer: 2.0 m/s²

### Simulation Parameters

- World size: 20x20 meters
- Number of survivors: 5-10
- Number of obstacles: 10-15
- Terrain types:
  - Flat ground
  - Uneven terrain
  - Debris fields
- Lighting conditions:
  - Normal daylight
  - Low light
  - Darkness

## Usage

1. Start the rover:

```bash
python app.py
```

2. Access the dashboard:

- Open a web browser
- Navigate to `http://localhost:5000`

3. Control the rover:

- Use the dashboard interface to:
  - Start/stop the rover
  - Monitor sensor data
  - Track survivor detections
  - View power status
  - Monitor navigation path
  - Control simulation parameters

4. Run Webots simulation:

```bash
# Start Webots world
webots worlds/disaster_zone.wbt

# Run controller
python controllers/rover_controller/rover_controller.py
```

## Project Structure

```
RoverX/
├── app.py                 # Main application entry point
├── navigation_system.py   # Navigation and path planning
├── sensor_fusion.py      # Multi-sensor data processing
├── power_management.py   # Power and battery management
├── rover_controller.py   # Main rover control system
├── static/              # Static web assets
│   ├── css/
│   └── js/
├── templates/           # Web templates
│   └── index.html
├── worlds/             # Webots world files
│   ├── disaster_zone.wbt
│   └── training_zone.wbt
├── controllers/        # Webots controllers
│   └── rover_controller/
│       ├── rover_controller.py
│       └── rover_controller_config.py
└── protos/            # Webots PROTO files
    ├── RoverX.proto
    ├── Survivor.proto
    └── Obstacle.proto
```

## Simulation Features

### World Design

- Custom disaster zone environment
- Multiple terrain types
- Dynamic obstacle placement
- Survivor placement tools
- Charging station locations

### Robot Model

- Accurate physical dimensions
- Realistic sensor placement
- Motor control simulation
- Battery consumption modeling
- Temperature simulation

### Sensor Simulation

- Ultrasonic sensor:
  - Distance measurement
  - Noise simulation
  - Beam angle modeling
- Infrared sensor:
  - Reflection simulation
  - Range limitations
  - Environmental effects
- RFID reader:
  - Tag detection
  - Signal strength
  - Interference modeling
- Accelerometer:
  - 3-axis acceleration
  - Noise simulation
  - Calibration options

### Visualization Tools

- Real-time sensor data display
- Path visualization
- Battery status overlay
- Temperature heat map
- Survivor detection markers

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built for the Autonomous Rescue Rover Challenge
- Uses Flask for web interface
- Implements WebSocket for real-time communication
- Integrates with external API for data management
- Powered by Webots for realistic simulation

## Developed by Team Prospera

- Tharun T.V
- Rishab Rajeev
- Priyajit Biswal
- Prannav R
