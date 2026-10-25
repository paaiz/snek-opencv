# It's a Snek! (OpenCV + Pygame)

Game **Snake** interaktif yang dikendalikan menggunakan **kamera (webcam)** melalui deteksi objek berwarna hijau secara _real-time_ menggunakan **OpenCV**, lengkap dengan visualisasi tahapan pemrosesan citra (`HSV Space`, `Binary Mask`, dan `Green Result`) serta dukungan kontrol _hybrid_ (Kamera & Keyboard).

---

## Fitur Utama

- **Kontrol Kamera (Computer Vision):** Menggerakkan ular dengan mengarahkan objek berwarna hijau ke tombol D-Pad virtual berbentuk `+` (dengan zona netral di tengah).
- **Visualisasi Proses OpenCV Real-Time:** Panel bawah kamera menampilkan 3 tahap pemrosesan warna hijau secara langsung:
  1. **HSV Space** — Konversi ruang warna BGR ke HSV.
  2. **Binary Mask** — Hasil _thresholding_ rentang warna hijau (`inRange`) + _morphological filtering_ (`erode` & `dilate`).
  3. **Green Result** — Hasil isolasi objek hijau (`bitwise_and`) beserta garis kontur terbesar dan titik _centroid_.
- **Sensor Stabilization & Smoothing:** Menggunakan filter luas kontur minimum (`MIN_CONTOUR_AREA`) dan _Exponential Moving Average_ untuk pergerakan titik sensor yang mulus dan bebas _jitter_.
- **Auto-Pause & Countdown:** Otomatis menghentikan permainan sementara ketika objek hijau keluar dari jangkauan kamera, disertai hitung mundur 5 detik saat sensor kembali terdeteksi.
- **Multi-Food Spawn:** Jumlah makanan di arena selalu muncul secara acak antara **2 hingga 5 buah** sekaligus.
- **Kontrol Hybrid:** Mendukung penuh penggunaan sensor kamera maupun tombol keyboard (`WASD` / _Arrow Keys_).

---

## Struktur Proyek

```text
snek-opencv/
├── main.py
├── assets/
│   └── fonts/
└── src/
    ├── app.py
    ├── config.py
    ├── snake.py
    ├── vision_tracker.py
    ├── camera_ui.py
    └── states/
        ├── base_state.py
        ├── menu_state.py
        ├── playing_state.py
        ├── paused_state.py
        └── game_over_state.py
```

---

## Persyaratan & Instalasi

Pastikan **Python 3.9+** dan webcam sudah terpasang di perangkat kamu.

1. **Clone repository:**

   ```bash
   git clone https://github.com/paaiz/snek-opencv.git
   cd snek-opencv
   ```

2. **Install dependencies:**

   ```bash
   pip install opencv-python numpy pygame-ce
   ```

   _(Catatan: Jika menggunakan `pygame` standar, ganti `pygame-ce` menjadi `pygame`)_

3. **Jalankan game:**
   ```bash
   python main.py
   ```

---

## Cara Bermain

### Menggunakan Kamera (Objek Hijau)

1. Siapkan benda berwarna hijau terang (tutup botol hijau, kertas/kartu hijau, atau benda hijau lainnya).
2. Pada layar **Main Menu**, arahkan benda hijau ke tombol **START** di layar kamera.
3. Saat bermain (**Playing**), arahkan benda hijau ke tombol **W** (Atas), **A** (Kiri), **S** (Bawah), atau **D** (Kanan) pada layar kamera. Gunakan kotak tengah sebagai area netral.
4. Jika benda hijau keluar dari kamera, game otomatis masuk ke mode **Paused** dan akan melanjutkan permainan setelah hitung mundur 5 detik ketika benda hijau kembali terdeteksi.

### Menggunakan Keyboard

- `W` / `↑` : Belok ke Atas
- `S` / `↓` : Belok ke Bawah
- `A` / `←` : Belok ke Kiri
- `D` / `→` : Belok ke Kanan
- `P` : Pause / Resume
- `SPACE` / `ENTER` : Mulai / Retry
- `M` / `ESC` : Kembali ke Main Menu saat Game Over

---

## Kustomisasi

Seluruh pengaturan sensitivitas warna hijau, kecepatan ular, dan jumlah makanan dapat diubah langsung melalui file [`src/config.py`](src/config.py):

- `HSV_GREEN_LOWER` & `HSV_GREEN_UPPER`: Rentang deteksi warna hijau pada ruang warna HSV.
- `MIN_CONTOUR_AREA`: Batas ukuran minimum objek hijau agar tidak menangkap _noise_ latar belakang.
- `SNAKE_MOVE_DELAY_MS`: Kecepatan gerak ular (dalam milidetik per langkah grid).
- `MIN_FOOD_COUNT` & `MAX_FOOD_COUNT`: Jumlah minimum dan maksimum makanan yang muncul di layar.
