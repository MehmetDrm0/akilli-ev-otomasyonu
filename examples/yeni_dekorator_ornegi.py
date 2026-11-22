"""Soru: "Yeni bir dekoratör (çeşni) eklersem kodda ne değişir?"

Cevap: yalnızca yeni bir sınıf yazılır. akilli_ev.py içindeki HİÇBİR sınıfa dokunulmaz
(Açık-Kapalı Prensibi). Bu dosya, akilli_ev.py'yi değiştirmeden yeni bir dekoratör ekler.
"""
from akilli_ev import SmartHomeFacade, NovaFactory, LightDecorator, LoggedLight


class MinBrightnessLight(LightDecorator):   # YENİ ConcreteDecorator (tek yeni sınıf)
    """LED'ler %10'un altında titrediği için sıfırdan büyük istekleri en az %10'a yükseltir."""
    def __init__(self, inner, minimum: int = 10):
        super().__init__(inner)
        self._min = minimum

    def set_brightness(self, percent):
        if 0 < percent < self._min:
            percent = self._min
        self._inner.set_brightness(percent)

    def describe(self):
        return self._inner.describe() + f", Min%{self._min}"


if __name__ == "__main__":
    home = SmartHomeFacade()
    home.add_light("yatak odası", NovaFactory())
    home.set_thermostat(NovaFactory())

    home.wrap_light("yatak odası", MinBrightnessLight, minimum=10)   # Facade değişmedi
    home.wrap_light("yatak odası", LoggedLight)                      # eskiyle birlikte çalışır
    print("Zincir:", home.describe_light("yatak odası"))
    home.set_light("yatak odası", 3)                                 # %3 istendi -> %10 uygulanır
    home.undo()
