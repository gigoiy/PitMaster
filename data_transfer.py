# data_transfer.py
import time
import threading
from flask import Flask, jsonify, render_template
import board
import digitalio
import max6675


# Define GPIO pins for each K-type probe
cs_pins = {
    "smoker_left": board.D8,   # GPIO8 (pin 24)
    "smoker_right": board.D7,  # GPIO7 (pin 26)
    "meat_probe": board.D16    # GPIO16 (pin 36)
}

# SPI bus (shared)
spi = board.SPI()

# Define each MAX6675 and assigned each K-type probe to each MAX6675
sensors = {}
for name, cs_pin in cs_pins.items():
    cs = digitalio.DigitalInOut(cs_pin)
    sensors[name] = max6675.MAX6675(spi, cs)

# Define nested dictionaries to create a shared variable for temperature data
temperature_data = {
    "smoker_left": {"temp_c": 0.0, "temp_f": 0.0},
    "smoker_right": {"temp_c": 0.0, "temp_f": 0.0},
    "meat_probe": {"temp_c": 0.0, "temp_f": 0.0},
    "last_updated": ""
}

# Start of the Flask app
app = Flask(__name__)

# Background thread that updates temperatures every few seconds
def read_sensors_loop():
    while True:
        for name, sensor in sensors.items():
            try:
                temp_c = sensor.temperature
                temp_f = temp_c * 9/5 + 32
                temperature_data[name]["temp_c"] = round(temp_c, 2)
                temperature_data[name]["temp_f"] = round(temp_f, 2)
            except Exception as e:
                print(f"[WARN] Error reading {name}: {e}")
        temperature_data["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
        time.sleep(3)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    return jsonify(temperature_data)

if __name__ == '__main__':
    threading.Thread(target=read_sensors_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)

