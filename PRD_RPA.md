# Product Requirements Document (PRD): RecruitFlow-RPA
**Komponen: UiPath Robotic Automation Core (Single Unified REFramework Project)**  
*Repositori: `iammadsfq/RecruitFlow-RPA` | Versi: 3.2 (Production-Ready)*

Dokumen ini memetakan implementasi spesifik dari proyek robot UiPath Studio tunggal (*Single Unified Project*) yang beroperasi di latar belakang (*unattended background worker*) dalam arsitektur RecruitFlow.

---

## 1. Arsitektur Single Unified Project

Seluruh otomasi dibangun di atas kerangka kerja **Robotic Enterprise Framework (REFramework)** dengan 4 *entry point* independen:

```
RecruitFlow-RPA/
├── project.json                      # Konfigurasi dependensi UiPath Studio
├── .gitignore                        # Mengisolasi file cache, build, dan rahasia
├── README.md                         # Panduan operasional bagi tim Windows
├── PRD_RPA.md                        # Dokumen spesifikasi fungsional RPA (file ini)
│
├── Main_CV_Screening.xaml            # Entry Point 1: Ekstraksi & Skoring CV (Knockout + Bobot)
├── Main_Messaging.xaml               # Entry Point 2: Transmisi Pesan Sah HR (Multi-Channel)
├── Main_Scheduling.xaml              # Entry Point 3: Alokasi Slot, Overbooking 20%, Pengingat H-1
├── Main_Reporting.xaml               # Entry Point 4: Laporan Harian Modern Excel & Housekeeping
│
├── Framework/                        # REFramework State Machine (Init, Get, Process, SetStatus)
├── Workflows/
│   ├── Common/                       # Api_Request.xaml, Log_To_Web.xaml, Mask_Pii.xaml
│   ├── CV_Screening/                 # Download, OCR Fallback, Parsing, Summary, Skoring
│   ├── Messaging/                    # Fetch, Render Template, Dispatch Email/WA, Post Result
│   ├── Scheduling/                   # Slot Allocation (Retry 409), Overbooking, Reschedule, D-1
│   └── Reporting/                    # Build Excel Modern, Email Report, Housekeeping Temp
├── Data/
│   ├── Config/Config.xlsx            # Pengaturan teknis antrean & ambang OCR
│   ├── Input/                        # 50 berkas PDF CV sintetis data uji lomba
│   └── Temp/                         # Berkas unduhan CV runtime sementara
└── Tests/                            # Test cases otomatis (Test Explorer)
```

---

## 2. Rincian Modul & Fitur Kunci

### Modul 1: `Main_CV_Screening.xaml`
- **Tujuan**: Meniadakan beban pembacaan berkas manual oleh HR pada skenario rekrutmen massal.
- **Ekstraksi Teks**: Membaca dokumen PDF via `Read PDF Text`. Jika panjang karakter $< 200$, otomatis beralih ke `Read PDF With OCR` (UiPath Screen OCR).
- **Evaluasi 4 Syarat Knock-Out**:
  1. Domisili / Kesiapan penempatan luar kota.
  2. Tingkat pendidikan minimal (SMK/D3/S1).
  3. Pengalaman kerja minimal.
  4. Ketersediaan tanggal mulai bekerja.
  *Jika salah satu gagal, kandidat langsung masuk kelompok `TIDAK_SESUAI`.*
- **Kalkulasi Skor Terbobot (0–100)**:
  - Skill Wajib: 50%
  - Skill Tambahan: 20%
  - Pengalaman Kerja: 20%
  - Pendidikan Formal: 10%
- **Pemahaman Semantik Dokumen & Generator Narasi (LLM Cognitive Unit)**:
  Robot mengatasi bias format ATS non-standar (Canva, 2 kolom, portofolio grafis) dengan memanggil Google Gemini API (`gemini-3.8-flash` sebagai model produksi resmi aktif) via HTTP Request di UiPath. LLM mengembalikan *Structured JSON* berisi ringkasan naratif kontekstual 2–3 kalimat, verifikasi keahlian, dan estimasi pengalaman kerja. Jika terjadi kegagalan jaringan/kuota, robot otomatis *fallback* ke parser lokal dan menandai kandidat berstatus `PERLU_DICEK` (*zero crash*).
- **Generator Ringkasan Eksekutif (Candidate Summary)**:
  Narasi kualitatif hasil pemahaman LLM disimpan pada kolom `summary` untuk disajikan ke HR Dashboard, menghilangkan kebutuhan membaca berkas fisik secara manual.
- **Ambang Batas Kelompok**:
  - `SESUAI` ($\ge 75$)
  - `PERLU_DICEK` ($55 \le \text{skor} < 75$, atau ada selisih data form vs CV $> 1$ tahun, atau confidence ekstraksi $< 0.6$)
  - `TIDAK_SESUAI` ($< 55$ atau gagal syarat knock-out).

### Modul 2: `Main_Messaging.xaml`
- **Pematuhan Mutlak Human-in-the-Lead (BR-01)**:
  Robot hanya mengambil pesan `PENDING` yang telah disetujui HR via status `DISETUJUI_UNDANG` atau `DISETUJUI_TOLAK`.
- **Anti-Duplikasi (Idempotensi BR-09)**:
  Klaim pesan via `POST /robot/messages/{id}/claim` mengunci status menjadi `SENDING`.
- **Multi-Kanal**:
  - Email resmi via SMTP (mendukung flag `RF_Email_Mode = SIMULATION` saat testing beban dan pengalihan ke kotak surat tim pada `RF_Env = DEMO`).
  - Integrasi WhatsApp Webhook/Gateway untuk format teks padat ramah seluler.
- **Standar Pesan Lengkap & Hangat**:
  - Undangan: Memuat hari, tanggal, jam, link/lokasi, dokumen bawaan, kontak narahubung, dan tautan konfirmasi satu klik.
  - Penolakan: Bahasa apresiatif, kalimat motivasi, dan tautan pendaftaran Talent Pool.

### Modul 3: `Main_Scheduling.xaml`
- **Mitigasi Bentrok Slot (Concurrency Handling)**:
  Jika peladen mengembalikan status HTTP `409 Conflict` saat reservasi slot, robot secara otomatis mengambil slot kosong berikutnya dan mencoba ulang hingga 5 kali.
- **Faktor Overbooking Mass Hiring**:
  Menerapkan penambahan kuota slot cadangan (+20%) untuk mengantisipasi angka ketidakhadiran (*no-show*).
- **Jendela Respons 24 Jam**:
  Kandidat yang tidak merespons dalam 24 jam ditandai `TIDAK_MERESPONS`, dan slotnya dibebaskan secara otomatis untuk kandidat cadangan.
- **Pengingat H-1 (Harian 09:00 WIB)**:
  Mengirimkan notifikasi pengingat detail jadwal kepada seluruh kandidat `TERKONFIRMASI` untuk esok hari.

### Modul 4: `Main_Reporting.xaml`
- **Jadwal Eksekusi**: Harian pukul 17:00 WIB.
- **Laporan Excel Modern**: Mengisi template multi-sheet (`Executive Summary`, `Performa Lowongan`, `Daftar Pengecualian`) menggunakan *Modern Excel Activities*.
- **Housekeeping**: Menghapus berkas unduhan PDF di `Data/Temp/` yang berusia $> 7$ hari.

---

## 3. Konfigurasi Orchestrator (Aset & Antrean)

### Aset Wajib di Folder `RecruitFlow`
- `RF_Api_BaseUrl` (Text): Alamat URL backend Platform.
- `RF_Api_Token` (Credential): Token Bearer API robot.
- `RF_Smtp_Credential` (Credential): Kredensial akun email SMTP.
- `RF_Smtp_Host` (Text, default: `smtp.gmail.com`), `RF_Smtp_Port` (Integer, default: `587`).
- `RF_Sender_Email` (Text, contoh: `recruitment@example.com`).
- `RF_Env` (Text: `DEMO` / `PROD`).
- `RF_Email_Mode` (Text: `SMTP` / `SIMULATION`).
- `RF_Llm_ApiKey` (Credential: Password berisi Google AI Studio API Key).
- `RF_Llm_Model` (Text, default: `gemini-3.8-flash`, alternatif: `gemini-3.5-flash-lite`).
- `RF_Use_LLM` (Boolean, default: `True`).
- `RF_Max_Emails_Per_Run` (Integer: `50`).
- `RF_Timezone` (Text: `Asia/Jakarta`).

### Antrean Orchestrator
1. `RF_CV_Processing` (Unique Reference: `application_id`, Max Retry: 3).
2. `RF_Messaging` (Unique Reference: `message_id`, Max Retry: 3).
3. `RF_Scheduling` (Unique Reference: `application_id:action:version`, Max Retry: 3).

---

## 4. Matriks Exception Handling

- **`BusinessRuleException`**: Berkas CV rusak/tidak terbaca, email invalid, variabel template belum lengkap. *Tindakan: Jangan retry antrean, catat error ke backend via `POST .../error` (status ➔ `PERLU_DITINJAU`).*
- **`SystemException`**: Koneksi API backend terputus (HTTP 500/timeout). *Tindakan: Retry otomatis Orchestrator hingga 3 kali dengan interval jeda.*
- **Normal Flow**: Selisih pengalaman form vs CV, data kontak kosong di CV. *Tindakan: Lanjutkan kalkulasi, tandai override kelompok ke `PERLU_DICEK`.*
