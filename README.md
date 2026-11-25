# RecruitFlow-RPA – UiPath Robotic Automation Core
**Automation Hackathon 2026 (#HumanInTheLead)**  
*Single Unified UiPath Studio Project (Windows · VB.NET)*

`RecruitFlow-RPA` adalah mesin otomasi robotik (**UiPath**) untuk mengotomatisasi proses rekrutmen *end-to-end* dengan prinsip **Human-in-the-Lead (BR-01)**: robot melakukan ekstraksi PDF CV, evaluasi syarat knock-out, kalkulasi skor terbobot, penjadwalan anti-bentrok, pengiriman pesan sah HR, dan pelaporan harian Excel, sementara keputusan kelulusan tetap dipegang penuh oleh manusia.

> **Catatan Keamanan (Kepatuhan Lomba):**  
> Repositori dan arsip ZIP ini **TIDAK menyertakan password, Bearer token, maupun API key**. Seluruh kredensial disuntikkan saat runtime melalui **UiPath Orchestrator Assets**, **Environment Variables** (`RF_API_TOKEN`, `RF_LLM_API_KEY`), atau **Input Arguments** (`in_ApiToken`, `in_LlmApiKey`).

---

## 1. Tools / Teknologi yang Dipakai

- **Platform RPA:** UiPath Studio Desktop `v24.10+` / `v26.10` (`targetFramework: Windows`, bahasa ekspresi `VisualBasic`).
- **Paket Aktivitas Resmi UiPath:**
  - `UiPath.System.Activities` (`24.10.0`)
  - `UiPath.WebAPI.Activities` (`1.20.1`) — Integrasi REST API (`HttpClient`) & `Newtonsoft.Json`
  - `UiPath.PDF.Activities` (`3.25.3`) — Ekstraksi teks PDF (`ReadPDFText`) & penjagaan ambang teks
  - `UiPath.Excel.Activities` (`2.23.4`) — Pembacaan `Config.xlsx` & penulisan laporan Excel (`WriteRange`)
  - `UiPath.Mail.Activities` (`1.23.1`) — Pengiriman email undangan/penolakan (`SendMail` SMTP / mode `SIMULATION`)
  - `UiPath.Testing.Activities` (`24.10.0`) — Test Case otomatis (`VerifyExpression`)
- **Integrasi Ekosistem RecruitFlow:**
  - Backend REST API (`RecruitFlow-Platform` / Node.js + SQLite)
  - Opsional LLM Cognitive Enrichment: Google Gemini API (dengan fallback otomatis ke parser Regex lokal jika tanpa API key / offline).

---

## 2. Kebutuhan Aplikasi & Koneksi

1. **Sistem Operasi:** Windows 10 / 11 (64-bit) dengan .NET 8 Runtime (terbawa oleh UiPath Studio/Robot).
2. **Aplikasi UiPath:**
   - **UiPath Studio Desktop** (untuk membuka, menganalisis, dan menjalankan test case) atau **UiPath Robot (`UiRobot.exe`)** (untuk eksekusi paket `.nupkg`).
3. **Koneksi & Layanan Pendukung:**
   - Akses jaringan ke peladen API **RecruitFlow-Platform** (default lokal: `http://localhost:5000`).
   - Akses internet ke feed resmi NuGet UiPath saat pertama kali melakukan *Restore Dependencies*.
   - *(Opsional)* Server SMTP (`smtp.gmail.com:587`) bila `RF_Email_Mode` diubah dari `SIMULATION` ke `SMTP`, serta API Key Google AI Studio bila `RF_Use_LLM` diaktifkan (`True`).

### Daftar Konfigurasi (`Data/Config/Config.xlsx` & Parameter Runtime)
| Kunci | Nilai Default | Keterangan |
|---|---|---|
| `RF_Api_BaseUrl` | `http://localhost:5000` | URL peladen API `RecruitFlow-Platform` |
| `RF_Api_Token` | *(kosong di file)* | Isi lewat Env Var `RF_API_TOKEN` / Argumen `in_ApiToken` / Orchestrator |
| `RF_Use_LLM` | `False` | `True` untuk ringkasan Gemini API, `False` untuk parser Regex lokal |
| `RF_Llm_ApiKey` | *(kosong di file)* | Isi lewat Env Var `RF_LLM_API_KEY` / Argumen `in_LlmApiKey` |
| `RF_Email_Mode` | `SIMULATION` | `SIMULATION` (aman untuk demo/uji) atau `SMTP` |
| `RF_Ocr_MinChars` | `200` | Ambang minimum karakter PDF sebelum ditandai rendah kepercayaan |
| `RF_Temp_Dir` | `Data\Temp` | Direktori sementara unduhan PDF |
| `RF_Report_Dir` | `Data\Output` | Direktori keluaran laporan Excel harian |

---

## 3. Struktur Proyek & Cara Menjalankan

### Struktur Folder Utama
```text
RecruitFlow-RPA/
├── project.json                        # Konfigurasi & 4 entry point UiPath
├── Main_CV_Screening.xaml              # Entry Point 1: Ekstraksi PDF, knock-out, & skoring
├── Main_Messaging.xaml                 # Entry Point 2: Pengiriman pesan sah HR (BR-01 & BR-09)
├── Main_Scheduling.xaml                # Entry Point 3: Alokasi slot anti-bentrok (retry 409) & H-1
├── Main_Reporting.xaml                 # Entry Point 4: Laporan harian Excel & housekeeping
├── Workflows/
│   ├── Common/                         # Load_Config, Api_Request, Log_To_Web, Mask_Pii
│   ├── CV_Screening/                   # Extract_Pdf_With_Ocr, Parse_Cv_Entities, Score_Candidate
│   └── Messaging/                      # Dispatch_Message
├── Data/
│   ├── Config/Config.xlsx              # Konfigurasi non-rahasia (tanpa token/password)
│   ├── Input/                          # 50 berkas PDF CV sintetis (cv_001.pdf - cv_050.pdf)
│   ├── Output/                         # Contoh keluaran laporan Excel harian
│   └── kunci_jawaban.csv               # Kunci jawaban evaluasi 50 CV uji
└── Tests/                              # Test_Score_Candidate.xaml & Test_Parse_Cv_Entities.xaml
```

### Cara Menjalankan via UiPath Studio Desktop
1. Pastikan backend `RecruitFlow-Platform` sudah berjalan di `http://localhost:5000` (dan database sudah di-seed).
2. Set Environment Variable Windows (atau isi saat run melalui parameter argumen):
   - `RF_API_TOKEN` = `<token bearer backend Anda>`
3. Buka `RecruitFlow-RPA/project.json` di **UiPath Studio**.
4. Jalankan salah satu *entry point*:
   - `Main_CV_Screening.xaml` (memproses pelamar berstatus `BARU`)
   - `Main_Messaging.xaml` (mengirim pesan `PENDING` yang sudah disetujui HR)
   - `Main_Scheduling.xaml` (mengalokasikan slot wawancara & cek pengingat H-1)
   - `Main_Reporting.xaml` (menghasilkan laporan Excel harian & membersihkan berkas `Data/Temp/` $> 7$ hari)
5. Untuk menjalankan unit test, buka panel **Test Explorer** lalu jalankan `Tests/Test_Score_Candidate.xaml` dan `Tests/Test_Parse_Cv_Entities.xaml`.

### Cara Menjalankan via `UiRobot.exe` (CLI)
```powershell
UiRobot.exe execute --file "<path>\RecruitFlow_RPA.1.0.3.nupkg" --entry "Main_CV_Screening.xaml" --input "{\"in_ApiBaseUrl\":\"http://localhost:5000\",\"in_ApiToken\":\"<TOKEN_ANDA>\"}"
```

---

## 4. Contoh Input & Output

### Contoh Input
1. **Berkas CV PDF Uji (`Data/Input/`):**
   - `cv_001.pdf` s/d `cv_015.pdf`: Kandidat ideal (`S1`, pengalaman $\ge 2$ tahun, menguasai React, Node.js, SQL, Git, Docker, TypeScript).
   - `cv_016.pdf` s/d `cv_025.pdf`: Skor menengah / batas ambang (`PERLU_DICEK`).
   - `cv_026.pdf` s/d `cv_035.pdf`: Melanggar syarat knock-out (`TIDAK_SESUAI`).
   - `cv_040.pdf`, `cv_041.pdf`, `cv_047.pdf`: Berkas scan/korup untuk uji pengecualian (`PERLU_DITINJAU`).
   - Referensi label uji: `Data/kunci_jawaban.csv`.
2. **Contoh Payload Antrean API (`GET /robot/applications?status=BARU`):**
```json
[
  {
    "id": "cv_001",
    "job_id": "job_software_eng_01",
    "name": "Siti Pratama",
    "city": "Jakarta Selatan",
    "education": "S1",
    "experience_years": 2.5,
    "status": "BARU"
  }
]
```

### Contoh Output
1. **Payload Skoring ke Backend (`POST /robot/applications/cv_001/score`):**
```json
{
  "score": 100.0,
  "group": "SESUAI",
  "breakdown": [
    { "label": "Pendidikan (10%)", "score": 10.0, "max": 10 },
    { "label": "Pengalaman (20%)", "score": 20.0, "max": 20 },
    { "label": "Skill Wajib (50%)", "score": 50.0, "max": 50 },
    { "label": "Skill Tambahan (20%)", "score": 20.0, "max": 20 }
  ],
  "summary": "Pendidikan S1 dengan pengalaman 2.5 tahun. Terpenuhi 4 skill wajib dan 2 skill tambahan.",
  "confidence": 0.96,
  "is_knockout_failed": false
}
```
2. **Hasil Uji Nyata 50 CV via `UiRobot.exe` (`Main_CV_Screening.xaml`):**
   - Total CV diproses: **50/50** dalam ~10 detik (`47 MENUNGGU_KEPUTUSAN`, `3 PERLU_DITINJAU`).
   - Distribusi kelompok: **21 `SESUAI`**, **15 `PERLU_DICEK`**, **11 `TIDAK_SESUAI`**, **3 `PERLU_DITINJAU`**.
   - Telemetri `POST /robot/logs` (dengan PII disamarkan oleh `Mask_Pii.xaml`) dan `POST /robot/heartbeat` tercatat di dashboard HR.
3. **Laporan Excel Harian (`Data/Output/RecruitFlow_Daily_Report_20261124.xlsx`):**
   - Sheet `Executive Summary` berisi tanggal laporan, total lamaran (`50`), dan jumlah wawancara terkonfirmasi.
