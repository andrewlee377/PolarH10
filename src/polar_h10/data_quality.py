from collections import deque
from datetime import datetime, timedelta
import statistics
import logging

class DataQuality:
    """Handles data quality monitoring and buffering for Polar H10."""
    
    def __init__(self, buffer_size=60):
        self.logger = logging.getLogger(__name__)
        self.buffer = deque(maxlen=buffer_size)
        self.signal_quality = 100.0
        self.last_update = None
        self.data_gaps = 0
        self.anomalies = 0
        
    def add_reading(self, timestamp, heart_rate):
        """Add a new heart rate reading and analyze its quality."""
        current_quality = self._calculate_quality(timestamp, heart_rate)
        self.buffer.append((timestamp, heart_rate, current_quality))
        self._update_signal_quality()
        self.last_update = timestamp
        
    def get_stats(self):
        """Get current data quality statistics."""
        if not self.buffer:
            return None
            
        readings = [hr for _, hr, _ in self.buffer]
        return {
            'signal_quality': self.signal_quality,
            'data_gaps': self.data_gaps,
            'anomalies': self.anomalies,
            'mean_hr': statistics.mean(readings),
            'std_dev': statistics.stdev(readings) if len(readings) > 1 else 0,
            'buffer_size': len(self.buffer)
        }
        
    def _calculate_quality(self, timestamp, heart_rate):
        """Calculate quality score for a single reading."""
        quality = 100.0
        
        # Check for data gaps
        if self.last_update:
            time_gap = (timestamp - self.last_update).total_seconds()
            if time_gap > 1.1:  # Expected update rate is ~1s
                self.data_gaps += 1
                quality -= min(50, time_gap * 10)  # Reduce quality based on gap size
        
        # Check for physiological plausibility
        if not (30 <= heart_rate <= 240):
            self.anomalies += 1
            quality -= 50
        
        # Check for sudden changes
        if len(self.buffer) > 0:
            last_hr = self.buffer[-1][1]
            hr_change = abs(heart_rate - last_hr)
            if hr_change > 20:  # Sudden change threshold
                self.anomalies += 1
                quality -= min(30, hr_change)
                
        return max(0.0, quality)
        
    def _update_signal_quality(self):
        """Update overall signal quality based on recent readings."""
        if not self.buffer:
            return
            
        # Convert deque to list for slicing
        buffer_list = list(self.buffer)
        # Get last 10 readings or all if less than 10
        recent_readings = buffer_list[-min(10, len(buffer_list)):]
        recent_quality = [q for _, _, q in recent_readings]
        self.signal_quality = statistics.mean(recent_quality)
        
    def clear(self):
        """Clear all stored data."""
        self.buffer.clear()
        self.signal_quality = 100.0
        self.data_gaps = 0
        self.anomalies = 0
        self.last_update = None

