# RecruitFlow-RPA – UiPath Intelligent Automation Engine
**Automation Hackathon 2026 (#HumanInTheLead)**  
*Repositori: `iammadsfq/RecruitFlow-RPA`*

Dokumen ini adalah panduan teknis bagi pengembang robot RPA (lingkungan Windows) dalam menyiapkan, menjalankan, menguji, dan mengemas proyek robot UiPath untuk kebutuhan kompetisi resmi.

---

## 🛠️ Persyaratan Lingkungan & Alat

1. **Sistem Operasi**: Windows 10/11 (64-bit).
2. **UiPath Studio**: Versi Desktop (Community atau Enterprise) v2022.10 atau yang lebih baru.
3. **Koneksi Orchestrator**: UiPath Automation Cloud (Personal / Community / Organization tenant).
4. **Dependensi NuGet Paket (Wajib diinstal via Manage Packages)**:
   - `UiPath.System.Activities`
   - `UiPath.WebAPI.Activities` (untuk HTTP Request & JSON Deserialization)
   - `UiPath.PDF.Activities` (untuk Read PDF Text & Read PDF With OCR)
   - `UiPath.Excel.Activities` (Modern Excel Activities)
   - `UiPath.Mail.Activities` (Send SMTP Mail Message)
   - `UiPath.Testing.Activities` (Unit Testing workflow)
   - `Newtonsoft.Json` (JObject & JArray manipulation)

---

## 📂 Struktur Modul

Proyek ini terbagi dalam 4 proses otomasi utama berbasis pola **Dispatcher–Performer** dan kerangka kerja **REFramework**:

```
RecruitFlow-RPA/
├── RF_Common/             # Library bersama: HTTP Client terstandar, logging web, PII masking
├── RF_CV_Screening/       # Proses 1: Unduh CV, OCR/Ekstraksi, Knockout, Skoring terbobot
├── RF_Messaging/          # Proses 2: Rendering template email & transmisi via SMTP/Simulasi
├── RF_Scheduling/         # Proses 3: Alokasi slot interview, resolusi bentrok 409, pengingat H-1
├── RF_Reporting/          # Proses 4: Pembuatan laporan eksekutif Excel harian & pengiriman email
├── Data/
│   ├── Config/            # Config.xlsx bawaan REFramework (hanya teknis, TANPA rahasia)
│   └── Input/             # 50 berkas PDF CV sintetis data uji
└── Tests/                 # Test cases otomatis (verifikasi logika skoring & ekstraksi)
```

> **Catatan Kepatuhan Arsitektur**:  
> Seluruh detail teknis alur kerja, penanganan *BusinessRuleException*, dan formula skoring dapat dipelajari di **[PRD_RPA.md](./PRD_RPA.md)**.

---

## ⚙️ Konfigurasi Orchestrator (Aset & Antrean)

Sebelum menjalankan robot, pastikan aset dan antrean berikut telah dibuat di UiPath Orchestrator pada folder `RecruitFlow`:

### 1. Assets
| Nama Asset | Tipe | Nilai Default / Contoh | Keterangan |
|---|---|---|---|
| `RF_Api_BaseUrl` | Text | `http://localhost:5000` atau URL server Platform | Alamat REST API backend |
| `RF_Api_Token` | Credential / Secret | Token Bearer resmi dari tim Web Lead | Token otentikasi API robot |
| `RF_Smtp_Credential` | Credential | User & App Password SMTP email | Kredensial pengirim email |
| `RF_Smtp_Host` | Text | `smtp.gmail.com` | Host peladen SMTP |
| `RF_Smtp_Port` | Integer | `587` | Port SMTP |
| `RF_Sender_Email` | Text | `recruitment@example.com` | Alamat pengirim resmi |
| `RF_Env` | Text | `DEMO` | `DEMO` (kirim ke kotak surat uji) / `PROD` |
| `RF_Email_Mode` | Text | `SIMULATION` / `SMTP` | `SIMULATION` (mock log tanpa email keluar) |
| `RF_Max_Emails_Per_Run` | Integer | `50` | Batas keamanan kuota email per run |
| `RF_Timezone` | Text | `Asia/Jakarta` | Zona waktu operasional (WIB) |

### 2. Queues
Pastikan opsi **Unique Reference** diaktifkan saat membuat antrean:
1. `RF_CV_Processing` (Reference: `application_id`, Max Retry: 3)
2. `RF_Messaging` (Reference: `message_id`, Max Retry: 3)
3. `RF_Scheduling` (Reference: `application_id:action:version`, Max Retry: 3)

---

## 🧪 Panduan Menjalankan Pengujian Lokal (Development)

1. **Jalankan Backend Terlebih Dahulu**: Pastikan `RecruitFlow-Platform` berjalan di localhost atau cloud, dan endpoint `/robot/heartbeat` merespons status 200 OK.
2. **Uji Ekstraksi & Skoring**:
   - Buka `RF_CV_Screening` di UiPath Studio.
   - Buka Test Explorer, jalankan unit test `Test_Score_Candidate.xaml` untuk memvalidasi formula knock-out dan bobot.
   - Jalankan `Main_Dispatcher.xaml` untuk mengambil berkas lamaran baru dari backend dan mengisinya ke antrean Orchestrator.
   - Jalankan `Main_Performer.xaml` untuk memproses dokumen CV dan memeriksa apakah status kandidat di web berubah menjadi `MENUNGGU_KEPUTUSAN`.
3. **Uji Komunikasi & Penjadwalan**:
   - Buka dashboard HR di web, setujui salah satu kandidat (`Setujui Undang` atau `Setujui Tolak`).
   - Jalankan `RF_Scheduling` untuk mengunci slot wawancara.
   - Jalankan `RF_Messaging` dengan `RF_Email_Mode = SIMULATION` untuk memeriksa apakah template ter-render dengan sempurna tanpa kebocoran token `{{...}}`.

---

## 📦 Panduan Pengemasan Berkas Submisi Lomba (Batas: 25 Nov 2026)

Berdasarkan ketentuan resmi kompetisi (Slide 10):
1. Format berkas pengumpulan source code robot adalah **ZIP (`.zip`)**.
2. **VERIFIKASI KEAMANAN SEBELUM COMPRESS**:
   - Pastikan **TIDAK ADA** password, API key, atau token rahasia yang tertulis di dalam file `.xaml` maupun `Config.xlsx`.
   - Pastikan folder `.local/`, `.screenshots/`, `bin/`, dan `obj/` telah dibersihkan atau diabaikan (sudah diatur otomatis oleh `.gitignore`).
3. Berkas ZIP wajib memuat:
   - Seluruh folder project UiPath lengkap yang dapat dibuka dan dijalankan.
   - File `README.md` ini sebagai panduan resmi reviewer.
   - Berkas contoh data uji di folder `Data/Input/`.
4. Beri nama berkas ZIP sesuai ketentuan panitia:  
   `NamaTim_RecruitFlow_SourceCode.zip`
