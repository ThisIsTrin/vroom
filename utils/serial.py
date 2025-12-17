import serial
import os
import time


class SerialADC:
    def __init__(
        self,
        port="/dev/ttyACM0",
        baudrate=9600,
        timeout=0.05,
        expected_fields=5,
        reconnect_interval=1.0
    ):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.expected_fields = expected_fields
        self.reconnect_interval = reconnect_interval

        self.ser = None
        self.last_attempt = 0
        self.connected = False

    def _try_connect(self):
        now = time.monotonic()
        if now - self.last_attempt < self.reconnect_interval:
            return

        self.last_attempt = now

        if not os.path.exists(self.port):
            if self.connected:
                print("[SerialADC] Device disappeared")
                self.connected = False
            return

        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self.connected = True
            print(f"[SerialADC] Connected to {self.port}")
        except serial.SerialException:
            self.connected = False
            self.ser = None

    def read(self):
        # Attempt reconnect if needed
        if not self.ser or not self.ser.is_open:
            self._try_connect()
            return None

        try:
            line = self.ser.readline().decode("utf-8", errors="ignore").strip()
        except serial.SerialException:
            # USB unplugged or Arduino reset mid-read
            print("[SerialADC] Serial read error, reconnecting…")
            self._close()
            return None

        if not line:
            return None

        parts = line.split(",")

        if len(parts) != self.expected_fields:
            return None

        try:
            values = list(map(int, parts))
        except ValueError:
            return None

        return {
            "time_ms": values[0],
            "A0": values[1],
            "A1": values[2],
            "A2": values[3],
            "A3": values[4],
        }

    def _close(self):
        if self.ser:
            try:
                self.ser.close()
            except Exception:
                pass
        self.ser = None
        self.connected = False

    def close(self):
        self._close()
