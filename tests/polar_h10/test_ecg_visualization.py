import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from src.polar_h10.ecg_visualization import ECGVisualizer

@pytest.fixture
def mock_figure():
    with patch('matplotlib.pyplot.figure') as mock_fig:
        figure = MagicMock()
        ax = MagicMock()
        figure.add_subplot.return_value = ax
        mock_fig.return_value = figure
        yield figure

@pytest.fixture
def mock_line():
    line = MagicMock()
    line.set_data = MagicMock()
    return line

@pytest.fixture
def visualizer(mock_figure):
    with patch('matplotlib.animation.FuncAnimation'):
        viz = ECGVisualizer(buffer_size=1000, update_interval=50)
        viz.line = mock_line()
        return viz

def test_initialization(visualizer):
    assert visualizer.buffer_size == 1000
    assert visualizer.update_interval == 50
    assert len(visualizer.data_buffer) == 0
    assert visualizer.is_running is False

def test_buffer_management(visualizer):
    # Test adding data to buffer
    test_data = [1.0, 2.0, 3.0]
    for value in test_data:
        visualizer.add_data_point(value)
    
    assert len(visualizer.data_buffer) == len(test_data)
    assert list(visualizer.data_buffer) == test_data

    # Test buffer overflow
    large_data = list(range(2000))
    for value in large_data:
        visualizer.add_data_point(value)
    
    assert len(visualizer.data_buffer) == visualizer.buffer_size
    assert list(visualizer.data_buffer)[-1] == large_data[-1]

def test_plot_update(visualizer, mock_line):
    test_data = np.array([1.0, 2.0, 3.0])
    for value in test_data:
        visualizer.add_data_point(value)
    
    visualizer._update(0)  # Frame number doesn't matter for test
    
    mock_line.set_data.assert_called_once()
    called_args = mock_line.set_data.call_args[0]
    np.testing.assert_array_equal(called_args[1], test_data)

def test_start_stop(visualizer):
    with patch('matplotlib.animation.FuncAnimation') as mock_anim:
        visualizer.start()
        assert visualizer.is_running is True
        mock_anim.assert_called_once()
        
        visualizer.stop()
        assert visualizer.is_running is False

def test_cleanup(visualizer):
    visualizer.start()
    visualizer.cleanup()
    assert visualizer.is_running is False
    assert visualizer.animation is None
    assert len(visualizer.data_buffer) == 0

def test_axis_configuration(visualizer):
    assert visualizer.ax.set_title.called
    assert visualizer.ax.set_xlabel.called
    assert visualizer.ax.set_ylabel.called
    assert visualizer.ax.grid.called

def test_animation_creation(visualizer):
    with patch('matplotlib.animation.FuncAnimation') as mock_anim:
        visualizer.start()
        mock_anim.assert_called_once_with(
            visualizer.fig,
            visualizer._update,
            interval=visualizer.update_interval,
            blit=True
        )

def test_error_handling(visualizer):
    # Test invalid data point
    with pytest.raises(ValueError):
        visualizer.add_data_point("invalid")
    
    # Test invalid buffer size
    with pytest.raises(ValueError):
        ECGVisualizer(buffer_size=0)
    
    with pytest.raises(ValueError):
        ECGVisualizer(buffer_size=-100)

    # Test invalid update interval
    with pytest.raises(ValueError):
        ECGVisualizer(update_interval=0)
    
    with pytest.raises(ValueError):
        ECGVisualizer(update_interval=-50)

