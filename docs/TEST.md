# Test Dokümanı

## Çalıştırma

Proje kökünde:

```bash
python -m unittest discover -s tests -t . -v
```

Beklenen sonuç: `Ran 58 tests ... OK`

Tek bir dosya veya test:

```bash
python -m unittest tests.test_decorators -v
python -m unittest tests.test_decorators.DecoratorTests.test_order_matters_for_what_gets_logged
```

Kapsam ölçümü (isteğe bağlı): `pip install coverage`, ardından `coverage run -m unittest discover -s tests -t .` ve `coverage report -m`.

## Test yaklaşımı

- Standart kütüphanenin `unittest` modülü kullanılır, harici paket gerekmez.
- Gerçek üretici SDK'ları yerine kayıt tutan sahte nesneler kullanılır (`tests/helpers.py`: `FakeLight`, `FakeThermostat`, `RecordingBridge`, `RecordingCloud`). Böylece testler ağa ve donanıma bağlı değildir.
- `print` çıktısı yakalanır (`QuietTestCase`): testler sessiz çalışır, günlük ve alarm mesajları ayrıca denetlenir.
- Her kalıbın kendi test dosyası vardır; testler kalıbın **neden var olduğunu** da doğrular (ör. aynı sahne iki kez çalıştırılıp geri alınabilir, yeni dekoratör mevcut sınıfları değiştirmeden eklenir).

## Test kapsamı (58 test)

| Dosya | Kalıp | Test sayısı | Neyi doğrular |
|---|---|---|---|
| `tests/test_adapters.py` | Adapter | 8 | Birim ve ölçek dönüşümleri (%→0-254, °C→°F, °C→onda bir derece), hatalı gönderimde durumun bozulmaması, arayüzlerin soyutluğu |
| `tests/test_factories.py` | Abstract Factory | 6 | Doğru ürün ailesi, ortak arayüzler, aile içi tek bağlantı, soyut fabrikanın örneklenememesi |
| `tests/test_decorators.py` | Decorator | 13 | Sınır, yeniden deneme (başarı/tükenme), günlük, zincir ve `describe()`, **sıranın etkisi**, uygunsuz sarmalamanın engellenmesi, yeni dekoratörün mevcut koda dokunmadan eklenmesi |
| `tests/test_commands.py` | Command | 6 | Çalıştır/geri al, makroyu ters sırada geri alma, boş geçmişte geri alma hatası |
| `tests/test_mediator_and_modes.py` | Mediator + State | 15 | Olay yönlendirme, bilinmeyen olay/mod hatası, Evde/Gece/Uzakta modlarının farklı tepkileri, moda giriş davranışı, alarm |
| `tests/test_facade.py` | Facade (uçtan uca) | 10 | Sahneler, geri alma, aynı sahneyi iki kez çalıştırıp geri alma, mod geçişi, çalışma anında dekoratör ekleme |

## El ile test senaryosu

1. `python -m akilli_ev` çalıştırın.
2. **Film sahnesi:** salon ışığı %20 (Luma yükünde `bri: 51`), diğer ışıklar kapalı, termostat 22 °C (`target_f: 71.6`).
3. **Geri al:** ters sırada eski değerler (termostat `68.0 °F` = 20 °C) geri yüklenir.
4. **Uzakta modu + hareket:** `ALARM!` satırı ve tüm ışıkların %100'e çıkması beklenir.
5. **Dekoratör zinciri:** iki başarısız `[Retry]` satırından sonra komut iletilir ve `bri: 152` (%60 sınırı uygulanmış) görülür.
6. **Sıra önemlidir:** `a` için günlükte `%100 isteniyor`, `b` için `%60 isteniyor` görülür.

## Sürekli entegrasyon

`.github/workflows/tests.yml` her `push` ve `pull request` işleminde testleri Python 3.9 ve 3.12 üzerinde otomatik çalıştırır. Sonuç GitHub'da **Actions** sekmesinde görülür.
