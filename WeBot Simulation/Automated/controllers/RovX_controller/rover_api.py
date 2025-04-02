import requests
import time
from config import SESSION_ID

class RoverAPI:
    def __init__(self, session_id=None):
        self.session_id = session_id if session_id else SESSION_ID
        self.base_url = 'https://roverdata2-production.up.railway.app/api'
        self.endpoints = {
            'status': f"{self.base_url}/rover/status",
            'move': f"{self.base_url}/rover/move",
            'stop': f"{self.base_url}/rover/stop",
            'charge': f"{self.base_url}/rover/charge"
        }
        self.timeout = 3  # seconds
        
    def get_params(self):
        return {'session_id': self.session_id}
    
    def _make_request(self, endpoint, method='get', params=None, retries=2):
        """Generic request handler with retry logic"""
        url = self.endpoints.get(endpoint)
        if not url:
            print(f"Invalid endpoint: {endpoint}")
            return None
            
        params = params or self.get_params()
        
        for attempt in range(retries + 1):
            try:
                if method.lower() == 'get':
                    response = requests.get(url, params=params, timeout=self.timeout)
                else:
                    response = requests.post(url, params=params, timeout=self.timeout)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"API request failed (attempt {attempt + 1}): {response.status_code}")
                    if attempt == retries and response.text:
                        print(f"Error details: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                if attempt == retries:
                    print(f"API connection error: {str(e)}")
                time.sleep(1)  # Wait before retry
        
        return None
    
    def get_rover_status(self):
        """Get rover status from API"""
        data = self._make_request('status')
        if not data:
            return None
            
        if 'error' in data:
            print(f"API Error: {data['error']}")
            return None
        
        # Ensure all required fields are present with defaults
        status = {
            'status': data.get('status', 'idle'),
            'battery': int(data.get('battery', 100)),
            'coordinates': data.get('coordinates', [0, 0])
        }
        
        # Handle charging if battery is low
        if status['battery'] <= 5 and status['status'] != 'charging':
            self.start_charging()
            status['status'] = 'charging'
        elif status['battery'] >= 80 and status['status'] == 'charging':
            self.stop_charging()
            status['status'] = 'moving'
        
        return status
        
    def start_charging(self):
        """Send charge command to API"""
        result = self._make_request('charge', method='post')
        if result and 'error' not in result:
            print("Charging started successfully")
            return True
        return False
            
    def stop_charging(self):
        """Send stop charging command to API"""
        result = self._make_request('stop', method='post')
        if result and 'error' not in result:
            print("Charging stopped successfully")
            return True
        return False
            
    def send_move_command(self, direction):
        """Send movement command to API"""
        params = self.get_params()
        params['direction'] = direction.lower()