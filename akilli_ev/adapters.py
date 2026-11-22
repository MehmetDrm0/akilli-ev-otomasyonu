"""ADAPTER (Yapısal): üretici SDK'ları (Adaptee) sistemin Light/Thermostat arayüzüne uyarlanır."""
from .devices import Light, Thermostat


# ---- Adaptee'ler: üreticilerin değiştiremediğimiz, birbirinden farklı SDK'ları
class LumaBridge:                           # Adaptee 1 (Zigbee): sözlük yükü, 0-254, Fahrenheit
    def __init__(self, fail_times: int = 0):
        self._fails = fail_times            # test için: ilk N gönderim zaman aşımına uğrar

    def send(self, device_id: str, payload: dict) -> None:
        if self._fails > 0:
            self._fails -= 1
            raise ConnectionError("Zigbee zaman aşımı")
        print(f"  [Luma/Zigbee] {device_id} <- {payload}")


class NovaCloud:                            # Adaptee 2 (Wi-Fi): 0-10 seviye, onda bir derece
    def light_set(self, light_id: str, level: int) -> None:
        print(f"  [Nova/Wi-Fi] light_set({light_id}, level={level})")

    def climate_set(self, unit_id: str, deci_celsius: int) -> None:
        print(f"  [Nova/Wi-Fi] climate_set({unit_id}, {deci_celsius})")


# ---- Adapter'lar
class LumaLightAdapter(Light):              # Adapter
    def __init__(self, name: str, bridge: LumaBridge):
        super().__init__(name)
        self._bridge = bridge
        self._percent = 0

    def set_brightness(self, percent):
        self._bridge.send(f"luma-light-{self.name}",
                          {"on": percent > 0, "bri": round(percent * 254 / 100)})
        self._percent = percent             # durum yalnızca gönderim başarılıysa güncellenir

    def get_brightness(self):
        return self._percent

    def describe(self):
        return f"Luma ışık ({self.name})"


class LumaThermostatAdapter(Thermostat):    # Adapter
    def __init__(self, name: str, bridge: LumaBridge):
        super().__init__(name)
        self._bridge = bridge
        self._target = 20.0

    def set_target(self, celsius):
        self._target = celsius
        self._bridge.send(f"luma-thermo-{self.name}",
                          {"target_f": round(celsius * 9 / 5 + 32, 1)})

    def get_target(self):
        return self._target


class NovaLightAdapter(Light):              # Adapter
    def __init__(self, name: str, cloud: NovaCloud):
        super().__init__(name)
        self._cloud = cloud
        self._percent = 0

    def set_brightness(self, percent):
        self._cloud.light_set(f"nova-light-{self.name}", round(percent / 10))
        self._percent = percent

    def get_brightness(self):
        return self._percent

    def describe(self):
        return f"Nova ışık ({self.name})"


class NovaThermostatAdapter(Thermostat):    # Adapter
    def __init__(self, name: str, cloud: NovaCloud):
        super().__init__(name)
        self._cloud = cloud
        self._target = 20.0

    def set_target(self, celsius):
        self._target = celsius
        self._cloud.climate_set(f"nova-climate-{self.name}", int(celsius * 10))

    def get_target(self):
        return self._target
