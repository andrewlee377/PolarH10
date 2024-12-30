import unittest
from unittest.mock import Mock, patch, AsyncMock
import pytest
from polar_h10.polar_device import PolarH10

class TestPolarH10(unittest.TestCase):
    """Test suite for PolarH10 BLE device operations."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.device = PolarH10()
        self.mock_client = Mock()
        self.device.client = self.mock_client
    
    @patch('polar_h10.polar_device.BleakClient')
    async def test_device_discovery(self, mock_bleak):
        """Test device discovery functionality."""
        mock_device = Mock()
        mock_device.address = "00:11:22:33:44:55"
        mock_device.name = "Polar H10"
        mock_bleak.discover.return_value = [mock_device]
        
        device = await self.device.discover_device()
        assert device is not None
        assert device.address == "00:11:22:33:44:55"
    
    @patch('polar_h10.polar_device.BleakClient')
    async def test_connect_device(self, mock_bleak):
        """Test device connection handling."""
        mock_bleak.return_value = self.mock_client
        self.mock_client.connect.return_value = True
        
        result = await self.device.connect()
        assert result is True
        self.mock_client.connect.assert_called_once()
    
    async def test_disconnect_device(self):
        """Test device disconnection."""
        self.mock_client.disconnect.return_value = True
        
        await self.device.disconnect()
        self.mock_client.disconnect.assert_called_once()
    
    @patch('polar_h10.polar_device.BleakClient')
    async def test_start_heart_rate_stream(self, mock_bleak):
        """Test heart rate data streaming."""
        mock_callback = AsyncMock()
        self.device.heart_rate_callback = mock_callback
        
        await self.device.start_heart_rate_stream()
        self.mock_client.start_notify.assert_called_once()
    
    def test_process_heart_rate_data(self):
        """Test heart rate data processing."""
        test_data = bytearray([0x00, 0x65])  # Heart rate of 101
        self.device.process_heart_rate_data(test_data)
        assert self.device.last_heart_rate == 101
    
    def test_validate_services(self):
        """Test service validation."""
        self.mock_client.services = Mock()
        self.mock_client.services.get_characteristic.return_value = True
        
        assert self.device.validate_services() is True
    
    def tearDown(self):
        """Clean up after each test method."""
        self.device = None

