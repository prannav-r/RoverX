from typing import Dict, List, Optional
import time
from dataclasses import dataclass
from enum import Enum

class PowerState(Enum):
    NORMAL = "normal"
    LOW_POWER = "low_power"
    CRITICAL = "critical"
    RECHARGING = "recharging"

@dataclass
class PowerMetrics:
    battery_level: float
    power_consumption: float
    temperature: float
    voltage: float
    current: float
    timestamp: float

class PowerManagementSystem:
    def __init__(self):
        self.current_state = PowerState.NORMAL
        self.power_history: List[PowerMetrics] = []
        self.charging_station_location = None
        
        # Power consumption rates (watts)
        self.base_consumption = 10.0
        self.movement_consumption = 20.0
        self.sensor_consumption = 5.0
        self.communication_consumption = 15.0
        
        # Battery thresholds
        self.RECHARGE_START = 5.0  # Start recharging at 5%
        self.RECHARGE_STOP = 80.0  # Stop recharging at 80%
        self.COMMS_LOSS = 10.0     # Communication lost below 10%
        self.LOW_POWER = 20.0      # Enter low power mode at 20%
        
        # Temperature thresholds
        self.TEMP_WARNING = 45.0   # °C
        self.TEMP_CRITICAL = 60.0  # °C
        
    def update_power_metrics(self, metrics: PowerMetrics):
        """Update power metrics and adjust system state"""
        self.power_history.append(metrics)
        self._cleanup_old_metrics()
        self._update_power_state(metrics)
        
    def _cleanup_old_metrics(self, max_age: float = 3600.0):
        """Remove metrics older than max_age seconds"""
        current_time = time.time()
        self.power_history = [
            metric for metric in self.power_history
            if current_time - metric.timestamp <= max_age
        ]
        
    def _update_power_state(self, metrics: PowerMetrics):
        """Update power state based on current metrics"""
        if metrics.battery_level <= self.COMMS_LOSS:
            self.current_state = PowerState.CRITICAL
        elif metrics.battery_level <= self.RECHARGE_START:
            self.current_state = PowerState.CRITICAL
        elif metrics.battery_level <= self.LOW_POWER:
            self.current_state = PowerState.LOW_POWER
        elif metrics.battery_level >= self.RECHARGE_STOP:
            self.current_state = PowerState.NORMAL
        elif self.current_state == PowerState.RECHARGING:
            self.current_state = PowerState.NORMAL
            
        # Check temperature
        if metrics.temperature >= self.TEMP_CRITICAL:
            self.current_state = PowerState.CRITICAL
        elif metrics.temperature >= self.TEMP_WARNING:
            self.current_state = PowerState.LOW_POWER
            
    def calculate_power_consumption(self, is_moving: bool, 
                                  sensor_active: bool, 
                                  communication_active: bool) -> float:
        """Calculate current power consumption based on system state"""
        consumption = self.base_consumption
        
        if is_moving:
            consumption += self.movement_consumption
        if sensor_active:
            consumption += self.sensor_consumption
        if communication_active:
            consumption += self.communication_consumption
            
        # Adjust based on power state
        if self.current_state == PowerState.LOW_POWER:
            consumption *= 0.7
        elif self.current_state == PowerState.CRITICAL:
            consumption *= 0.5
            
        return consumption
        
    def estimate_battery_life(self, current_consumption: float) -> float:
        """Estimate remaining battery life in seconds"""
        if not self.power_history:
            return 0.0
            
        current_metrics = self.power_history[-1]
        if current_consumption <= 0:
            return float('inf')
            
        return (current_metrics.battery_level / 100.0) * \
               (current_metrics.voltage * current_metrics.current) / current_consumption
               
    def get_power_recommendations(self) -> Dict:
        """Get power management recommendations"""
        if not self.power_history:
            return {}
            
        current_metrics = self.power_history[-1]
        recommendations = {
            "state": self.current_state.value,
            "battery_level": current_metrics.battery_level,
            "temperature": current_metrics.temperature,
            "actions": []
        }
        
        if self.current_state == PowerState.CRITICAL:
            recommendations["actions"].extend([
                "Stop all non-essential operations",
                "Return to charging station",
                "Reduce sensor sampling rate",
                "Minimize communication"
            ])
        elif self.current_state == PowerState.LOW_POWER:
            recommendations["actions"].extend([
                "Reduce movement speed",
                "Optimize sensor usage",
                "Limit communication frequency",
                "Monitor temperature"
            ])
            
        return recommendations
        
    def set_charging_station(self, location: List[float]):
        """Set the location of the charging station"""
        self.charging_station_location = location
        
    def should_return_to_charge(self) -> bool:
        """Determine if rover should return to charging station"""
        if not self.power_history:
            return False
            
        current_metrics = self.power_history[-1]
        return (current_metrics.battery_level <= self.RECHARGE_START or
                current_metrics.temperature >= self.TEMP_WARNING)
                
    def get_charging_station_path(self, current_position: List[float]) -> Optional[List[float]]:
        """Get path to charging station if needed"""
        if not self.charging_station_location or not self.should_return_to_charge():
            return None
            
        return self.charging_station_location 