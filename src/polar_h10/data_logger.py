import csv
from datetime import datetime
import os

class DataLogger:
    """Data logging functionality for Polar H10."""
    
    def __init__(self, log_dir="data"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.start_new_log()
    
    def _init_csv(self):
        """Initialize CSV file with headers."""
        try:
            with open(self.current_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'HeartRate'])
        except IOError as e:
            raise RuntimeError(f"Failed to initialize CSV file: {e}")
    
    def generate_filename(self):
        """Generate a new filename for the log file."""
        return os.path.join(
            self.log_dir,
            f"polar_h10_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

    def start_new_log(self):
        """Start a new log file."""
        self.current_file = self.generate_filename()
        self._init_csv()

    def log_heart_rate(self, hr):
        """Log heart rate data."""
        try:
            with open(self.current_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([datetime.now().isoformat(), hr])
        except IOError as e:
            raise RuntimeError(f"Failed to log heart rate data: {e}")

