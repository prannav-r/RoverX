from controller import Robot, Keyboard
import time
from rover_api import RoverAPI
import sys

class RovXController:
    def __init__(self):
        # Initialize robot
        self.robot = Robot()
        self.timestep = int(self.robot.getBasicTimeStep())
        
        # Verify Webots connection
        if not self.robot:
            print("ERROR: Failed to initialize Webots robot controller")
            sys.exit(1)
            
        print("Successfully connected to Webots robot")

        # Initialize keyboard
        self.keyboard = Keyboard()
        self.keyboard.enable(self.timestep)
        
        # Initialize motors
        self.left_front = self.robot.getDevice('front left wheel')
        self.right_front = self.robot.getDevice('front right wheel')
        self.left_back = self.robot.getDevice('back left wheel')
        self.right_back = self.robot.getDevice('back right wheel')
        
        # Verify motor devices
        if not all([self.left_front, self.right_front, self.left_back, self.right_back]):
            print("ERROR: Failed to initialize motor devices")
            sys.exit(1)

        # Initialize front sensors
        self.front_sensors = [
            self.robot.getDevice('so11'),
            self.robot.getDevice('so12')
        ]
        
        # Verify and enable sensors
        for i, sensor in enumerate(self.front_sensors, 1):
            if not sensor:
                print(f"ERROR: Failed to initialize sensor {i}")
                sys.exit(1)
            sensor.enable(self.timestep)
        
        # Set motor positions
        for motor in [self.left_front, self.right_front, self.left_back, self.right_back]:
            motor.setPosition(float('inf'))
            motor.setVelocity(0.0)
        
        # Initialize API with error handling
        try:
            self.api = RoverAPI()
            print("API initialized successfully")
        except Exception as e:
            print(f"ERROR: Failed to initialize API: {str(e)}")
            sys.exit(1)
        
        # Constants
        self.MAX_SPEED = 6.28
        self.TURN_SPEED = self.MAX_SPEED * 0.5
        self.OBSTACLE_THRESHOLD = 0.3
        self.STATUS_INTERVAL = 2.0
        self.last_status_time = 0
        self.is_charging = False
        self.shutdown = False
        
        print("Controller initialization complete")

    def set_speeds(self, left_speed, right_speed):
        """Set wheel speeds with validation"""
        try:
            self.left_front.setVelocity(left_speed)
            self.right_front.setVelocity(right_speed)
            self.left_back.setVelocity(left_speed)
            self.right_back.setVelocity(right_speed)
        except Exception as e:
            print(f"Motor speed error: {str(e)}")
            self.emergency_stop()
        
    def emergency_stop(self):
        """Stop all motors immediately"""
        for motor in [self.left_front, self.right_front, self.left_back, self.right_back]:
            try:
                motor.setVelocity(0.0)
            except:
                pass

    def check_obstacle(self):
        """Check for obstacles with error handling"""
        try:
            return any(sensor.getValue() < self.OBSTACLE_THRESHOLD for sensor in self.front_sensors)
        except Exception as e:
            print(f"Sensor error: {str(e)}")
            return False
        
    def update_status(self):
        """Get status with comprehensive error handling"""
        try:
            status = self.api.get_rover_status()
            if status:
                # Battery management
                if status['battery'] <= 5 and not self.is_charging:
                    self.is_charging = True
                    self.set_speeds(0, 0)
                    print("\nBattery critical! Starting recharge...")
                elif status['battery'] >= 80 and self.is_charging:
                    self.is_charging = False
                    print("\nBattery sufficiently charged. Resuming operation...")
                
                print(f"\nStatus: {status['status']} | Battery: {status['battery']}% | Position: {status['coordinates']}")
                return True
            return False
        except Exception as e:
            print(f"Status update error: {str(e)}")
            return False
        
    def run(self):
        """Main control loop with robust error handling"""
        print("\n=== RovX Controller Running ===")
        print("Press Q to quit, P for status\n")
        
        try:
            while not self.shutdown and self.robot.step(self.timestep) != -1:
                # Check keyboard input
                key = self.keyboard.getKey()
                if key == ord('Q'):
                    self.shutdown = True
                    break
                elif key == ord('P'):
                    self.update_status()
                
                # Periodic status updates
                if self.robot.getTime() - self.last_status_time >= self.STATUS_INTERVAL:
                    self.update_status()
                    self.last_status_time = self.robot.getTime()
                
                # Skip movement if charging
                if self.is_charging:
                    continue
                    
                # Obstacle avoidance
                if self.check_obstacle():
                    self.set_speeds(-self.TURN_SPEED, self.TURN_SPEED)
                else:
                    self.set_speeds(self.MAX_SPEED, self.MAX_SPEED)
                    
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received")
        except Exception as e:
            print(f"\nFatal error in main loop: {str(e)}")
        finally:
            self.emergency_stop()
            print("\n=== Controller Shutdown Complete ===")

if __name__ == "__main__":
    try:
        print("Initializing RovX controller...")
        controller = RovXController()
        controller.run()
    except Exception as e:
        print(f"Controller initialization failed: {str(e)}")
        sys.exit(1)