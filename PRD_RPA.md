# Product Requirements Document (PRD): RecruitFlow-RPA
**Komponen: UiPath Robotic Automation Core (Unattended & API-First)**  
*Repositori: `iammadsfq/RecruitFlow-RPA`*

---

## 1. Peran & Visi Robot dalam Ekosistem RecruitFlow

Dalam arsitektur RecruitFlow, **UiPath bukan sekadar pelengkap (*not a mere supplement*)**, melainkan **mesin otomasi dan pemrosesan komputasi utama**. Robot beroperasi di background secara *unattended*, berinteraksi langsung dengan peladen web melalui REST API (API-First), dan mengeksekusi 4 proses bisnis inti:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   UiPath Orchestrator Cloud / Server                   │
│   (Assets, Queues: RF_CV_Processing, RF_Messaging, RF_Scheduling)      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        4 PROSES ROBOT UIPATH                           │
├────────────────────┬────────────────────┬──────────────────────────────┤
│ 1. RF_CV_Screening │ 2. RF_Messaging    │ 3. RF_Scheduling & Reminders │
│    (Parse & Skor)  │    (Kirim Pesan)   │    (Alokasi Slot Kalender)   │
├────────────────────┴────────────────────┴──────────────────────────────┤
│ 4. RF_Reporting (Laporan Harian Excel Modern & Housekeeping Berkas)    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP Request (Bearer Token)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    RecruitFlow-Platform (Core API)                     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Struktur Repositori & Modul Kerja

```
RecruitFlow-RPA/
├── .gitignore                    # Isolasi cache Studio, .local, temporary excel, dan credential
├── README.md                     # Panduan setup tim Windows & submisi lomba
├── PRD_RPA.md                    # Dokumen spesifikasi teknis RPA (file ini)
├── RF_Common/                    # Shared Library / Workflows bersama
│   ├── Api_Get.xaml              # HTTP GET terstandarisasi + Retry
│   ├── Api_Post.xaml             # HTTP POST terstandarisasi + Retry
│   ├── Log_To_Web.xaml           # Telemetri log real-time ke web
│   └── Mask_Pii.xaml             # Masking data pribadi untuk log Orchestrator
├── RF_CV_Screening/              # Proses 1: REFramework Ekstraksi & Skoring CV
│   ├── Main_Dispatcher.xaml
│   ├── Main_Performer.xaml
│   └── Workflows/
│       ├── Download_Cv.xaml
│       ├── Extract_Text.xaml     # Read PDF Text / Fallback OCR
│       ├── Parse_Fields.xaml     # Regex & normalisasi kata kunci
│       ├── Compare_Form_Cv.xaml  # Deteksi mismatch form vs CV
│       └── Calculate_Score.xaml  # Algoritma knock-out & bobot kriteria
├── RF_Messaging/                 # Proses 2: REFramework Pengiriman Email & Notifikasi
│   ├── Main_Dispatcher.xaml
│   ├── Main_Performer.xaml
│   └── Workflows/
│       ├── Render_Template.xaml  # Substitusi variabel {{variabel}}
│       └── Send_Email.xaml       # SMTP Mail / Mode Simulasi
├── RF_Scheduling/                # Proses 3: Penjadwalan & Pemantauan Waktu
│   ├── Main.xaml
│   └── Workflows/
│       ├── Assign_Slot.xaml      # Alokasi slot anti-bentrok (Retry 409)
│       ├── Handle_Reschedule.xaml
│       ├── Check_Expiry.xaml     # Pelepasan slot lewat batas konfirmasi
│       └── Dispatch_D1_Reminder.xaml
├── RF_Reporting/                 # Proses 4: Pembuatan Laporan Harian
│   ├── Main.xaml
│   └── Workflows/
│       ├── Generate_Excel.xaml   # Modern Excel formatting
│       └── Email_Report.xaml
├── Data/
│   ├── Input/                    # Folder data CV sintetis (.pdf)
│   └── Config/
│       └── Config.xlsx           # Konfigurasi teknis REFramework (tanpa rahasia)
└── Tests/                        # UiPath Test Cases (Data-driven testing)
```

---

## 3. Spesifikasi Rinci 4 Proses UiPath

### 3.1 Proses 1: `RF_CV_Screening`
- **Tujuan**: Mengotomatiskan pembacaan dokumen CV, memeriksa validitas form vs dokumen, dan menghitung kelayakan berdasarkan kriteria lowongan.
- **Pola**: Dispatcher (Time Trigger tiap 5 menit) – Performer (Queue Trigger `RF_CV_Processing`).
- **Langkah Dispatcher**:
  1. `GET /robot/applications?status=BARU&limit=50`.
  2. Untuk tiap lamaran: panggil `POST /robot/applications/{id}/claim` (idempotent, mengunci status menjadi `DIPROSES`).
  3. Kirim item antrean ke `RF_CV_Processing` dengan `Reference = application_id`.
- **Langkah Performer**:
  1. Ambil data kriteria dari backend via `GET /robot/jobs/{job_id}/criteria` (di-cache per ID lowongan).
  2. Unduh file CV ke folder sementara melalui `GET /robot/applications/{id}/cv`.
  3. **Ekstraksi Teks**:
     - Gunakan `UiPath.PDF.Activities.ReadPDFText`.
     - Evaluasi panjang teks hasil pembacaan. Apabila teks $< 200$ karakter (indikasi berkas scan gambar), aktifkan *fallback* `UiPath.PDF.Activities.ReadPDFWithOCR`.
     - Bila teks tetap tidak dapat dibaca, lempar `BusinessRuleException` ("Dokumen rusak / bukan CV yang dapat dibaca").
  4. **Parsing Entitas**:
     - Kontak: Regex telepon Indonesia (`08\d{8,11}`, `\+62\d{9,12}`) dan email.
     - Pendidikan: Pencarian jenjang (SMK, SMA, D3, S1, S2) dipetakan ke level numerik 1–4.
     - Pengalaman: Parsing rentang tanggal (contoh: "Jan 2021 – Feb 2023", "2020 - Sekarang"), hitung durasi bulan tanpa overlap, konversi ke akumulasi tahun.
     - Keahlian (*Skills*): Pencarian kata kunci skill wajib & tambahan berdasarkan sinonim dari data kriteria.
  5. **Verifikasi Silang Form vs CV**:
     - Bandingkan pengalaman form vs hitungan CV. Jika selisih $> 1$ tahun, beri penanda `mismatch_pengalaman`.
  6. **Kalkulasi Skor**:
     - Evaluasi syarat knock-out. Jika gagal, kelompok = `TIDAK_SESUAI`.
     - Hitung skor terbobot (0–100) sesuai formula bobot lowongan.
     - Tentukan kelompok (`SESUAI` jika skor $\ge 75$, `PERLU_DICEK` jika $55 \le \text{skor} < 75$ atau ada anomali, `TIDAK_SESUAI` jika skor $< 55$).
  7. **Pelaporan**:
     - Kirim data ekstraksi via `POST /robot/applications/{id}/extraction`.
     - Kirim nilai akhir via `POST /robot/applications/{id}/score` (status kandidat di backend bertransisi menjadi `MENUNGGU_KEPUTUSAN`).
     - Hapus berkas lokal di `%TEMP%`.

---

### 3.2 Proses 2: `RF_Messaging`
- **Tujuan**: Merender template dan mengirimkan komunikasi resmi (undangan / penolakan) hanya kepada kandidat yang telah disetujui HR.
- **Pola**: Dispatcher (Time Trigger tiap 5 menit) – Performer (Queue Trigger `RF_Messaging`).
- **Prinsip Kepatuhan BR-01**: Backend hanya merilis pesan dengan status `PENDING` jika kandidat berstatus `DISETUJUI_UNDANG` atau `DISETUJUI_TOLAK`. Robot tidak memiliki wewenang mengirim email di luar antrean yang disahkan backend.
- **Langkah Eksekusi**:
  1. Dispatcher membaca `GET /robot/messages?status=PENDING&limit=100`.
  2. Tambahkan ke Queue `RF_Messaging` dengan `Reference = message_id`.
  3. Performer memanggil `POST /robot/messages/{id}/claim`. Jika pesan sudah dalam proses/terkirim, selesaikan transaksi (idempotensi).
  4. Ambil detail template dan variabel melalui `GET /robot/messages/{id}`.
  5. Substitusi seluruh token variabel `{{...}}`. Jika regex mendeteksi masih ada token yang tersisa tanpa nilai, lempar `BusinessRuleException` ("Variabel template belum lengkap").
  6. Pengiriman:
     - Jika mode `RF_Email_Mode = SMTP`: Kirim via `UiPath.Mail.Activities.SendSMTPMailMessage`.
     - Jika mode `RF_Email_Mode = SIMULATION`: Catat pesan ke log telemetri tanpa transmisi nyata (aman untuk pengujian berulang).
     - Dalam lingkungan demo (`RF_Env = DEMO`), alihkan alamat penerima ke kotak surat tim.
  7. Laporkan status pengiriman via `POST /robot/messages/{id}/result` (`SENT` atau `FAILED`).

---

### 3.3 Proses 3: `RF_Scheduling`
- **Tujuan**: Mengelola alokasi slot kalender interview tanpa konflik, menampung permintaan *reschedule*, membebaskan slot kadaluwarsa, dan mengirimkan pengingat H-1.
- **Jadwal Eksekusi**:
  - Tiap 10 menit: Alokasi slot baru (`ASSIGN`), penanganan ganti jadwal, dan evaluasi jendela respons.
  - Harian pukul 09:00 WIB: Pemrosesan kandidat terkonfirmasi untuk pengingat H-1.
- **Penanganan Konflik Kalender (Concurrency)**:
  - Saat robot mengirim `POST /robot/interviews` untuk mengunci slot, jika backend merespons dengan HTTP `409 Conflict` (karena slot telah diambil oleh proses lain), robot secara otomatis mencoba slot kosong berikutnya hingga maksimal 5 kali percobaan sebelum mencatat notifikasi.

---

### 3.4 Proses 4: `RF_Reporting`
- **Tujuan**: Menyediakan pelaporan eksekutif berkala kepada manajemen HR mengenai performa corong rekrutmen.
- **Jadwal Eksekusi**: Harian pukul 17:00 WIB.
- **Langkah Eksekusi**:
  1. Ambil rekap agregat dari `GET /robot/reports/daily`.
  2. Buka template Excel menggunakan *Modern Excel Activities*.
  3. Isi lembar kerja:
     - Sheet 1: *Executive Summary* (Total Pelamar, Lolos Knock-out, Distribusi Kelompok, Rasio Kehadiran).
     - Sheet 2: *Breakdown Lowongan* (Status per posisi aktif).
     - Sheet 3: *Daftar Pengecualian Terbuka* (Kandidat yang membutuhkan intervensi HR di status `PERLU_DITINJAU`).
  4. Simpan berkas dengan format `RecruitFlow_Report_YYYYMMDD.xlsx`.
  5. Kirim berkas laporan sebagai lampiran email ke alamat pimpinan HR.
  6. Catat log pengiriman via `POST /robot/reports`.
  7. Lakukan *housekeeping*: bersihkan berkas sementara lokal yang berusia $> 7$ hari.

---

## 4. Konfigurasi Orchestrator (Assets & Queues)

Seluruh kredensial dan endpoint wajib dikonfigurasi melalui UiPath Orchestrator, **dilarang dicantumkan secara hardcoded di dalam repository**:

### Daftar Assets
| Nama Asset | Tipe | Keterangan |
|---|---|---|
| `RF_Api_BaseUrl` | Text | Alamat peladen backend (contoh: `https://api.recruitflow.example.com` atau `http://localhost:5000`) |
| `RF_Api_Token` | Credential / Secret | Token Bearer resmi otentikasi robot |
| `RF_Smtp_Credential` | Credential | Username dan Password peladen SMTP email |
| `RF_Smtp_Host` | Text | Host server SMTP (contoh: `smtp.gmail.com` atau `mail.example.com`) |
| `RF_Smtp_Port` | Integer | Port SMTP (contoh: `587` atau `465`) |
| `RF_Sender_Email` | Text | Alamat pengirim resmi email rekrutmen |
| `RF_Env` | Text | `DEMO` (hanya kirim ke kotak surat uji) atau `PROD` |
| `RF_Email_Mode` | Text | `SMTP` (kirim email nyata) atau `SIMULATION` (mock log) |
| `RF_Max_Emails_Per_Run` | Integer | Batas kuota pengiriman per transaksi batch (default: `50`) |
| `RF_Timezone` | Text | `Asia/Jakarta` |

### Daftar Queues
| Nama Queue | Tipe Reference | Auto-Retry |
|---|---|---|
| `RF_CV_Processing` | `application_id` (Unique Reference Aktif) | 3 kali |
| `RF_Messaging` | `message_id` (Unique Reference Aktif) | 3 kali |
| `RF_Scheduling` | `application_id:action:version` | 3 kali |

---

## 5. Strategi Penanganan Pengecualian (Exception Handling)

| Kondisi Masalah | Kategori Exception | Perilaku Robot | Status di Website |
|---|---|---|---|
| Format berkas PDF rusak / tidak bisa dibaca teksnya | `BusinessRuleException` | Jangan retry. Laporkan ke backend via `POST .../error`. | `PERLU_DITINJAU` (Butuh intervensi manual) |
| Kontak kosong / hasil ekstraksi meragukan | Aturan Bisnis Normal | Eksekusi terus berjalan, beri tanda override kelompok. | `MENUNGGU_KEPUTUSAN` (Masuk tab *Perlu Dicek*) |
| Backend mengalami gangguan jaringan / HTTP 500 | `SystemException` | Transaksi gagal, Orchestrator melakukan retry otomatis (maks 3x dengan jeda 5/15/30 detik). | Status tidak berubah sampai retry berhasil |
| Token robot salah / kedaluwarsa (HTTP 401/403) | `SystemException` Fatal | Hentikan eksekusi segera, catat log kesalahan kritikal. | Alarm di Dasbor Monitor Robot A11 |
| Alamat email kandidat invalid / bounce | `BusinessRuleException` | Jangan retry. Laporkan status pesan `FAILED`. | Pesan gagal tercatat di riwayat A6 |
| Variabel template tidak lengkap | `BusinessRuleException` | Batalkan pengiriman pesan spesifik tersebut. | Pesan berstatus `FAILED` di log |

---

## 6. Protokol Privasi & Keamanan Data (Kepatuhan Lomba)
1. **Pencegahan Kebocoran PII (BR-16)**: Activity `Mask_Pii.xaml` memastikan string yang dicatat ke log Orchestrator hanya memuat ID transaksi (misal: `app_01HX9`), bukan nama lengkap, email, atau nomor telepon kandidat.
2. **Kemandirian Lingkungan Windows**: Anggota tim yang mengembangkan di Windows wajib memastikan seluruh package NuGet (`UiPath.WebAPI.Activities`, `UiPath.PDF.Activities`, `UiPath.Excel.Activities`, `UiPath.Mail.Activities`) terdaftar di `project.json` dengan versi stabil.
