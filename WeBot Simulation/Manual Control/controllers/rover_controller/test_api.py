from rover_api import RoverAPI
import time

def test_api():
    # Initialize API with new session ID
    api = RoverAPI(session_id="b8f6fcfc-cf47-4f06-b6c1-2600e1fcdf7a")
    
    try:
        print("\n=== Testing API Data Handling ===")
        
        # Test 1: Get initial status
        print("\nTest 1: Getting initial status...")
        status = api.get_rover_status()
        if status:
            print("Initial Status:")
            print(f"Rover Status: {status['status']}")
            print(f"Battery Level: {status['battery']}%")
            print(f"Position: {status['coordinates']}")
            print(f"Communication: {status['sensor_data']['communication_status']}")
        
        # Test 2: Send movement commands and check status changes
        print("\nTest 2: Testing movement commands...")
        movements = ['forward', 'right', 'backward', 'left']
        
        for direction in movements:
            print(f"\nSending {direction} command...")
            api.send_move_command(direction)
            time.sleep(2)  # Wait for 2 seconds
            
            # Get updated status
            status = api.get_rover_status()
            if status:
                print(f"Updated Status after {direction}:")
                print(f"Battery Level: {status['battery']}%")
                print(f"Position: {status['coordinates']}")
        
        # Test 3: Stop command
        print("\nTest 3: Testing stop command...")
        api.send_stop_command()
        time.sleep(1)
        
        # Get final status
        status = api.get_rover_status()
        if status:
            print("\nFinal Status:")
            print(f"Rover Status: {status['status']}")
            print(f"Battery Level: {status['battery']}%")
            print(f"Position: {status['coordinates']}")
            print("\nDetailed Sensor Data:")
            print(f"Accelerometer: {status['sensor_data']['accelerometer']}")
            print(f"Ultrasonic: {status['sensor_data']['ultrasonic']}")
            print(f"IR: {status['sensor_data']['ir']}")
            print(f"RFID: {status['sensor_data']['rfid']}")
        
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    test_api()
