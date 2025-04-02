from typing import Dict, List, Optional
import time
from navigation_system import NavigationSystem
from sensor_fusion import SensorFusionSystem, SensorReading, SensorType
from power_management import PowerManagementSystem, PowerMetrics, PowerState
from dataclasses import dataclass
from enum import Enum

class RoverState(Enum):
    IDLE = "idle"
    SEARCHING = "searching"
    MOVING_TO_SURVIVOR = "moving_to_survivor"
    DELIVERING_AID = "delivering_aid"
    RETURNING_TO_CHARGE = "returning_to_charge"
    RECHARGING = "recharging"

@dataclass
class RoverStatus:
    position: List[float]
    battery_level: float
    temperature: float
    voltage: float
    current: float
    state: RoverState
    survivors_found: int
    timestamp: float

class RoverController:
    def __init__(self):
        self.navigation = NavigationSystem()
        self.sensor_fusion = SensorFusionSystem()
        self.power_management = PowerManagementSystem()
        self.current_state = RoverState.IDLE
        self.status_history: List[RoverStatus] = []
        self.start_position = [0, 0]
        
    def update_status(self, status: RoverStatus):
        """Update rover status and trigger appropriate actions"""
        self.status_history.append(status)
        self._cleanup_old_status()
        
        # Update power metrics
        power_metrics = PowerMetrics(
            battery_level=status.battery_level,
            power_consumption=self._calculate_current_consumption(),
            temperature=status.temperature,
            voltage=status.voltage,
            current=status.current,
            timestamp=status.timestamp
        )
        self.power_management.update_power_metrics(power_metrics)
        
        # Update navigation position
        self.navigation.update_position(status.position, self._get_current_direction())
        
        # Check for state transitions
        self._check_state_transitions(status)
        
    def _cleanup_old_status(self, max_age: float = 3600.0):
        """Remove old status entries"""
        current_time = time.time()
        self.status_history = [
            status for status in self.status_history
            if current_time - status.timestamp <= max_age
        ]
        
    def _calculate_current_consumption(self) -> float:
        """Calculate current power consumption"""
        is_moving = self.current_state in [RoverState.SEARCHING, 
                                         RoverState.MOVING_TO_SURVIVOR,
                                         RoverState.RETURNING_TO_CHARGE]
        sensor_active = self.current_state != RoverState.IDLE
        communication_active = True  # Always maintain basic communication
        
        return self.power_management.calculate_power_consumption(
            is_moving, sensor_active, communication_active
        )
        
    def _get_current_direction(self) -> str:
        """Get current movement direction"""
        if len(self.status_history) < 2:
            return "forward"
            
        current = self.status_history[-1].position
        previous = self.status_history[-2].position
        
        dx = current[0] - previous[0]
        dy = current[1] - previous[1]
        
        if abs(dx) > abs(dy):
            return "right" if dx > 0 else "left"
        else:
            return "forward" if dy > 0 else "backward"
            
    def _check_state_transitions(self, status: RoverStatus):
        """Check and handle state transitions"""
        # Check for critical battery
        if self.power_management.should_return_to_charge():
            self.current_state = RoverState.RETURNING_TO_CHARGE
            return
            
        # Check for charging station arrival
        if (self.current_state == RoverState.RETURNING_TO_CHARGE and
            self._is_at_charging_station(status.position)):
            self.current_state = RoverState.RECHARGING
            return
            
        # Check for charging completion
        if (self.current_state == RoverState.RECHARGING and
            status.battery_level >= self.power_management.RECHARGE_STOP):
            self.current_state = RoverState.IDLE
            return
            
        # Check for survivor detection
        survivors = self.sensor_fusion.get_priority_survivors()
        if survivors and self.current_state == RoverState.SEARCHING:
            self.current_state = RoverState.MOVING_TO_SURVIVOR
            return
            
        # Check for aid delivery completion
        if (self.current_state == RoverState.DELIVERING_AID and
            self._is_aid_delivered()):
            self.current_state = RoverState.SEARCHING
            return
            
    def _is_at_charging_station(self, position: List[float]) -> bool:
        """Check if rover is at charging station"""
        if not self.power_management.charging_station_location:
            return False
            
        charging_station = self.power_management.charging_station_location
        return (abs(position[0] - charging_station[0]) < 10 and
                abs(position[1] - charging_station[1]) < 10)
                
    def _is_aid_delivered(self) -> bool:
        """Check if aid has been delivered to current survivor"""
        # Implementation depends on specific aid delivery mechanism
        return True
        
    def process_sensor_data(self, sensor_type: SensorType, value: float, 
                          position: List[float], confidence: float):
        """Process incoming sensor data"""
        reading = SensorReading(
            type=sensor_type,
            value=value,
            timestamp=time.time(),
            position=position,
            confidence=confidence
        )
        self.sensor_fusion.add_sensor_reading(reading)
        
    def get_next_action(self) -> Dict:
        """Get next action based on current state"""
        if not self.status_history:
            return {"command": "stop"}
            
        current_status = self.status_history[-1]
        
        if self.current_state == RoverState.IDLE:
            return {"command": "start_search"}
            
        elif self.current_state == RoverState.SEARCHING:
            return {"command": "search_pattern"}
            
        elif self.current_state == RoverState.MOVING_TO_SURVIVOR:
            survivors = self.sensor_fusion.get_priority_survivors()
            if not survivors:
                return {"command": "stop"}
                
            target = survivors[0]['position']
            return self.navigation.get_navigation_commands(
                target, current_status.battery_level
            )
            
        elif self.current_state == RoverState.DELIVERING_AID:
            return {"command": "deliver_aid"}
            
        elif self.current_state == RoverState.RETURNING_TO_CHARGE:
            charging_station = self.power_management.get_charging_station_path(
                current_status.position
            )
            if charging_station:
                return self.navigation.get_navigation_commands(
                    charging_station, current_status.battery_level
                )
            return {"command": "stop"}
            
        elif self.current_state == RoverState.RECHARGING:
            return {"command": "recharge"}
            
        return {"command": "stop"}
        
    def get_status_report(self) -> Dict:
        """Generate comprehensive status report"""
        if not self.status_history:
            return {}
            
        current_status = self.status_history[-1]
        power_recommendations = self.power_management.get_power_recommendations()
        survivors = self.sensor_fusion.get_survivor_detections()
        
        return {
            "state": self.current_state.value,
            "position": current_status.position,
            "battery_level": current_status.battery_level,
            "temperature": current_status.temperature,
            "survivors_found": len(survivors),
            "power_state": power_recommendations.get("state"),
            "power_actions": power_recommendations.get("actions", []),
            "estimated_battery_life": self.power_management.estimate_battery_life(
                self._calculate_current_consumption()
            )
        } 