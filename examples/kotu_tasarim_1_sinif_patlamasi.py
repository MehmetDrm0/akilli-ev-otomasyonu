"""KÖTÜ TASARIM 1: Her davranış kombinasyonu için ayrı alt sınıf (sınıf patlaması).

Davranışlar: Log, Limit (en çok %60), Retry. Üretici: Luma, Nova.
Kitaptaki 'HouseBlendWithSoyAndMochaAndWhip' tasarımının karşılığı.
"""
from akilli_ev import LumaBridge, NovaCloud


class LumaLight:
    def __init__(self, name): self.name, self.bridge = name, LumaBridge()
    def set_brightness(self, p):
        self.bridge.send(f"luma-{self.name}", {"on": p > 0, "bri": round(p * 254 / 100)})


class LumaLightWithLimit(LumaLight):
    def set_brightness(self, p):
        super().set_brightness(min(p, 60))              # sınır kuralı burada kopyalandı


class LumaLightWithLog(LumaLight):
    def set_brightness(self, p):
        print(f"  [Log] {p}")
        super().set_brightness(p)


class LumaLightWithLogAndLimit(LumaLight):
    def set_brightness(self, p):
        print(f"  [Log] {p}")
        super().set_brightness(min(p, 80))              # kopyala-yapıştır: kural 80'e kaymış!


# ... LumaLightWithRetry, LumaLightWithLogAndRetry, LumaLightWithLimitAndRetry,
#     LumaLightWithLogAndLimitAndRetry, sonra aynıları Nova için de ... (toplam 16 sınıf)


def sinif_sayisi(uretici, davranis):
    return uretici * 2 ** davranis


if __name__ == "__main__":
    print("Üretici  Davranış  Gereken sınıf (üretici x 2^davranış)")
    for u, d in [(2, 3), (2, 4), (4, 6)]:
        print(f"{u:>7} {d:>9} {sinif_sayisi(u, d):>10}")
    print("Retry eklenince (2 üretici, 3 -> 4 davranış): 16 -> 32 sınıf\n")

    print("SORUN 1 - aynı 'limit' kuralı kopyalandığı için sınıflar birbiriyle çelişiyor:")
    print("  LumaLightWithLimit (%100 istendi):")
    LumaLightWithLimit("a").set_brightness(100)         # %60 sınırı -> bri 152
    print("  LumaLightWithLogAndLimit (%100 istendi):")
    LumaLightWithLogAndLimit("b").set_brightness(100)   # %80 sınırı (kaymış kopya) -> bri 203
    print("SORUN 2 - sınırı 60'tan 50'ye çekmek için limit içeren TÜM sınıflar elle düzeltilmeli.")
    print("SORUN 3 - çalışma anında davranış eklenemez: sınıf nesne yaratılırken seçilir.")
