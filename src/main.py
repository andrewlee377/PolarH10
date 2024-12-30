import asyncio
import logging
import argparse
import sys
import os
import matplotlib

# Use Agg backend for testing, TkAgg for normal use
if 'PYTEST_CURRENT_TEST' in os.environ:
    matplotlib.use('Agg')
else:
    matplotlib.use('TkAgg')
from polar_h10 import PolarH10, HeartRateDisplay, DataLogger
from bleak.exc import BleakError

async def hr_callback(hr_display, data_logger, hr):
    """Handle incoming heart rate data."""
    if hr is not None:
        print(f"Heart Rate: {hr} BPM")
        if hr_display:
            await hr_display.update(hr)
        if data_logger:
            await data_logger.log_hr(hr)

async def main(device_id, polar=None, hr_display=None, data_logger=None):
    """Main application entry point.
    
    Args:
        device_id: The Polar H10 device ID 
        polar: Optional PolarH10 instance for testing
        hr_display: Optional HeartRateDisplay instance for testing 
        data_logger: Optional DataLogger instance for testing
    """
    logging.basicConfig(
        level=logging.INFO,  
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    try:
        # Use provided instances or create new ones
        data_logger = data_logger or DataLogger()
        polar = polar or PolarH10()
        
        logger.info("Attempting to connect to Polar H10...")
        
        for attempt in range(3):  # Try up to 3 times
            try:
                await polar.connect()
                break
            except BleakError as e:
                if attempt == 2:  # Last attempt
                    raise
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}. Retrying...")
                await asyncio.sleep(2)
        
        logger.info("Successfully connected to Polar H10")
        callback = lambda hr: asyncio.create_task(hr_callback(hr_display, data_logger, hr))
        await polar.start_hr_monitoring(callback)
        
        # Keep the script running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await polar.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Polar H10 Monitor')
    parser.add_argument('--mode', choices=['HR', 'ECG'], default='HR',
                    help='Monitoring mode (HR or ECG)')
    parser.add_argument('--visualize', action='store_true',
                    help='Enable real-time visualization')
    parser.add_argument('--log-level', default='INFO',
                    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                    help='Logging level')
    
    args = parser.parse_args()
    asyncio.run(main(None, hr_display=HeartRateDisplay() if args.visualize else None))

