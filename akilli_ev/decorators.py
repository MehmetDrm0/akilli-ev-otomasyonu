"""DECORATOR (Yapısal): ışığa çalışma anında bağımsız davranışlar eklenir."""
from .devices import Light


# =====================================================================
# DECORATOR - ışığa çalışma anında, bağımsız ve birleştirilebilir davranışlar ekler
# =====================================================================
class LightDecorator(Light):                # Decorator (Component'ten türer, bir Light sarmalar)
    def __init__(self, inner: Light):
        if not isinstance(inner, Light):    # uygunsuz sarmalamayı engeller (ör. Thermostat)
            raise TypeError(f"{type(inner).__name__} bir Light değil, sarmalanamaz")
        super().__init__(inner.name)
        self._inner = inner

    # ortak iletme burada; somut dekoratörler yalnızca kendi farkını yazar
    def set_brightness(self, percent):
        self._inner.set_brightness(percent)

    def get_brightness(self):
        return self._inner.get_brightness()
    # describe() soyut kalır: her somut dekoratör kendi açıklamasını ekler


class LoggedLight(LightDecorator):          # ConcreteDecorator
    def set_brightness(self, percent):
        print(f"  [Log] {self.name}: %{percent} isteniyor")
        self._inner.set_brightness(percent)

    def describe(self):
        return self._inner.describe() + ", Log"


class BrightnessLimitedLight(LightDecorator):   # ConcreteDecorator
    def __init__(self, inner: Light, max_percent: int = 60):
        super().__init__(inner)
        self._max = max_percent

    def set_brightness(self, percent):
        self._inner.set_brightness(min(percent, self._max))

    def describe(self):
        return self._inner.describe() + f", Max%{self._max}"


class RetryLight(LightDecorator):           # ConcreteDecorator
    def __init__(self, inner: Light, tries: int = 3):
        super().__init__(inner)
        self._tries = tries

    def set_brightness(self, percent):
        for attempt in range(1, self._tries + 1):
            try:
                self._inner.set_brightness(percent)
                return
            except ConnectionError:
                print(f"  [Retry] {self.name}: deneme {attempt}/{self._tries} başarısız")
                if attempt == self._tries:
                    raise

    def describe(self):
        return self._inner.describe() + f", Retry×{self._tries}"
