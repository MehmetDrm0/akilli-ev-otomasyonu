"""MEDIATOR (Davranışsal): sensörler ve cihazlar arasındaki koordinasyon HomeHub'dadır."""
from abc import ABC, abstractmethod

from .commands import CommandInvoker, SetBrightnessCommand, SetTemperatureCommand
from .devices import Light, Thermostat
from .modes import ModeManager


# =====================================================================
# MEDIATOR - sensörler ve cihazlar birbirini tanımaz, tüm koordinasyon hub'da
# =====================================================================
class Mediator(ABC):                        # Mediator
    @abstractmethod
    def notify(self, sender: "Sensor", event: str, data) -> None: ...


class Sensor(ABC):                          # Colleague
    def __init__(self, room: str, mediator: Mediator):
        self.room = room
        self._mediator = mediator


class MotionSensor(Sensor):                 # ConcreteColleague
    def trigger(self):
        print(f"  [Sensör] {self.room}: hareket algılandı")
        self._mediator.notify(self, "motion", self.room)


class TemperatureSensor(Sensor):            # ConcreteColleague
    def report(self, celsius: float):
        print(f"  [Sensör] {self.room}: {celsius:.1f}°C ölçüldü")
        self._mediator.notify(self, "temperature", celsius)




# =====================================================================
# HomeHub: ConcreteMediator
# =====================================================================
class HomeHub(Mediator):                    # ConcreteMediator
    def __init__(self, invoker: CommandInvoker):
        self._invoker = invoker
        self._lights: dict[str, Light] = {}
        self._thermostat = None
        self._modes = ModeManager(self)

    # kayıt ve erişim
    def register_light(self, room: str, light: Light): self._lights[room] = light
    def register_thermostat(self, t: Thermostat): self._thermostat = t
    def light(self, room: str) -> Light: return self._lights[room]
    def rooms(self) -> list: return list(self._lights)

    @property
    def thermostat(self) -> Thermostat: return self._thermostat

    @property
    def modes(self) -> ModeManager: return self._modes

    # eylemler: her zaman Command olarak çalışır (geri alınabilir)
    def set_light(self, room: str, percent: int):
        self._invoker.run(SetBrightnessCommand(self._lights[room], percent))

    def set_temperature(self, celsius: float):
        self._invoker.run(SetTemperatureCommand(self._thermostat, celsius))

    def log(self, msg: str): print(f"  [Hub] {msg}")

    # Mediator arayüzü
    def notify(self, sender, event, data):
        if event == "motion":
            self._modes.on_motion(data)
        elif event == "temperature":
            self._modes.on_temperature(data)
        else:
            raise ValueError(f"Bilinmeyen olay: {event}")
