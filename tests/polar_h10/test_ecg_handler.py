import pytest
from unittest.mock import Mock, patch, call
import numpy as np
from polar_h10.ecg_handler import ECGHandler
from bleak.exc import BleakError

@pytest.fixture
def mock_client():
    client = Mock()
    client.is_connected = True
    return client

@pytest.fixture
def mock_callbacks():
    return {
        'data_callback': Mock(),
        'error_callback': Mock(),
        'connection_callback': Mock()
    }

@pytest.fixture
def ecg_handler(mock_client, mock_callbacks):
    handler = ECGHandler(
        client=mock_client,
        device_id="test_device",
        data_callback=mock_callbacks['data_callback'],
        error_callback=mock_callbacks['error_callback'],
        connection_callback=mock_callbacks['connection_callback']
    )
    yield handler
    handler.stop_streaming()

class TestECGHandler:
    def test_initialization(self, ecg_handler, mock_client):
        assert ecg_handler.client == mock_client
        assert ecg_handler.device_id == "test_device"
        assert not ecg_handler.is_streaming
        
    @pytest.mark.asyncio
    async def test_start_streaming_success(self, ecg_handler, mock_client):
        mock_client.write_gatt_char.return_value = None
        
        await ecg_handler.start_streaming()
        
        assert ecg_handler.is_streaming
        assert mock_client.write_gatt_char.call_count == 2  # PMD control point and config
        
    @pytest.mark.asyncio
    async def test_stop_streaming(self, ecg_handler, mock_client):
        mock_client.write_gatt_char.return_value = None
        await ecg_handler.start_streaming()
        
        await ecg_handler.stop_streaming()
        
        assert not ecg_handler.is_streaming
        assert mock_client.write_gatt_char.call_count >= 3  # Including stop command
        
    def test_handle_ecg_data(self, ecg_handler, mock_callbacks):
        # Simulate raw ECG data (example format)
        raw_data = bytes([0x00, 0x01, 0x02, 0x03] * 4)  # 16 bytes of sample data
        
        ecg_handler._handle_ecg_data(raw_data)
        
        mock_callbacks['data_callback'].assert_called_once()
        data = mock_callbacks['data_callback'].call_args[0][0]
        assert isinstance(data, np.ndarray)
        
    @pytest.mark.asyncio
    async def test_connection_lost(self, ecg_handler, mock_client, mock_callbacks):
        mock_client.is_connected = False
        
        with pytest.raises(BleakError):
            await ecg_handler.start_streaming()
        
        mock_callbacks['connection_callback'].assert_called_with(False)
        
    def test_invalid_data_format(self, ecg_handler, mock_callbacks):
        invalid_data = bytes([0x00])  # Too short to be valid
        
        ecg_handler._handle_ecg_data(invalid_data)
        
        mock_callbacks['error_callback'].assert_called_once()
        
    @pytest.mark.asyncio
    async def test_multiple_start_calls(self, ecg_handler, mock_client):
        mock_client.write_gatt_char.return_value = None
        
        await ecg_handler.start_streaming()
        await ecg_handler.start_streaming()  # Second call
        
        # Should only initialize once
        assert mock_client.write_gatt_char.call_count == 2
        
    @pytest.mark.asyncio
    async def test_error_handling_during_write(self, ecg_handler, mock_client, mock_callbacks):
        mock_client.write_gatt_char.side_effect = BleakError("Mock error")
        
        with pytest.raises(BleakError):
            await ecg_handler.start_streaming()
        
        mock_callbacks['error_callback'].assert_called_once()
        assert not ecg_handler.is_streaming
        
    def test_data_validation(self, ecg_handler, mock_callbacks):
        # Test with valid data format
        valid_data = bytes([0x00, 0x01, 0x02, 0x03] * 4)
        ecg_handler._handle_ecg_data(valid_data)
        assert mock_callbacks['error_callback'].call_count == 0
        
        # Test with invalid data format
        invalid_data = bytes([0x00, 0x01])
        ecg_handler._handle_ecg_data(invalid_data)
        assert mock_callbacks['error_callback'].call_count == 1

