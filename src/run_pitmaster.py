#!/usr/bin/env python3
# run_pitmaster.py

import time
import threading
from flask import Flask, jsonify, render_template
import RPi.GPIO as GPIO
from max6675_simple import MAX6675

def create_app():
    # Define CS pins (BCM numbering)
    cs_pins = {
        "smoker_left": 8,    # GPIO8 (BCM)
        "smoker_right": 7,   # GPIO7 (BCM) 
        "meat_probe": 16     # GPIO16 (BCM)
    }

    # Create sensor objects
    sensors = {}
    for name, cs_pin in cs_pins.items():
        sensors[name] = MAX6675(cs_pin)

    temperature_data = {
        "smoker_left": {"temp_c": 0.0, "temp_f": 0.0},
        "smoker_right": {"temp_c": 0.0, "temp_f": 0.0},
        "meat_probe": {"temp_c": 0.0, "temp_f": 0.0},
        "last_updated": ""
    }

    app = Flask(__name__)

    def read_sensors_loop():
        while True:
            for name, sensor in sensors.items():
                try:
                    temp_c = sensor.read_temp_c()
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

    sensor_thread = threading.Thread(target=read_sensors_loop, daemon=True)
    sensor_thread.start()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8080)