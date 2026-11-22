"""ABSTRACT FACTORY (Yaratımsal): üreticinin cihaz ailesi tutarlı biçimde üretilir."""
from abc import ABC, abstractmethod

from .adapters import (LumaBridge, LumaLightAdapter, LumaThermostatAdapter,
                       NovaCloud, NovaLightAdapter, NovaThermostatAdapter)
from .devices import Light, Thermostat


# =====================================================================
# ABSTRACT FACTORY - bir üreticinin cihaz ailesini tutarlı üretir
# =====================================================================
class DeviceFactory(ABC):                   # AbstractFactory
    @abstractmethod
    def create_light(self, name: str) -> Light: ...

    @abstractmethod
    def create_thermostat(self, name: str) -> Thermostat: ...


class LumaFactory(DeviceFactory):           # ConcreteFactory
    def __init__(self, fail_times: int = 0):
        self._bridge = LumaBridge(fail_times)   # ailedeki tüm cihazlar aynı bağlantıyı paylaşır

    def create_light(self, name):
        return LumaLightAdapter(name, self._bridge)

    def create_thermostat(self, name):
        return LumaThermostatAdapter(name, self._bridge)


class NovaFactory(DeviceFactory):           # ConcreteFactory
    def __init__(self):
        self._cloud = NovaCloud()

    def create_light(self, name):
        return NovaLightAdapter(name, self._cloud)

    def create_thermostat(self, name):
        return NovaThermostatAdapter(name, self._cloud)
