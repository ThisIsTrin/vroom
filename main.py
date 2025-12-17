import time
from sensors.imu import IMU
from utils.influx import InfluxLogger
from utils.serial import SerialADC

imu = IMU()
influx = InfluxLogger(db="fsae_data")
adc = SerialADC(port="/dev/ttyACM0")

SAMPLE_RATE = 0.01   # 100 Hz
next_tick = time.perf_counter()

while True:
    # IMU
    imu_data = imu.read()
    influx.write("imu", imu_data)

    adc_data = adc.read()
    if adc_data:
        influx.write(
            "adc",
            {
                "tps": adc_data["A1"],
                # "tps": adc_data["A1"],
            }
        )


 # ---- Timing (stable 100 Hz) ----
    next_tick += SAMPLE_RATE
    sleep_time = next_tick - time.perf_counter()
    if sleep_time > 0:
        time.sleep(sleep_time)
