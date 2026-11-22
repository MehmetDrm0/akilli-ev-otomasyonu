# Kurulum

## Gereksinimler

- Python **3.9 veya üzeri** (geliştirme ve testler Python 3.12 ile yapılmıştır)
- Harici paket gerekmez, `pip install` yapılmaz
- (İsteğe bağlı) Git

Sürümü kontrol edin:

```bash
python --version        # Windows'ta gerekirse: py --version
python3 --version       # macOS / Linux
```

## 1. Projeyi edinme

Git ile:

```bash
git clone https://github.com/MehmetDrm0/akilli-ev-otomasyonu.git
cd akilli-ev-otomasyonu
```

Git olmadan: GitHub sayfasında **Code → Download ZIP**, arşivi açın ve klasöre girin.

## 2. (İsteğe bağlı) Sanal ortam

Bağımlılık olmadığı için zorunlu değildir.

```bash
python -m venv .venv
# Windows (PowerShell):  .venv\Scripts\Activate.ps1
# macOS / Linux:         source .venv/bin/activate
```

## 3. Çalıştırma

Proje klasörünün kökünde (içinde `akilli_ev/` klasörünü gördüğünüz yerde) çalıştırın:

```bash
python -m akilli_ev
```

Beklenen çıktı bölümleri: `--- Film sahnesi`, `--- Geri al`, `--- Gece modu`, `--- Uzakta modu` (içinde `ALARM!` satırı), `--- Evde modu`, `--- Dekoratör zinciri`, `--- Sıra önemlidir`, `--- Uygunsuz sarmalama engellenir`.

Ek örnekler:

```bash
python -m examples.yeni_dekorator_ornegi
python -m examples.kotu_tasarim_1_sinif_patlamasi
python -m examples.kotu_tasarim_2_bayraklar
python -m examples.decorator_kullanim_ornekleri
```

## 4. Testleri çalıştırma

```bash
python -m unittest discover -s tests -t . -v
```

Ayrıntılar: [TEST.md](TEST.md)

## Sık karşılaşılan sorunlar

| Belirti | Çözüm |
|---|---|
| `No module named akilli_ev` | Komutu proje klasörünün **kökünde** çalıştırın (`cd akilli-ev-otomasyonu`) |
| `python` bulunamadı | Windows'ta `py`, macOS/Linux'ta `python3` kullanın |
| `Ran 0 tests` | Komutta `-t .` ve `-s tests` bölümlerinin olduğundan emin olun |
