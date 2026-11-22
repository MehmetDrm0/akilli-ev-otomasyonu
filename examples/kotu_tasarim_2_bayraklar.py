"""KÖTÜ TASARIM 2: Üst sınıfta var/yok bayrakları ve alan değerleri.

Kitaptaki Beverage içinde has_milk(), has_mocha() bayrakları tutan tasarımın karşılığı.
"""
from akilli_ev import NovaCloud


class Device:                               # tek şişkin üst sınıf
    def __init__(self, name):
        self.name = name
        self.log = False
        self.max_brightness = None          # sınır var/yok
        self.retry = 0
        # YENİ DAVRANIŞ => buraya yeni alan EKLENMELİ (Device değişir)

    # YENİ DAVRANIŞ => buraya yeni set_ metodu EKLENMELİ
    def enable_log(self): self.log = True
    def set_max(self, m): self.max_brightness = m      # ikinci çağrı ilkini ezer
    def set_retry(self, n): self.retry = n

    def _apply(self, p):                    # YENİ DAVRANIŞ => bu metot DEĞİŞMELİ
        if self.log:
            print(f"  [Log] {self.name}: %{p}")       # sıra sabit: hep önce log
        if self.max_brightness is not None:
            p = min(p, self.max_brightness)
        return p


class LightDevice(Device):
    def __init__(self, name):
        super().__init__(name); self.cloud = NovaCloud()
    def set_brightness(self, p):
        p = self._apply(p)
        self.cloud.light_set(self.name, round(p / 10))


class ThermostatDevice(Device):             # ışık bayraklarını da miras alır (kitaptaki 'buzlu çay + whip')
    def set_target(self, c): print(f"  [Termostat] {self.name} -> {c}°C")


if __name__ == "__main__":
    print("SORUN 1 - termostata anlamsız 'maksimum parlaklık' verilebiliyor, hata yok:")
    t = ThermostatDevice("ana"); t.set_max(60); print("  kabul edildi, max =", t.max_brightness)

    print("SORUN 2 - iki ayrı sınır uygulanamaz, ikincisi ilkini ezer (Decorator'da iç içe sarılır):")
    l = LightDevice("salon"); l.set_max(60); l.set_max(40); l.set_brightness(100)

    print("SORUN 3 - sıra seçilemez: 'sınırlanmış değeri logla' istenirse sınıf kodu değişmeli:")
    l2 = LightDevice("yatak"); l2.enable_log(); l2.set_max(60); l2.set_brightness(100)   # hep %100 loglar

    print("SORUN 4 - yeni davranış (ör. minimum parlaklık) için Device'ın alanı, set_ metodu ve")
    print("          _apply() içi değiştirilmeli: Açık-Kapalı Prensibi ihlali, 4 ayrı yer.")
    print("SORUN 5 - sınıf sayısı az (davranış + 1) ama her davranış her cihaza bulaşır.")
