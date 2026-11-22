"""Hedef arayüzler: Adapter kalıbındaki Target rolü (Light, Thermostat)."""
from abc import ABC, abstractmethod


class Light(ABC):                           # Target
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def set_brightness(self, percent: int) -> None: ...

    @abstractmethod
    def get_brightness(self) -> int: ...

    @abstractmethod
    def describe(self) -> str: ...


class Thermostat(ABC):                      # Target
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def set_target(self, celsius: float) -> None: ...

    @abstractmethod
    def get_target(self) -> float: ...
