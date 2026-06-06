# Hamming-Error-Correcting-Code-Simulator

# ◈ Hamming Error-Correcting Code Simülatörü

> **BLM230 Bilgisayar Mimarisi — Dönem Projesi**  
> Bursa Teknik Üniversitesi

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-informational?style=flat-square)
![License](https://img.shields.io/badge/Lisans-MIT-green?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)

---

## 📌 Proje Hakkında

Bu proje, **Hamming Error-Correcting Code (ECC)** algoritmasını görsel ve etkileşimli biçimde simüle eden bir masaüstü uygulamasıdır. 8, 16 ve 32 bitlik veriler üzerinde Hamming kodlaması yapılabilmekte; belleğe yazma, yapay hata oluşturma, sendrom hesaplama ve otomatik hata düzeltme adımları adım adım gözlemlenebilmektedir.

---

## 🎬 Demo Videosu

> 📺 https://www.youtube.com/watch?v=e1_uvDAfYmw

---

## ✨ Özellikler

| Özellik | Açıklama |
|---|---|
| **8 / 16 / 32 bit destek** | Üç farklı veri uzunluğu için tam Hamming kodlaması |
| **Otomatik parity hesabı** | Her parity bitinin hangi bitleri kapsadığı gösterilir |
| **İnteraktif hata enjeksiyonu** | Herhangi bir bite tıklayarak yapay bit hatası oluşturulur |
| **Sendrom analizi** | Sendrom değeri hesaplanır ve hatalı bit konumu tespit edilir |
| **Otomatik düzeltme** | Hatalı bit otomatik olarak düzeltilir ve sonuç gösterilir |
| **Görsel bit grid** | Parity ve veri bitleri renk kodlarıyla ayrıştırılmış gösterim |

---

## 🧠 Teorik Arka Plan

### Hamming Kodu Nedir?

Hamming kodu, 1950'de Richard Hamming tarafından geliştirilen ve **tek bit hatalarını tespit edip düzelten (SEC — Single Error Correction)** bir hata düzeltme kodudur.

### Parity Bit Sayısının Hesaplanması

`m` bitlik bir veri için gereken `r` parity bit sayısı:

```
2^r ≥ m + r + 1
```

| Veri uzunluğu (m) | Parity bitleri (r) | Toplam uzunluk |
|:-:|:-:|:-:|
| 8 | 4 | 12 |
| 16 | 5 | 21 |
| 32 | 6 | 38 |

### Parity Bitlerinin Yerleşimi

Parity bitleri, 2'nin kuvveti olan konumlara yerleştirilir: **1, 2, 4, 8, 16, 32, ...**  
Veri bitleri geri kalan konumlara sırayla doldurulur.

```
Konum:   1   2   3   4   5   6   7   8   9  10  11  12
Tür:    [P1][P2][D1][P4][D2][D3][D4][P8][D5][D6][D7][D8]
```

### Sendrom ve Hata Tespiti

Bellekten okunan kelime üzerinde parity bitleri yeniden hesaplanır. XOR işlemleri sonucu elde edilen **sendrom değeri**, doğrudan hatalı bitin konum numarasını verir:

```
Sendrom = 0      → Hata yok
Sendrom = N (≠0) → N. bit hatalı
```

---


### Gereksinimler

- Python **3.10** veya üzeri
- `tkinter` (Python ile birlikte gelir — ayrıca kurulum gerekmez)


> **Not:** Linux sistemlerde tkinter ayrıca kurulması gerekebilir:
> ```bash
> sudo apt-get install python3-tk
> ```

---

## 🖥️ Kullanım Kılavuzu

Uygulama 4 adımdan oluşur:

```
[ 1 ] Veri Girişi  →  [ 2 ] Kodlama  →  [ 3 ] Hata Ekleme  →  [ 4 ] Sendrom & Düzeltme
```

**Adım 1 — Veri girişi:**  
Bit uzunluğunu seçin (8/16/32). İkili veriyi elle girin ya da "Rastgele" butonuyla otomatik oluşturun.

**Adım 2 — Kodlama:**  
"Kodla" butonuna basın. Parity bitleri hesaplanır, kod kelimesi ve her parity bitinin kapsam tablosu gösterilir.

**Adım 3 — Hata enjeksiyonu:**  
Görsel bit grid üzerinde herhangi bir bite tıklayarak bit değerini tersine çevirin (yapay hata). Aynı bite tekrar tıklayarak hatayı geri alabilirsiniz.

**Adım 4 — Tespit & Düzeltme:**  
"Sendromu Hesapla" butonuna basın. Sendrom bitleri, sendrom değeri, hatalı bit konumu ve düzeltilmiş kod kelimesi gösterilir.


---

## ⚙️ Teknik Detaylar

### Temel Fonksiyonlar

```python
calc_parity_bit_count(m: int) -> int
```
`2^r ≥ m + r + 1` koşulunu sağlayan minimum `r` değerini döner.

```python
encode(data_bits: list[int]) -> list[int]
```
Veri bitlerini alır, parity bitlerini hesaplar ve tam kod kelimesini 1-indexed liste olarak döner.

```python
calculate_syndrome(word: list[int]) -> tuple[int, list[dict]]
```
Kod kelimesinin sendromunu hesaplar. `(syndrome_value, parity_details)` döner.

```python
correct(word: list[int], syndrome: int) -> list[int]
```
Sendromun gösterdiği konumdaki biti tersine çevirerek düzeltilmiş kelimeyi döner.

---

## 📋 Örnek Çalışma

```
Veri (8 bit):     1 0 1 1 0 0 1 1
Parity bit sayısı: 4
Toplam uzunluk:   12 bit

Kod kelimesi:
  Konum:  1   2   3   4   5   6   7   8   9  10  11  12
  Değer: [1] [0] [1] [0] [1] [1] [1] [1] [0] [0] [1] [1]
         P1  P2  D   P4  D   D   D   P8  D   D   D   D

Hata: Bit 7 ters çevrildi (1 → 0)

Sendrom hesabı:
  P1 (bit 1): kapsar [1,3,5,7,9,11] → XOR = 1
  P2 (bit 2): kapsar [2,3,6,7,10,11] → XOR = 1
  P4 (bit 4): kapsar [4,5,6,7,12] → XOR = 1
  P8 (bit 8): kapsar [8,9,10,11,12] → XOR = 0

  Sendrom = 1 + 2 + 4 = 7  →  Bit 7 hatalı ✓
  Düzeltme: Bit 7 → 0 → 1
```

---

## 🔬 Algoritma Akışı

```
Veri Girişi (m bit)
       │
       ▼
Parity Bit Sayısı Hesapla (r)
       │
       ▼
Kod Kelimesini Oluştur (m + r bit)
  - 2^i konumlar → Parity
  - Diğer konumlar → Veri
       │
       ▼
Parity Değerlerini Hesapla (XOR)
       │
       ▼
    Belleğe Yaz
       │
    [Hata?]
       │
       ▼
 Bellekten Oku
       │
       ▼
Sendromu Hesapla (XOR)
       │
  ┌────┴────┐
  │         │
  ▼         ▼
S=0       S≠0
Hata Yok  Bit S'i Düzelt
```

---

## 📄 Lisans

Bu proje MIT lisansı ile dağıtılmaktadır.

---

*BLM230 Bilgisayar Mimarisi — Bursa Teknik Üniversitesi*
