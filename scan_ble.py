import asyncio
import sys
import platform
from bleak import BleakScanner
from bleak.exc import BleakError

async def scan_devices():
    print("Checking system requirements...")
    
    if platform.system() == "Darwin":  # macOS
        print("NOTE: On macOS, you may need to grant Bluetooth permissions to Terminal/IDE")
        print("If scanning fails, please check System Preferences -> Security & Privacy -> Privacy -> Bluetooth\n")
    
    try:
        print("Scanning for BLE devices...")
        devices = await BleakScanner.discover(timeout=10.0)
        
        if not devices:
            print("No BLE devices found!")
            return
        
        print("\nFound devices:")
        for d in devices:
            print(f"Name: {d.name or 'Unknown'}")
            print(f"Address: {d.address}")
            print(f"RSSI: {d.rssi}dBm")
            if d.metadata:
                print("Metadata:", d.metadata)
            print("-" * 50)
    
    except BleakError as e:
        print(f"Bluetooth error: {e}")
        print("Please ensure Bluetooth is enabled and permissions are granted.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        print("If this persists, try running the script with administrator privileges")

if __name__ == "__main__":
    try:
        asyncio.run(scan_devices())
    except KeyboardInterrupt:
        print("\nScan cancelled by user")
        sys.exit(0)
