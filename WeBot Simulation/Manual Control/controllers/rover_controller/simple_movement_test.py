from rover_api import RoverAPI
import time

def print_status(api):
    """Print current rover status"""
    status = api.get_rover_status()
    if status:
        print(f"\nCurrent Status:")
        print(f"Battery Level: {status['battery']}%")
        print(f"Position: {status['coordinates']}")
        print(f"Status: {status['status']}")
    else:
        print("\nError: Could not get rover status")

def main():
    api = RoverAPI()  # Will use the default session ID from RoverAPI class
    
    while True:
        print("\n=== Rover Movement Test ===")
        print("Commands:")
        print("f - Move Forward")
        print("b - Move Backward")
        print("l - Turn Left")
        print("r - Turn Right")
        print("s - Stop")
        print("q - Quit")
        print("p - Print current status")
        
        command = input("\nEnter command: ").lower()
        
        if command == 'q':
            break
        elif command == 'p':
            print_status(api)
        elif command in ['f', 'b', 'l', 'r']:
            direction = {
                'f': 'forward',
                'b': 'backward',
                'l': 'left',
                'r': 'right'
            }[command]
            
            api.send_move_command(direction)
            print_status(api)
        elif command == 's':
            api.send_stop_command()
            print_status(api)
        else:
            print("Invalid command!")
        
        time.sleep(0.5)  # Small delay between commands

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTest ended by user")
    except Exception as e:
        print(f"\nError: {e}")
