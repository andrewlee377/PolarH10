import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from src.main import hr_callback, main
from src.polar_h10.polar_device import PolarH10
from src.polar_h10.visualization import HeartRateDisplay
from src.polar_h10.data_logger import DataLogger

@pytest.fixture
def mock_display():
    display = Mock(spec=HeartRateDisplay)
    display.update = AsyncMock()
    return display

@pytest.fixture
def mock_logger():
    logger = Mock(spec=DataLogger)
    logger.log_hr = AsyncMock()
    return logger

@pytest.fixture
def mock_polar():
    polar = Mock(spec=PolarH10)
    polar.connect = AsyncMock()
    polar.disconnect = AsyncMock()
    return polar

@pytest.mark.asyncio
async def test_hr_callback_updates_display_and_logs():
    # Arrange
    mock_display = Mock(spec=HeartRateDisplay)
    mock_display.update = AsyncMock()
    mock_logger = Mock(spec=DataLogger)
    mock_logger.log_hr = AsyncMock()
    hr = 75
    
    # Act
    await hr_callback(mock_display, mock_logger, hr)
    
    # Assert
    mock_display.update.assert_awaited_once_with(hr)
    mock_logger.log_hr.assert_awaited_once_with(hr)

@pytest.mark.asyncio
async def test_hr_callback_handles_none_hr():
    # Arrange
    mock_display = Mock(spec=HeartRateDisplay)
    mock_display.update = AsyncMock()
    mock_logger = Mock(spec=DataLogger)
    mock_logger.log_hr = AsyncMock()
    hr = None
    
    # Act
    await hr_callback(mock_display, mock_logger, hr)
    
    # Assert
    mock_display.update.assert_not_awaited()
    mock_logger.log_hr.assert_not_awaited()

@pytest.mark.asyncio
async def test_main():
    # Arrange
    mock_display = Mock(spec=HeartRateDisplay)
    mock_logger = Mock(spec=DataLogger)
    mock_polar = Mock(spec=PolarH10)
    
    mock_polar.connect = AsyncMock()
    mock_polar.disconnect = AsyncMock()
    
    device_id = "12:34:56:78:90:AB"
    
    # Act
    with patch('asyncio.get_event_loop', return_value=Mock()):
        with patch('signal.signal'):  # Mock signal handler
            # Start main but cancel after a short delay to simulate Ctrl+C
            task = asyncio.create_task(main(device_id, mock_polar, mock_display, mock_logger))
            await asyncio.sleep(0.1)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    # Assert
    mock_polar.connect.assert_awaited_once()
    mock_polar.disconnect.assert_awaited_once()
