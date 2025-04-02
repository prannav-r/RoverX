from controller import Robot, Keyboard
from rover_api import RoverAPI
import math

# Create robot instance and API handler
robot = Robot()
api = RoverAPI()
keyboard = robot.getKeyboard()
keyboard.enable(50)  # Enable keyboard with 50ms sampling period

# Get the time step of the simulation
time_step = int(robot.getBasicTimeStep())

# Initialize motors
front_left_motor = robot.getDevice("front left wheel")
front_right_motor = robot.getDevice("front right wheel")
back_left_motor = robot.getDevice("back left wheel")
back_right_motor = robot.getDevice("back right wheel")

# Initialize sensors
accelerometer = robot.getDevice("accelerometer")
gps = robot.getDevice("gps")
if accelerometer:
    accelerometer.enable(time_step)
if gps:
    gps.enable(time_step)

# Set motor positions to infinity for velocity control
motors = [front_left_motor, front_right_motor, back_left_motor, back_right_motor]
for motor in motors:
    motor.setPosition(float('inf'))
    motor.setVelocity(0.0)

def set_motor_speeds(left_speed, right_speed):
    """Set speeds for left and right side motors"""
    front_left_motor.setVelocity(left_speed)
    back_left_motor.setVelocity(left_speed)
    front_right_motor.setVelocity(right_speed)
    back_right_motor.setVelocity(right_speed)

def move_forward(speed=6.28):
    """Move rover forward"""
    set_motor_speeds(speed, speed)
    api.send_move_command('forward')

def move_backward(speed=6.28):
    """Move rover backward"""
    set_motor_speeds(-speed, -speed)
    api.send_move_command('backward')

def turn_left(speed=3.14):
    """Turn rover left"""
    set_motor_speeds(-speed, speed)
    api.send_move_command('left')

def turn_right(speed=3.14):
    """Turn rover right"""
    set_motor_speeds(speed, -speed)
    api.send_move_command('right')

def stop():
    """Stop the rover"""
    set_motor_speeds(0.0, 0.0)
    api.send_stop_command()

def get_sensor_data():
    """Get sensor data from both simulation and API"""
    # Get API data
    api_data = api.get_rover_status()
    
    # Get simulation sensor data
    sim_data = {
        'accelerometer': {'x': 0, 'y': 0, 'z': 0},
        'position': {'x': 0, 'y': 0},
    }
    
    if accelerometer:
        acc_values = accelerometer.getValues()
        sim_data['accelerometer'] = {
            'x': acc_values[0],
            'y': acc_values[1],
            'z': acc_values[2]
        }
    
    if gps:
        pos_values = gps.getValues()
        sim_data['position'] = {
            'x': pos_values[0],
            'y': pos_values[2]  # Using z as y for 2D position
        }
    
    return {
        'simulation': sim_data,
        'api': api_data
    }

def print_status():
    """Print current status and sensor data"""
    sensor_data = get_sensor_data()
    if sensor_data['api']:
        print("\nStatus Update:")
        print(f"Rover Status: {sensor_data['api']['status']}")
        print(f"Battery Level: {sensor_data['api']['battery']}%")
        print(f"Position: {sensor_data['api']['coordinates']}")
        print(f"Communication: {sensor_data['api']['sensor_data']['communication_status']}")

# Print control instructions
print("\nRover Control Instructions:")
print("UP ARROW: Move Forward")
print("DOWN ARROW: Move Backward")
print("LEFT ARROW: Turn Left")
print("RIGHT ARROW: Turn Right")
print("SPACEBAR: Stop")
print("S: Print Status")
print("Q: Quit")

# Main control loop
while robot.step(time_step) != -1:
    try:
        # Get keyboard input
        key = keyboard.getKey()
        
        # Handle controls
        if key == Keyboard.UP:
            move_forward()
        elif key == Keyboard.DOWN:
            move_backward()
        elif key == Keyboard.LEFT:
            turn_left()
        elif key == Keyboard.RIGHT:
            turn_right()
        elif key == Keyboard.SPACE:
            stop()
        elif key == ord('S'):  # Status update
            print_status()
        elif key == ord('Q'):  # Quit
            break
            
        # Update status every 50 steps (about 1 second)
        if robot.getTime() % 1.0 < time_step / 1000.0:
            print_status()
            
    except Exception as e:
        print(f"Error during simulation: {e}")
        break

# Clean up
stop()
print("Simulation ended")
