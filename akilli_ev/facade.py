"""FACADE (Yapısal): istemci için tek ve basit giriş noktası."""
from .commands import (Command, CommandInvoker, MacroCommand,
                       SetBrightnessCommand, SetTemperatureCommand)
from .factories import DeviceFactory
from .mediator import HomeHub, MotionSensor, TemperatureSensor


# =====================================================================
# FACADE - istemci için tek ve basit giriş noktası
# =====================================================================
class SmartHomeFacade:                      # Facade
    def __init__(self):
        self._invoker = CommandInvoker()
        self._hub = HomeHub(self._invoker)
        self._motion: dict[str, MotionSensor] = {}
        self._temp_sensor = None
        self._scenes = {"film": self._movie_scene, "uyku": self._sleep_scene}

    # kurulum
    def add_light(self, room: str, factory: DeviceFactory):
        self._hub.register_light(room, factory.create_light(room))
        self._motion[room] = MotionSensor(room, self._hub)

    def set_thermostat(self, factory: DeviceFactory):
        self._hub.register_thermostat(factory.create_thermostat("ana"))
        self._temp_sensor = TemperatureSensor("salon", self._hub)

    def wrap_light(self, room: str, decorator_cls, **kwargs):
        """Odadaki ışığı çalışma anında bir dekoratörle sarmalar (yeni dekoratör için bu sınıf değişmez)."""
        self._hub.register_light(room, decorator_cls(self._hub.light(room), **kwargs))

    # kullanım
    def set_light(self, room: str, percent: int): self._hub.set_light(room, percent)
    def describe_light(self, room: str) -> str: return self._hub.light(room).describe()
    def brightness(self, room: str) -> int: return self._hub.light(room).get_brightness()
    def target_temperature(self) -> float: return self._hub.thermostat.get_target()
    def mode_name(self) -> str: return self._hub.modes.current_name
    def run_scene(self, name: str):
        if name not in self._scenes:
            raise ValueError(f"Bilinmeyen sahne: {name}")
        self._invoker.run(self._scenes[name]())   # her seferinde yeni komut nesnesi

    def set_mode(self, key: str): self._hub.modes.set_mode(key)
    def undo(self): self._invoker.undo()
    def motion(self, room: str): self._motion[room].trigger()
    def temperature(self, celsius: float): self._temp_sensor.report(celsius)

    # sahneler
    def _movie_scene(self) -> Command:
        h = self._hub
        cmds = [SetBrightnessCommand(h.light(r), 20 if r == "salon" else 0) for r in h.rooms()]
        cmds.append(SetTemperatureCommand(h.thermostat, 22))
        return MacroCommand("film", cmds)

    def _sleep_scene(self) -> Command:
        h = self._hub
        cmds = [SetBrightnessCommand(h.light(r), 0) for r in h.rooms()]
        cmds.append(SetTemperatureCommand(h.thermostat, 19))
        return MacroCommand("uyku", cmds)
