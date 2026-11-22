# Akıllı Ev Otomasyon Sistemi

Tasarım Kalıpları dersi dönem projesi.
**Yazar:** Mehmet Dürmüş, Nişantaşı Üniversitesi, Bilgisayar Mühendisliği

Farklı üreticilerin (Luma/Zigbee, Nova/Wi-Fi) ışık ve termostat cihazlarını tek noktadan yöneten; sahne ve geri alma destekleyen; sensör olaylarına evin moduna göre tepki veren Python uygulaması. Harici bağımlılığı yoktur.

## Problem

- Üreticilerin SDK'ları birbirinden farklıdır (0-254 parlaklık + Fahrenheit ile 0-10 seviye + onda bir derece gibi).
- Kullanıcı "film" gibi sahnelerle birden çok cihazı birlikte ayarlamak ve yaptığını geri almak ister.
- Sensörler (hareket, sıcaklık) evin moduna göre farklı davranışı tetikler: evdeyken ışık yanar, geceleyin loş ışık yanar, uzaktayken alarm verilir.
- Işıklara günlükleme, parlaklık sınırı ve yeniden deneme gibi bağımsız davranışlar, istenen sırayla ve çalışma anında eklenebilmelidir.

## Kullanılan tasarım kalıpları

| Kalıp | Grup | Kod konumu | Çözdüğü problem |
|---|---|---|---|
| Adapter | Yapısal | [`akilli_ev/adapters.py`](akilli_ev/adapters.py) | Farklı üretici SDK'larını tek `Light`/`Thermostat` arayüzüne uyarlar |
| Decorator | Yapısal | [`akilli_ev/decorators.py`](akilli_ev/decorators.py) | Günlükleme, sınır, yeniden deneme: sınıf patlaması olmadan, çalışma anında birleştirilir |
| Facade | Yapısal | [`akilli_ev/facade.py`](akilli_ev/facade.py) | İstemciye tek ve sade giriş noktası |
| Abstract Factory | Yaratımsal | [`akilli_ev/factories.py`](akilli_ev/factories.py) | Üreticinin cihaz ailesini tutarlı üretir |
| Command | Davranışsal | [`akilli_ev/commands.py`](akilli_ev/commands.py) | Geri alma ve sahne (makro) |
| Mediator | Davranışsal | [`akilli_ev/mediator.py`](akilli_ev/mediator.py) | Sensörler ve cihazlar birbirini tanımaz |
| State | Davranışsal | [`akilli_ev/modes.py`](akilli_ev/modes.py) | Evde/Gece/Uzakta modlarına göre farklı tepki |

Her kalıbın rolleri, gerekçesi ve hangi sınıfın hangi rolü üstlendiği: **[docs/TASARIM_KALIPLARI.md](docs/TASARIM_KALIPLARI.md)**

## Hızlı başlangıç

```bash
git clone https://github.com/MehmetDrm0/akilli-ev-otomasyonu.git
cd akilli-ev-otomasyonu
python -m akilli_ev                                    # demo
python -m unittest discover -s tests -t . -v           # testler
```

Windows'ta `python` çalışmazsa `py`, macOS/Linux'ta `python3` kullanın. Ayrıntılar: [docs/KURULUM.md](docs/KURULUM.md)

## Dokümanlar

- [Kurulum](docs/KURULUM.md)
- [Test dokümanı](docs/TEST.md)
- [Tasarım kalıpları ve rol eşlemesi](docs/TASARIM_KALIPLARI.md)
- [Decorator soruları ve cevapları](docs/DECORATOR_SORULARI.md)

## Klasör yapısı

```
akilli_ev/          uygulama paketi (her kalıp ayrı modülde)
  devices.py        hedef arayüzler: Light, Thermostat
  adapters.py       Adapter
  factories.py      Abstract Factory
  decorators.py     Decorator
  commands.py       Command
  modes.py          State
  mediator.py       Mediator
  facade.py         Facade
  __main__.py       demo (python -m akilli_ev)
tests/              birim ve uçtan uca testler (58 test)
examples/           Decorator için ek örnekler ve kötü tasarım karşılaştırmaları
docs/               kurulum, test ve tasarım dokümanları
```

## Örnek kullanım

```python
from akilli_ev import (SmartHomeFacade, LumaFactory, NovaFactory,
                       RetryLight, BrightnessLimitedLight, LoggedLight)

home = SmartHomeFacade()
home.add_light("salon", LumaFactory())
home.add_light("mutfak", NovaFactory())
home.set_thermostat(LumaFactory())

home.wrap_light("salon", RetryLight, tries=3)             # Decorator, çalışma anında
home.wrap_light("salon", BrightnessLimitedLight, max_percent=60)
home.wrap_light("salon", LoggedLight)

home.run_scene("film")        # Command (makro)
home.undo()                   # geri al
home.set_mode("uzakta")       # State
home.motion("salon")          # Mediator + State: alarm
```
