import unittest
from unittest.mock import Mock, patch
import numpy as np
import matplotlib.pyplot as plt
from polar_h10.visualization import HeartRateDisplay

class TestHeartRateDisplay(unittest.TestCase):
    """Test suite for heart rate visualization functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.display = HeartRateDisplay()
        plt.ion()

    @patch('matplotlib.pyplot.figure')
    def test_initialize_plot(self, mock_figure):
        """Test plot initialization and setup."""
        self.display.initialize_plot()
        assert self.display.fig is not None
        assert self.display.ax is not None
        assert self.display.line is not None
    
    def test_update_data(self):
        """Test data update mechanism."""
        initial_length = len(self.display.heart_rates)
        self.display.update_data(75)
        assert len(self.display.heart_rates) == initial_length + 1
        assert self.display.heart_rates[-1] == 75
    
    def test_max_points_limit(self):
        """Test maximum points limitation in the plot."""
        max_points = self.display.max_points
        for i in range(max_points + 10):
            self.display.update_data(i)
        assert len(self.display.heart_rates) <= max_points
    
    @patch('matplotlib.pyplot.draw')
    def test_update_plot(self, mock_draw):
        """Test plot update functionality."""
        self.display.initialize_plot()
        self.display.update_data(70)
        self.display.update_plot()
        mock_draw.assert_called_once()
    
    def test_clear_data(self):
        """Test data clearing functionality."""
        self.display.update_data(70)
        self.display.clear_data()
        assert len(self.display.heart_rates) == 0
        assert len(self.display.timestamps) == 0
    
    def tearDown(self):
        """Clean up after each test method."""
        plt.close('all')
        self.display = None

