"""COMMAND (Davranışsal): cihaz eylemleri geri alınabilir nesneler olur."""
from abc import ABC, abstractmethod

from .devices import Light, Thermostat


# =====================================================================
# COMMAND - cihaz eylemleri nesne olur: geri alınabilir, sahnede birleştirilebilir
# =====================================================================
class Command(ABC):                         # Command
    @abstractmethod
    def execute(self) -> None: ...

    @abstractmethod
    def undo(self) -> None: ...

    @abstractmethod
    def describe(self) -> str: ...


class SetBrightnessCommand(Command):        # ConcreteCommand (Receiver: Light)
    def __init__(self, light: Light, percent: int):
        self._light = light
        self._new = percent
        self._old = 0

    def execute(self):
        self._old = self._light.get_brightness()
        self._light.set_brightness(self._new)

    def undo(self):
        self._light.set_brightness(self._old)

    def describe(self):
        return f"{self._light.name} ışığı %{self._new}"


class SetTemperatureCommand(Command):       # ConcreteCommand (Receiver: Thermostat)
    def __init__(self, thermostat: Thermostat, celsius: float):
        self._thermostat = thermostat
        self._new = celsius
        self._old = 0.0

    def execute(self):
        self._old = self._thermostat.get_target()
        self._thermostat.set_target(self._new)

    def undo(self):
        self._thermostat.set_target(self._old)

    def describe(self):
        return f"Termostat {self._new:.1f}°C"


class MacroCommand(Command):                # ConcreteCommand: sahne = komut dizisi
    def __init__(self, name: str, commands: list):
        self._name = name
        self._commands = commands

    def execute(self):
        for c in self._commands:
            c.execute()

    def undo(self):
        for c in reversed(self._commands):  # ters sırada geri al
            c.undo()

    def describe(self):
        return f"Sahne '{self._name}' ({len(self._commands)} adım)"


class CommandInvoker:                       # Invoker
    def __init__(self):
        self._history: list[Command] = []

    def run(self, cmd: Command) -> None:
        print(f"  [Komut] {cmd.describe()}")
        cmd.execute()
        self._history.append(cmd)

    def undo(self) -> None:
        if not self._history:
            raise ValueError("Geri alınacak komut yok")
        cmd = self._history.pop()
        print(f"  [Geri Al] {cmd.describe()}")
        cmd.undo()
