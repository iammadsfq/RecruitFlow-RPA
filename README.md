# RecruitFlow-RPA – UiPath Robotic Automation Core
**Automation Hackathon 2026 (#HumanInTheLead)**  
*Repositori: `iammadsfq/RecruitFlow-RPA` | Model Arsitektur: Single Unified Project*

Dokumen ini adalah panduan teknis bagi pengembang robot RPA (lingkungan Windows) dalam menyiapkan, menjalankan, menguji, dan mengemas proyek robot UiPath Studio tunggal untuk kebutuhan kompetisi resmi.

---

## 🛠️ Persyaratan Lingkungan & Alat

1. **Sistem Operasi**: Windows 10/11 (64-bit).
2. **UiPath Studio**: Versi Desktop (Community atau Enterprise) v2022.10+.
3. **Koneksi Orchestrator**: UiPath Automation Cloud (Personal / Community / Organization tenant).
4. **Dependensi NuGet Paket (Manage Packages)**:
   - `UiPath.System.Activities`
   - `UiPath.WebAPI.Activities` (HTTP Request & JSON Deserialization)
   - `UiPath.PDF.Activities` (Read PDF Text & Read PDF With OCR)
   - `UiPath.Excel.Activities` (Modern Excel Activities)
   - `UiPath.Mail.Activities` (Send SMTP Mail Message)
   - `UiPath.Testing.Activities` (Unit Testing)
   - `Newtonsoft.Json` (Manipulasi JObject & JArray)

---

## 📂 Struktur Project Single Unified REFramework

Proyek ini menggunakan **1 Single Unified Project** dengan 4 *entry point* independen:

```
RecruitFlow-RPA/
├── project.json                      # Berkas proyek utama UiPath Studio
├── Main_CV_Screening.xaml            # Entry Point 1: Ekstraksi & Skoring CV
├── Main_Messaging.xaml               # Entry Point 2: Transmisi Pesan Multi-Kanal
├── Main_Scheduling.xaml              # Entry Point 3: Alokasi Slot & Pengingat H-1
├── Main_Reporting.xaml               # Entry Point 4: Laporan Eksekutif Excel
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

> **Dokumentasi Spesifikasi Lengkap**:  
> Seluruh formula skoring, aturan knock-out, dan matriks pengecualian terinci tersedia di **[PRD_RPA.md](./PRD_RPA.md)** dan file master di root **[PRD_RPA_DETAILED.md](../PRD_RPA_DETAILED.md)**.

---

## ⚙️ Konfigurasi Orchestrator (Aset & Antrean)

Buat aset dan antrean berikut di UiPath Orchestrator pada folder `RecruitFlow`:

### 1. Assets
| Nama Asset | Tipe | Contoh Nilai | Keterangan |
|---|---|---|---|
| `RF_Api_BaseUrl` | Text | `https://api.recruitflow.example.com` | URL peladen backend Platform |
| `RF_Api_Token` | Credential / Secret | Token Bearer resmi dari tim Web Lead | Token otentikasi API robot |
| `RF_Smtp_Credential` | Credential | User & App Password SMTP | Kredensial akun email pengirim |
| `RF_Smtp_Host` | Text | `smtp.gmail.com` | Host server SMTP |
| `RF_Smtp_Port` | Integer | `587` | Port SMTP (TLS) |
| `RF_Sender_Email` | Text | `recruitment@example.com` | Alamat pengirim resmi email |
| `RF_WhatsApp_ApiUrl`| Text | `https://api.whatsapp-gateway.mock` | Endpoint transmisi WhatsApp |
| `RF_Env` | Text | `DEMO` | `DEMO` (kotak surat uji) / `PROD` |
| `RF_Email_Mode` | Text | `SIMULATION` / `SMTP` | `SIMULATION` (mock log tanpa email keluar) |
| `RF_Llm_ApiKey` | Credential / Secret | `<Google AI Studio Key>` | Kredensial rahasia Gemini API |
| `RF_Llm_Model` | Text | `gemini-3.8-flash` | Model resmi aktif (opsi: `gemini-3.5-flash-lite`) |
| `RF_Use_LLM` | Boolean | `True` | Flag aktivasi pemahaman semantik LLM |
| `RF_Max_Emails_Per_Run` | Integer | `50` | Batas maksimum batch transmisi email |
| `RF_Timezone` | Text | `Asia/Jakarta` | Zona waktu operasional (WIB) |

### 2. Queues (Pastikan opsi **Unique Reference** diaktifkan)
1. `RF_CV_Processing` (Reference: `application_id`, Max Retry: 3)
2. `RF_Messaging` (Reference: `message_id`, Max Retry: 3)
3. `RF_Scheduling` (Reference: `application_id:action:version`, Max Retry: 3)

---

## 📊 Dataset Uji Sintetis & Kunci Jawaban (`Data/`)

Di dalam folder `Data/` tersedia 50 berkas PDF CV sintetis (`Data/Input/cv_001.pdf` s/d `cv_050.pdf`) beserta berkas label acuan **`Data/kunci_jawaban.csv`** untuk mengukur akurasi skoring robot:

| Kategori Skenario Uji | Jumlah | ID Berkas | Ekspektasi Kelompok | Target Skor |
|---|:---:|---|:---:|:---:|
| **Memenuhi Kriteria Ideal** | 15 | `cv_001` - `cv_015` | `SESUAI` | **100.0** |
| **Batas Bawah Skor (Skill Kurang)** | 10 | `cv_016` - `cv_025` | `PERLU_DICEK` | **67.5** |
| **Melanggar Syarat Mutlak Knock-Out** | 10 | `cv_026` - `cv_035` | `TIDAK_SESUAI` | **13.0 - 30.0** |
| **Layout 2 Kolom Canva Modern** | 4 | `cv_036` - `cv_039` | `SESUAI` | **90.0** |
| **Scan Raster Gambar (Uji OCR Fallback)** | 2 | `cv_040` - `cv_041` | `SESUAI` | **80.0** |
| **Bilingual / Full English CV** | 2 | `cv_042` - `cv_043` | `SESUAI` | **88.0** |
| **Kontak Tidak Dicantumkan (BR-03)** | 3 | `cv_044` - `cv_046` | `PERLU_DICEK` | **55.0** |
| **Berkas Korup & Non-CV (Exception)** | 2 | `cv_047` - `cv_048` | `PERLU_DITINJAU` | **0.0** |
| **Lamaran Duplikat (BR-04)** | 2 | `cv_049` - `cv_050` | `DUPLIKAT` | **75.0** |

---

## 🧪 Panduan Menjalankan & Menguji di Studio

1. Buka folder `RecruitFlow-RPA` di UiPath Studio Desktop.
2. Jalankan Test Case di panel **Test Explorer**:
   - `Test_Parse_Cv_Entities.xaml` (memvalidasi ekstraksi regex terhadap teks PDF).
   - `Test_Score_Candidate.xaml` (memvalidasi kelulusan knock-out dan bobot nilai).
3. Jalankan masing-masing *entry point* sesuai kebutuhan:
   - Untuk memproses antrean pelamar: jalankan `Main_CV_Screening.xaml`.
   - Untuk memproses pesan yang disahkan HR: jalankan `Main_Messaging.xaml`.
   - Untuk menguji alokasi slot wawancara: jalankan `Main_Scheduling.xaml`.
   - Untuk menghasilkan laporan Excel: jalankan `Main_Reporting.xaml`.

---

## 📦 Panduan Pengemasan Berkas Submisi Lomba (Batas: 25 Nov 2026)

Sesuai ketentuan resmi Slide 10:
1. Pastikan **TIDAK ADA** password, API key, atau token rahasia yang tertinggal di `.xaml` maupun `Config.xlsx`.
2. Format berkas pengumpulan adalah **ZIP (`.zip`)**.
3. Kompres folder `RecruitFlow-RPA` lengkap ke dalam berkas ZIP dengan penamaan resmi:  
   `NamaTim_RecruitFlow_SourceCode.zip`
