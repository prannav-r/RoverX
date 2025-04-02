from typing import Dict, List, Tuple
import numpy as np
from dataclasses import dataclass
from enum import Enum

class SensorType(Enum):
    ULTRASONIC = "ultrasonic"
    IR = "ir"
    RFID = "rfid"
    ACCELEROMETER = "accelerometer"

@dataclass
class SensorReading:
    type: SensorType
    value: float
    timestamp: float
    position: Tuple[float, float]
    confidence: float

class SensorFusionSystem:
    def __init__(self):
        self.sensor_readings = []
        self.survivor_detections = []
        self.sensor_weights = {
            SensorType.ULTRASONIC: 0.3,
            SensorType.IR: 0.3,
            SensorType.RFID: 0.4,
            SensorType.ACCELEROMETER: 0.1
        }
        
        # Sensor thresholds
        self.thresholds = {
            SensorType.ULTRASONIC: 200,  # cm
            SensorType.IR: 0.7,          # reflection coefficient
            SensorType.RFID: 0.5,        # signal strength
            SensorType.ACCELEROMETER: 2.0 # m/s²
        }
        
    def add_sensor_reading(self, reading: SensorReading):
        """Add a new sensor reading to the system"""
        self.sensor_readings.append(reading)
        self._cleanup_old_readings()
        self._process_new_reading(reading)
        
    def _cleanup_old_readings(self, max_age: float = 5.0):
        """Remove sensor readings older than max_age seconds"""
        current_time = self.sensor_readings[-1].timestamp if self.sensor_readings else 0
        self.sensor_readings = [
            reading for reading in self.sensor_readings
            if current_time - reading.timestamp <= max_age
        ]
        
    def _process_new_reading(self, reading: SensorReading):
        """Process new sensor reading and update survivor detections"""
        if self._is_survivor_detected(reading):
            self._update_survivor_detection(reading)
            
    def _is_survivor_detected(self, reading: SensorReading) -> bool:
        """Check if a sensor reading indicates a survivor"""
        threshold = self.thresholds[reading.type]
        
        if reading.type == SensorType.ULTRASONIC:
            return reading.value < threshold
        elif reading.type == SensorType.IR:
            return reading.value > threshold
        elif reading.type == SensorType.RFID:
            return reading.value > threshold
        elif reading.type == SensorType.ACCELEROMETER:
            return reading.value > threshold
            
        return False
        
    def _update_survivor_detection(self, reading: SensorReading):
        """Update or create a survivor detection based on new sensor reading"""
        # Check if we have a nearby existing detection
        for detection in self.survivor_detections:
            if self._is_nearby(reading.position, detection['position']):
                # Update existing detection
                detection['confidence'] = self._calculate_confidence(detection, reading)
                detection['last_update'] = reading.timestamp
                detection['sensor_readings'].append(reading)
                return
                
        # Create new detection
        self.survivor_detections.append({
            'position': reading.position,
            'confidence': reading.confidence,
            'last_update': reading.timestamp,
            'sensor_readings': [reading]
        })
        
    def _is_nearby(self, pos1: Tuple[float, float], pos2: Tuple[float, float], 
                   threshold: float = 50.0) -> bool:
        """Check if two positions are within threshold distance"""
        return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2) <= threshold
        
    def _calculate_confidence(self, detection: Dict, new_reading: SensorReading) -> float:
        """Calculate updated confidence based on all sensor readings"""
        readings = detection['sensor_readings'] + [new_reading]
        total_weight = 0
        weighted_sum = 0
        
        for reading in readings:
            weight = self.sensor_weights[reading.type]
            total_weight += weight
            weighted_sum += weight * reading.confidence
            
        return weighted_sum / total_weight if total_weight > 0 else 0
        
    def get_survivor_detections(self, min_confidence: float = 0.5) -> List[Dict]:
        """Get all survivor detections above minimum confidence"""
        return [
            detection for detection in self.survivor_detections
            if detection['confidence'] >= min_confidence
        ]
        
    def get_priority_survivors(self, max_count: int = 5) -> List[Dict]:
        """Get highest priority survivors based on confidence and recency"""
        current_time = self.sensor_readings[-1].timestamp if self.sensor_readings else 0
        
        # Sort by confidence and recency
        sorted_detections = sorted(
            self.survivor_detections,
            key=lambda x: (x['confidence'], current_time - x['last_update']),
            reverse=True
        )
        
        return sorted_detections[:max_count] 