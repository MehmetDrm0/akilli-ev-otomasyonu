"""Decorator'ın gerçek dünyadan 3 somut kullanımı (hepsi çalışır)."""
import gzip
import io
from abc import ABC, abstractmethod


# ---------- 1) G/Ç akışları: tamponlama + sıkıştırma açma + metin çözme katmanları ----------
def ornek_io():
    ham = io.BytesIO(gzip.compress("merhaba\ndünya\n".encode("utf-8")))   # ham bayt
    tamponlu = io.BufferedReader(ham)                                       # + tamponlama
    acilmis = gzip.GzipFile(fileobj=tamponlu)                               # + gzip açma
    metin = io.TextIOWrapper(acilmis, encoding="utf-8")                     # + metin çözme
    print("  satırlar:", [satir.strip() for satir in metin])


# ---------- 2) Web ara katman yazılımı (WSGI): uygulama sarmalanır ----------
def uygulama(environ, start_response):
    start_response("200 OK", [("Content-Type", "text/plain")])
    return [b"merhaba"]


class GunlukMiddleware:
    def __init__(self, app): self.app = app
    def __call__(self, environ, start_response):
        print(f"  [Log] {environ['PATH_INFO']}")
        return self.app(environ, start_response)


class KimlikMiddleware:
    def __init__(self, app): self.app = app
    def __call__(self, environ, start_response):
        if "HTTP_AUTHORIZATION" not in environ:
            start_response("401 Unauthorized", [])
            return [b"giris gerekli"]
        return self.app(environ, start_response)


def ornek_middleware():
    app = GunlukMiddleware(KimlikMiddleware(uygulama))
    durum = []
    for env in ({"PATH_INFO": "/a"}, {"PATH_INFO": "/b", "HTTP_AUTHORIZATION": "x"}):
        yanit = app(env, lambda s, h: durum.append(s))
        print("  ", durum[-1], yanit)


# ---------- 3) Servis katmanında önbellek + yeniden deneme + günlükleme ----------
class HavaServisi(ABC):
    @abstractmethod
    def sicaklik(self, sehir: str) -> float: ...


class UzakHavaServisi(HavaServisi):         # gerçek iş: ağ çağrısı (burada ilk 2 çağrı zaman aşımı)
    def __init__(self): self.cagri = 0
    def sicaklik(self, sehir):
        self.cagri += 1
        if self.cagri <= 2:
            raise TimeoutError("ağ zaman aşımı")
        return 21.5


class OnbellekServisi(HavaServisi):
    def __init__(self, ic): self._ic, self._kayit = ic, {}
    def sicaklik(self, sehir):
        if sehir not in self._kayit:
            self._kayit[sehir] = self._ic.sicaklik(sehir)
        return self._kayit[sehir]


class YenidenDenemeServisi(HavaServisi):
    def __init__(self, ic, deneme=3): self._ic, self._deneme = ic, deneme
    def sicaklik(self, sehir):
        for i in range(self._deneme):
            try:
                return self._ic.sicaklik(sehir)
            except TimeoutError:
                if i == self._deneme - 1:
                    raise


class GunlukServisi(HavaServisi):
    def __init__(self, ad, ic): self._ad, self._ic = ad, ic
    def sicaklik(self, sehir):
        print(f"  [{self._ad}] sicaklik({sehir})")
        return self._ic.sicaklik(sehir)


def ornek_servis():
    print(" Sıra 1: Log(Retry(servis)) -> yeniden deneme dışarıdan görünmez, tek kayıt:")
    s1 = GunlukServisi("dış", YenidenDenemeServisi(UzakHavaServisi()))
    print("  sonuç:", s1.sicaklik("İstanbul"))
    print(" Sıra 2: Retry(Log(servis)) -> her deneme ayrı kaydedilir, 3 kayıt:")
    s2 = YenidenDenemeServisi(GunlukServisi("iç", UzakHavaServisi()))
    print("  sonuç:", s2.sicaklik("İstanbul"))
    print(" Önbellekli zincir: ikinci çağrı ağa gitmez:")
    uzak = UzakHavaServisi()
    s3 = OnbellekServisi(YenidenDenemeServisi(uzak))
    s3.sicaklik("İstanbul"); s3.sicaklik("İstanbul")
    print("  ağ çağrısı sayısı:", uzak.cagri, "(2 başarısız + 1 başarılı)")


if __name__ == "__main__":
    print("1) G/Ç akışları"); ornek_io()
    print("2) Middleware"); ornek_middleware()
    print("3) Servis dekoratörleri"); ornek_servis()
