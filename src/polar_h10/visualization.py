import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

class HeartRateDisplay:
    """Real-time heart rate visualization."""
    
    def __init__(self, max_points=100):
        """Initialize the heart rate display with a maximum number of points to show.
        
        Args:
            max_points: Maximum number of data points to display at once
        """
        self.max_points = max_points
        self.timestamps = []
        self.heart_rates = []
        self.fig = None
        self.ax = None
        self.line = None
        try:
            self.initialize_plot()
        except Exception as e:
            print(f"Failed to initialize plot: {e}")

    def initialize_plot(self):
        """Initialize the matplotlib plot with proper axes and labels."""
        try:
            self.fig, self.ax = plt.subplots()
            self.ax.set_ylim(40, 200)
            self.ax.set_xlim(0, 30)  # Start with 30 second window
            self.ax.set_title("Real-time Heart Rate")
            self.ax.set_xlabel("Time (s)")
            self.ax.set_ylabel("Heart Rate (BPM)")
            # Initialize with empty lists for x and y data
            plot_data = self.ax.plot([0], [0], 'b-', label='Heart Rate')
            self.line = plot_data[0] 
            self.ax.grid(True)
            self.ax.legend()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize plot: {e}")
    
    def update_data(self, hr):
        """Update the data arrays with new heart rate value.
        
        Args:
            hr: New heart rate value to add to the display
        """
        self.heart_rates.append(hr)
        if len(self.timestamps) == 0:
            self.timestamps.append(0)
        else:
            self.timestamps.append(self.timestamps[-1] + 1)
        
        if len(self.timestamps) > self.max_points:
            self.timestamps.pop(0)
            self.heart_rates.pop(0)

    def clear_data(self):
        """Clear all stored data from the display."""
        self.timestamps = []
        self.heart_rates = []
        if self.line is not None:
            self.line.set_data([], [])

    def update_plot(self):
        """Update the display with current data.
        
        Should be called after update_data() to refresh the visualization.
        """
        if self.line is None or self.ax is None:
            return
            
        self.line.set_data(self.timestamps, self.heart_rates)
        self.ax.relim()
        self.ax.autoscale_view()
        try:
            plt.draw()
            plt.pause(0.01)
        except Exception as e:
            print(f"Failed to update plot: {e}")

