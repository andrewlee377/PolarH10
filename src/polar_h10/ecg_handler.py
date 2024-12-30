import logging
from typing import Callable, Optional
from bleak import BleakClient
from dataclasses import dataclass
from enum import Enum
import struct

logger = logging.getLogger(__name__)

# PMD Service and Characteristic UUIDs
PMD_SERVICE = "FB005C80-02E7-F387-1CAD-8ACD2D8DF0C8"
PMD_CONTROL = "FB005C81-02E7-F387-1CAD-8ACD2D8DF0C8"
PMD_DATA = "FB005C82-02E7-F387-1CAD-8ACD2D8DF0C8"

class ECGError(Exception):
    """Base exception for ECG-related errors."""
    pass

class ECGStreamError(ECGError):
    """Exception raised for errors during ECG streaming."""
    pass

class ECGControlError(ECGError):
    """Exception raised for errors in ECG control operations."""
    pass

@dataclass
class ECGMeasurement:
    """Represents a single ECG measurement."""
    timestamp: int
    microvolts: float
    data_quality: int

class ECGHandler:
    """Handles ECG measurements from Polar H10 device."""
    
    def __init__(self, client: BleakClient):
        """Initialize the ECG handler.
        
        Args:
            client: BleakClient instance for the connected Polar H10
        """
        self._client = client
        self._streaming = False
        self._callback: Optional[Callable[[ECGMeasurement], None]] = None
        
    async def start_streaming(self, callback: Callable[[ECGMeasurement], None]) -> None:
        """Start ECG data streaming.
        
        Args:
            callback: Function to call with each ECG measurement
            
        Raises:
            ECGStreamError: If streaming fails to start
            ECGControlError: If control commands fail
        """
        if self._streaming:
            raise ECGStreamError("ECG streaming is already active")
        
        try:
            # Enable ECG streaming via PMD Control characteristic
            ecg_control = bytearray([0x02, 0x00, 0x00, 0x01, 0x82, 0x00, 0x01, 0x01, 0x0E, 0x00])
            await self._client.write_gatt_char(PMD_CONTROL, ecg_control)
            
            # Set up notification handler
            self._callback = callback
            await self._client.start_notify(PMD_DATA, self._handle_ecg_data)
            
            self._streaming = True
            logger.info("ECG streaming started successfully")
            
        except Exception as e:
            raise ECGStreamError(f"Failed to start ECG streaming: {str(e)}")
        
    async def stop_streaming(self) -> None:
        """Stop ECG data streaming.
        
        Raises:
            ECGStreamError: If streaming fails to stop
        """
        if not self._streaming:
            return
            
        try:
            # Disable ECG streaming
            ecg_control = bytearray([0x02, 0x00, 0x00, 0x01, 0x82, 0x00, 0x01, 0x01, 0x00, 0x00])
            await self._client.write_gatt_char(PMD_CONTROL, ecg_control)
            
            # Stop notifications
            await self._client.stop_notify(PMD_DATA)
            
            self._streaming = False
            self._callback = None
            logger.info("ECG streaming stopped successfully")
            
        except Exception as e:
            raise ECGStreamError(f"Failed to stop ECG streaming: {str(e)}")
        
    def _handle_ecg_data(self, _, data: bytearray) -> None:
        """Handle incoming ECG data.
        
        Args:
            _: Characteristic handle (unused)
            data: Raw ECG data from the device
        """
        if not self._callback:
            return
            
        try:
            # Parse frame type and sample count
            frame_type = data[0]
            if frame_type != 0x02:  # ECG frame type
                return
                
            sample_count = (len(data) - 3) // 3  # 3 bytes per sample
            
            # Parse samples
            for i in range(sample_count):
                offset = 3 + (i * 3)
                sample_bytes = data[offset:offset + 3]
                
                # Convert 24-bit signed int to microvolts
                value = int.from_bytes(sample_bytes, byteorder='little', signed=True)
                microvolts = value * 0.25  # Scale factor for Polar H10
                
                measurement = ECGMeasurement(
                    timestamp=int.from_bytes(data[1:3], byteorder='little'),
                    microvolts=microvolts,
                    data_quality=1  # Default quality, can be enhanced
                )
                
                self._callback(measurement)
                
        except Exception as e:
            logger.error(f"Error processing ECG data: {str(e)}")

    @property
    def is_streaming(self) -> bool:
        """Return whether ECG streaming is active."""
        return self._streaming

