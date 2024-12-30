import unittest
import os
import tempfile
import csv
import shutil
from datetime import datetime
from polar_h10.data_logger import DataLogger

class TestDataLogger(unittest.TestCase):
    """Test suite for data logging functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = DataLogger(self.temp_dir)

    def test_initialize_logger(self):
        """Test logger initialization and directory creation."""
        new_dir = os.path.join(self.temp_dir, 'test_logs')
        logger = DataLogger(new_dir)
        assert os.path.exists(new_dir)
        assert logger.log_dir == new_dir
    
    def test_generate_filename(self):
        """Test log filename generation."""
        filename = self.logger.generate_filename()
        assert filename.endswith('.csv')
        assert datetime.now().strftime('%Y%m%d') in filename
    
    def test_log_heart_rate(self):
        """Test heart rate data logging."""
        test_hr = 75
        self.logger.log_heart_rate(test_hr)
        
        with open(self.logger.current_file, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            row = next(reader)
            assert int(row[1]) == test_hr
    
    def test_file_creation(self):
        """Test log file creation and header writing."""
        self.logger.start_new_log()
        assert os.path.exists(self.logger.current_file)
        
        with open(self.logger.current_file, 'r') as f:
            header = f.readline().strip()
            assert header == "Timestamp,HeartRate"
    
    def test_multiple_entries(self):
        """Test logging multiple heart rate entries."""
        test_rates = [70, 75, 80]
        for rate in test_rates:
            self.logger.log_heart_rate(rate)
        
        with open(self.logger.current_file, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            logged_rates = [int(row[1]) for row in reader]
            assert logged_rates == test_rates
    
    def test_error_handling(self):
        """Test error handling for file operations."""
        # Test with invalid directory
        with self.assertRaises(Exception):
            DataLogger("/invalid/path/that/doesnt/exist")
    
    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir)
        self.logger = None

