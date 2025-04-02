import math
from typing import List, Tuple, Dict, Optional
import numpy as np
import time

class NavigationSystem:
    def __init__(self):
        self.obstacle_threshold = 50  # cm
        self.safe_distance = 100  # cm
        self.path_history = []
        self.obstacle_map = {}
        self.current_position = [0, 0]
        self.current_direction = "forward"
        self.search_pattern_width = 200  # cm
        self.search_pattern_length = 300  # cm
        self.last_turn_time = 0
        self.turn_interval = 5  # seconds
        self.current_pattern_angle = 0
        
    def process_ultrasonic_data(self, distance: float, angle: float) -> Dict:
        """Process ultrasonic sensor data to detect obstacles"""
        if distance < self.obstacle_threshold:
            # Calculate obstacle position relative to rover
            obstacle_x = self.current_position[0] + distance * math.cos(math.radians(angle))
            obstacle_y = self.current_position[1] + distance * math.sin(math.radians(angle))
            
            # Update obstacle map
            self.obstacle_map[(round(obstacle_x), round(obstacle_y))] = distance
            
            return {
                "obstacle_detected": True,
                "distance": distance,
                "angle": angle,
                "position": [obstacle_x, obstacle_y]
            }
        return {"obstacle_detected": False}
    
    def optimize_path(self, target_position: List[float], battery_level: float) -> List[Tuple[float, float]]:
        """Optimize path using zigzag pattern and avoiding straight lines"""
        path = []
        current_pos = self.current_position.copy()
        current_time = time.time()
        
        # Calculate direct path
        dx = target_position[0] - current_pos[0]
        dy = target_position[1] - current_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Determine number of zigzag segments based on distance and battery
        if battery_level < 20:
            segment_length = 50  # Shorter segments for low battery
        else:
            segment_length = 100  # Longer segments for normal battery
            
        num_segments = max(1, int(distance / segment_length))
        
        # Generate zigzag path
        for i in range(num_segments):
            # Calculate base position for this segment
            base_x = current_pos[0] + (dx/num_segments) * (i+1)
            base_y = current_pos[1] + (dy/num_segments) * (i+1)
            
            # Add zigzag points
            if i % 2 == 0:
                # Zig right
                zig_x = base_x + self.search_pattern_width * math.cos(math.radians(self.current_pattern_angle + 90))
                zig_y = base_y + self.search_pattern_width * math.sin(math.radians(self.current_pattern_angle + 90))
            else:
                # Zag left
                zig_x = base_x + self.search_pattern_width * math.cos(math.radians(self.current_pattern_angle - 90))
                zig_y = base_y + self.search_pattern_width * math.sin(math.radians(self.current_pattern_angle - 90))
                
            # Check if zigzag point is safe
            if self._is_position_safe([zig_x, zig_y]):
                path.append((zig_x, zig_y))
            else:
                # Find alternative safe point
                alt_point = self._find_safe_alternative([zig_x, zig_y])
                if alt_point:
                    path.append(alt_point)
                    
            # Add intermediate points for smoother movement
            if i < num_segments - 1:
                next_base_x = current_pos[0] + (dx/num_segments) * (i+2)
                next_base_y = current_pos[1] + (dy/num_segments) * (i+2)
                path.extend(self._generate_smooth_curve(
                    [zig_x, zig_y],
                    [next_base_x, next_base_y]
                ))
                
        return path
    
    def _generate_smooth_curve(self, start: List[float], end: List[float]) -> List[Tuple[float, float]]:
        """Generate smooth curve between two points"""
        curve_points = []
        num_points = 5
        
        for i in range(num_points):
            t = i / (num_points - 1)
            # Use quadratic Bezier curve for smooth movement
            x = (1-t)**2 * start[0] + 2*(1-t)*t * (start[0] + end[0])/2 + t**2 * end[0]
            y = (1-t)**2 * start[1] + 2*(1-t)*t * (start[1] + end[1])/2 + t**2 * end[1]
            curve_points.append((x, y))
            
        return curve_points
    
    def _is_position_safe(self, position: List[float]) -> bool:
        """Check if a position is safe from obstacles"""
        for obs_pos, distance in self.obstacle_map.items():
            dx = position[0] - obs_pos[0]
            dy = position[1] - obs_pos[1]
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < self.safe_distance:
                return False
        return True
    
    def _find_safe_alternative(self, target: List[float]) -> Optional[Tuple[float, float]]:
        """Find a safe alternative point near the target"""
        # Try different angles and distances
        angles = [45, 90, 135, 180, 225, 270, 315]
        distances = [self.safe_distance * 1.2, self.safe_distance * 1.5]
        
        for distance in distances:
            for angle in angles:
                test_x = target[0] + distance * math.cos(math.radians(angle))
                test_y = target[1] + distance * math.sin(math.radians(angle))
                if self._is_position_safe([test_x, test_y]):
                    return (test_x, test_y)
        return None
    
    def update_position(self, new_position: List[float], direction: str):
        """Update rover position and direction"""
        self.current_position = new_position
        self.current_direction = direction
        self.path_history.append((new_position[0], new_position[1]))
        
        # Update pattern angle based on movement
        current_time = time.time()
        if current_time - self.last_turn_time > self.turn_interval:
            self.current_pattern_angle = (self.current_pattern_angle + 45) % 360
            self.last_turn_time = current_time
        
    def get_navigation_commands(self, target_position: List[float], battery_level: float) -> Dict:
        """Generate navigation commands based on current state"""
        path = self.optimize_path(target_position, battery_level)
        
        if not path:
            return {
                "command": "stop",
                "reason": "no_safe_path"
            }
            
        next_point = path[0]
        dx = next_point[0] - self.current_position[0]
        dy = next_point[1] - self.current_position[1]
        
        # Calculate required movement
        angle = math.degrees(math.atan2(dy, dx))
        distance = math.sqrt(dx*dx + dy*dy)
        
        return {
            "command": "move",
            "angle": angle,
            "distance": distance,
            "path": path
        } 