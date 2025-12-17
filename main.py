import os
import time
from sensors.imu import IMU
from utils.influx import InfluxLogger

import serial

ser = None

if os.path.exists("/dev/ttyACM0"):
    ser = serial.Serial(
        port="/dev/ttyACM0",    # or /dev/ttyAMA0 or /dev/ttyS0 depending on your wiring
        baudrate=9600,
        timeout=1
    )


imu = IMU()
influx = InfluxLogger(db="fsae_data")

SAMPLE_RATE = 0.01   # 100 Hz

while True:
    imu_data = imu.read()

    influx.write("imu", imu_data)

    if ser:
        raw = ser.readline().decode("utf-8", errors="ignore").strip()

        try:
            tps_val = int(raw)
            influx.write("tps", {"volt": tps_val})
        except ValueError:
            print(f"Bad TPS data: {repr(raw)}")

    time.sleep(SAMPLE_RATE)
