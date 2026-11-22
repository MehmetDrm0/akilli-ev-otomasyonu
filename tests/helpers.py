"""Testlerde kullanılan sahte cihazlar ve sessiz test tabanı."""
import io
import unittest
from contextlib import redirect_stdout

from akilli_ev import Light, LumaBridge, NovaCloud, Thermostat


class QuietTestCase(unittest.TestCase):
    """print çıktısını yakalar: testler sessiz çalışır, çıktı self.output ile denetlenebilir."""

    def setUp(self):
        self._buf = io.StringIO()
        ctx = redirect_stdout(self._buf)
        ctx.__enter__()
        self.addCleanup(ctx.__exit__, None, None, None)

    @property
    def output(self) -> str:
        return self._buf.getvalue()

    def clear_output(self):
        self._buf.seek(0)
        self._buf.truncate(0)


class FakeLight(Light):
    def __init__(self, name="sahte", fail_times=0):
        super().__init__(name)
        self.percent = 0
        self.history = []
        self._fails = fail_times

    def set_brightness(self, percent):
        if self._fails > 0:
            self._fails -= 1
            raise ConnectionError("sahte zaman aşımı")
        self.history.append(percent)
        self.percent = percent

    def get_brightness(self):
        return self.percent

    def describe(self):
        return f"Sahte ışık ({self.name})"


class FakeThermostat(Thermostat):
    def __init__(self, name="ana", target=20.0):
        super().__init__(name)
        self.target = target
        self.history = []

    def set_target(self, celsius):
        self.history.append(celsius)
        self.target = celsius

    def get_target(self):
        return self.target


class RecordingBridge(LumaBridge):
    def __init__(self):
        super().__init__()
        self.sent = []

    def send(self, device_id, payload):
        self.sent.append((device_id, payload))


class RecordingCloud(NovaCloud):
    def __init__(self):
        self.calls = []

    def light_set(self, light_id, level):
        self.calls.append(("light_set", light_id, level))

    def climate_set(self, unit_id, deci_celsius):
        self.calls.append(("climate_set", unit_id, deci_celsius))
