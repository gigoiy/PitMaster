#!/usr/bin/env python3
# debug_spi.py

import spidev
import time
import RPi.GPIO as GPIO

class MAX6675Debug:
    def __init__(self, cs_pin):
        self.cs_pin = cs_pin
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 1000000
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.cs_pin, GPIO.OUT)
        GPIO.output(self.cs_pin, GPIO.HIGH)
    
    def read_raw(self):
        GPIO.output(self.cs_pin, GPIO.LOW)
        time.sleep(0.001)  # Wait for conversion
        
        # Read 2 bytes
        data = self.spi.readbytes(2)
        GPIO.output(self.cs_pin, GPIO.HIGH)
        
        return data

# Test all sensors
cs_pins = {
    "smoker_left": 8,
    "smoker_right": 7, 
    "meat_probe": 16
}

print("DEBUG: Reading raw SPI data from MAX6675 chips")
print("=" * 60)

for name, cs_pin in cs_pins.items():
    try:
        sensor = MAX6675Debug(cs_pin)
        raw_data = sensor.read_raw()
        value = (raw_data[0] << 8) | raw_data[1] if len(raw_data) >= 2 else 0
        
        print(f"{name:12} - CS Pin {cs_pin:2}:")
        print(f"  Raw bytes: {raw_data}")
        print(f"  Combined:  {bin(value):>16} (0x{value:04X})")
        print(f"  Bit 2 (Open): {'OPEN' if value & 0x04 else 'OK'}")
        print(f"  Temp bits: {(value >> 3) & 0xFFF}")
        print()
        
    except Exception as e:
        print(f"{name:12} - CS Pin {cs_pin:2}: ERROR - {e}")
        print()

GPIO.cleanup()