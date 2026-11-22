"""STATE (Davranışsal): evin modu olaylara verilen tepkiyi değiştirir."""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .mediator import HomeHub


# =====================================================================
# STATE - evin modu, olaylara verilen tepkiyi değiştirir
# =====================================================================
class ModeState(ABC):                       # State
    name = ""

    def on_enter(self, hub: "HomeHub") -> None:   # moda girişte yapılacak iş (isteğe bağlı)
        pass

    @abstractmethod
    def on_motion(self, hub: "HomeHub", room: str) -> None: ...

    @abstractmethod
    def on_temperature(self, hub: "HomeHub", celsius: float) -> None: ...


class AtHomeMode(ModeState):                # ConcreteState
    name = "Evde"

    def on_motion(self, hub, room):
        if hub.light(room).get_brightness() < 70:
            hub.set_light(room, 70)

    def on_temperature(self, hub, celsius):
        if celsius < 20:
            hub.set_temperature(22)


class NightMode(ModeState):                 # ConcreteState
    name = "Gece"

    def on_motion(self, hub, room):
        if hub.light(room).get_brightness() != 15:
            hub.set_light(room, 15)         # gece lambası

    def on_temperature(self, hub, celsius):
        if celsius < 19:
            hub.set_temperature(19)


class AwayMode(ModeState):                  # ConcreteState
    name = "Uzakta"

    def on_enter(self, hub):
        for room in hub.rooms():
            hub.set_light(room, 0)
        hub.set_temperature(17)             # tasarruf

    def on_motion(self, hub, room):
        hub.log(f"ALARM! Evde yokken {room} odasında hareket")
        for r in hub.rooms():
            hub.set_light(r, 100)           # caydırıcı

    def on_temperature(self, hub, celsius):
        if hub.thermostat.get_target() != 17:
            hub.set_temperature(17)


class ModeManager:                          # Context
    def __init__(self, hub: "HomeHub"):
        self._hub = hub
        self._states = {"evde": AtHomeMode(), "gece": NightMode(), "uzakta": AwayMode()}
        self._current: ModeState = self._states["evde"]

    def set_mode(self, key: str) -> None:
        if key not in self._states:
            raise ValueError(f"Bilinmeyen mod: {key}")
        self._current = self._states[key]
        self._hub.log(f"Mod: {self._current.name}")
        self._current.on_enter(self._hub)

    @property
    def current_name(self) -> str:
        return self._current.name

    def on_motion(self, room):
        self._current.on_motion(self._hub, room)

    def on_temperature(self, celsius):
        self._current.on_temperature(self._hub, celsius)
