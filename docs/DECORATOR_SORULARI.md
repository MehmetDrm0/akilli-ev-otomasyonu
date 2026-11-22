# Decorator: Sık Sorulan Sorular ve Cevaplar (Akıllı Ev Projesi)

Bu doküman Decorator kalıbına ilişkin dört temel soruya projeden cevap verir. Her cevabın kodu çalıştırılıp doğrulanmıştır.

## 1) Decorator kodu doğru mu?

Dosya: `akilli_ev/decorators.py` (demo çıktısı: `python -m akilli_ev`).

| GoF rolü | Projedeki sınıf |
|---|---|
| Component | `Light` (soyut, `abc.ABC`) |
| ConcreteComponent | `LumaLightAdapter`, `NovaLightAdapter` |
| Decorator | `LightDecorator` (bir `Light` sarmalar, ortak iletmeyi yapar) |
| ConcreteDecorator | `LoggedLight`, `BrightnessLimitedLight`, `RetryLight` |

Önemli noktalar:
- `LightDecorator`, `Light`'tan yalnızca **tip uyumu** için türer. Davranışı, sarmaladığı `_inner` nesneye **devrederek** kazanır.
- Python'daki `@decorator` söz dizimi (fonksiyon dekoratörü) bu GoF kalıbıyla aynı şey değildir. Burada nesneler sarmalanır.
- Zincir çalışma anında kurulur: `Logged(Limited(Retry(Luma)))`. `describe()` zinciri gösterir: `Luma ışık (salon), Retry×3, Max%60, Log`.
- Demoda arızalı Zigbee bağlantısında `RetryLight` iki başarısız denemeden sonra komutu iletir (`bri: 152`, yani %60 sınırı uygulanmış).

## 2) Yeni bir dekoratör eklersem ne değişir?

Dosya: `examples/yeni_dekorator_ornegi.py` (`python -m examples.yeni_dekorator_ornegi`). Yalnızca **bir yeni sınıf** (`MinBrightnessLight`) yazılır.

| Kod parçası | Değişir mi? |
|---|---|
| `Light`, `LightDecorator` | Hayır |
| Adapter'lar (`Luma...`, `Nova...`) | Hayır |
| Mevcut dekoratörler | Hayır |
| `SmartHomeFacade` (`wrap_light` sınıfı parametre alır) | Hayır |
| Yeni dekoratör sınıfı | Eklenir |
| Kullanım yeri (`wrap_light(...)` çağrısı) | Yeni dekoratörü kullanmak için eklenir |

Bu Açık-Kapalı Prensibi'dir. Dürüst not: projede kalıbın dışında kalan iki yer tam açık-kapalı değildir. `ModeManager` içindeki mod sözlüğü (`modes.py`) ve `SmartHomeFacade` içindeki sahne sözlüğü (`facade.py`), yeni mod/sahne eklenirken bir satır güncellenmesini ister. Decorator bundan etkilenmez.

İsteğe bağlı iyileştirme: tekrar eden iletme mantığı `LightDecorator`'a taşınmıştır, somut dekoratörler yalnızca kendi farkını yazar (Starbuzz'daki `CondimentDecorator` refactor'unun karşılığı). Bedeli: kendi iletme mantığı farklı olan bir dekoratör `set_brightness`'ı yine geçersiz kılar.

## 3) İki kötü tasarım (ayrı dosyalarda)

| Kriter | `examples/kotu_tasarim_1_sinif_patlamasi.py` | `examples/kotu_tasarim_2_bayraklar.py` | Decorator |
|---|---|---|---|
| Sınıf sayısı | üretici × 2^davranış (2×2³=16, 4 davranışta 32) | davranış sayısından bağımsız ama tek şişkin sınıf | davranış sayısı + temel sınıflar |
| Yeni davranış | Sınıf sayısı katlanır | `Device` içinde 4 ayrı yer değişir | Tek yeni sınıf |
| Kural tutarlılığı | Kopyalanan kural kayar (demoda 60 yerine 80 çıkıyor) | Tek yerde, ama her davranışa bulaşır | Her kural tek sınıfta |
| Aynı davranışı iki kez | Ayrı sınıf gerekir | İkinci çağrı ilkini ezer | İç içe sarılır |
| Sıra seçimi | Sınıf adına gömülü | Sabit (hep önce log) | Sarmalama sırasıyla seçilir |
| Uygunsuz birleşim (termostata parlaklık sınırı) | Sınıf yazılmazsa olmaz | Hata vermeden kabul edilir | `TypeError` ile engellenir |
| Çalışma anında ekleme | Yok | Kısmen (bayrak) | Var (`wrap_light`) |

Not: Decorator'ın uygunsuz sarmalamayı engellemesi kendiliğinden olmaz. Bu projede `LightDecorator.__init__` içindeki `isinstance` denetimiyle sağlanır. Denetim yazılmazsa Python bunu yapmaz.

## 4) Avantajlar, dezavantajlar, ne zaman tercih edilir, 3 somut örnek

**Avantajlar**
- Açık-Kapalı Prensibi: yeni davranış mevcut koda dokunmadan eklenir.
- Çalışma zamanı esnekliği: davranışlar nesne kurulurken seçilir ve birleştirilir.
- Sınıf patlamasını önler (16 sınıf yerine 3 dekoratör + temel sınıflar).
- Tek Sorumluluk: her dekoratör tek bir iş yapar (günlükleme, sınır, yeniden deneme).
- Aynı dekoratör tekrar kullanılabilir, iki kez bile sarılabilir.
- İstemci kodu değişmez: dekoratörlü nesne aynı arayüzü sunar.

**Dezavantajlar**
- Çok sayıda küçük nesne: zincir uzadıkça hata ayıklama zorlaşır.
- **Sıra önemlidir:** `Log(Sınır(x))` istenen değeri (%100), `Sınır(Log(x))` uygulanan değeri (%60) kaydeder (demoda gösterilir).
- Nesne kimliği bozulur: `isinstance(dekoratörlü, LumaLightAdapter)` `False` döner. Somut tipe bakan kod bozulur.
- Zincirin ortasındaki bir dekoratörü çıkarmak zordur.
- Arayüz büyükse her dekoratör tüm metotları iletmek zorundadır (Python'da `__getattr__` ile kolaylaşır).
- Dıştaki referans yalnızca `Light` arayüzünü görür, iç dekoratörün özel metotlarına erişilemez.

**Ne zaman tercih edilir**
- Davranışlar bağımsızdır ve kombinasyon sayısı patlıyorsa.
- Davranış çalışma anında eklenip çıkarılacaksa.
- Kalıtım mümkün değilse (final sınıf, üçüncü taraf kütüphane).
- Kesişen ilgiler için: günlükleme, önbellek, yetki, yeniden deneme, ölçüm.

**Benzer kalıplarla farkı**
- Decorator: aynı arayüz, sarmalar, **sorumluluk ekler**.
- Proxy: aynı arayüz, sarmalar, **erişimi denetler** (tembel yükleme, yetki, uzak nesne).
- Adapter: **farklı** arayüzü uyarlar (projede `Luma...Adapter`).
- Strategy: nesnenin **içindeki** algoritmayı değiştirir (Decorator dış kabuğu, Strategy içi değiştirir).

**3 somut kullanım** (dosya: `examples/decorator_kullanim_ornekleri.py`, çalıştırılıp doğrulandı)
1. **G/Ç akışları:** `BytesIO` → `BufferedReader` (tamponlama) → `GzipFile` (açma) → `TextIOWrapper` (metin çözme). Java'daki `BufferedReader(InputStreamReader(GZIPInputStream(FileInputStream)))` zinciri aynı yapıdır.
2. **Web ara katman yazılımı (WSGI/Django/Express):** `GunlukMiddleware(KimlikMiddleware(uygulama))`. Her ara katman da bir uygulamadır, sarmaladığını çağırır. Kimlik denetimi yoksa istek `401` ile içeri girmeden durur.
3. **Servis katmanında önbellek + yeniden deneme + günlükleme:** Demoda `Log(Retry(servis))` tek kayıt, `Retry(Log(servis))` üç kayıt üretir (sıranın etkisi). Önbellekli zincirde ikinci çağrı ağa gitmez.
   - Projedeki karşılığı: arızalı Zigbee bağlantısında `RetryLight`.
