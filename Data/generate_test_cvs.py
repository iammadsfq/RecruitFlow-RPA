#!/usr/bin/env python3
"""
RecruitFlow - Synthetic Test CV Dataset Generator (50 CVs + Kunci Jawaban)
Automation Hackathon 2026 (#HumanInTheLead)

Generates 50 synthetic candidate CVs across 9 test categories to validate:
1. Native text extraction & parsing
2. Fallback OCR on scanned/rasterized PDFs
3. Layout resilience (standard vs 2-column Canva-style)
4. Bilingual processing (ID & EN)
5. Knock-out evaluation (Pendidikan, Pengalaman, Domisili, Penempatan)
6. Weighted scoring accuracy (Target >= 90%)
7. Exception handling (corrupted files, missing fields)
"""

import os
import csv
import random
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = "/home/saf/saf/projects/RecruitFlow/RecruitFlow-RPA/Data/Input"
ANSWER_KEY_PATH = "/home/saf/saf/projects/RecruitFlow/RecruitFlow-RPA/Data/kunci_jawaban.csv"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Indonesian Synthetic Names & Data
FIRST_NAMES = ["Budi", "Siti", "Ahmad", "Dewi", "Rizky", "Putri", "Fajar", "Anisa", "Dimas", "Nurul", "Hendro", "Mega", "Bayu", "Lestari", "Agus", "Maya", "Eko", "Dian", "Ilham", "Tiara"]
LAST_NAMES = ["Santoso", "Pratama", "Hidayat", "Wijaya", "Kusuma", "Saputra", "Wulandari", "Setiawan", "Utami", "Firmansyah", "Nugroho", "Rahmawati", "Lestari", "Siregar", "Nasution"]
CITIES_JABODETABEK = ["Jakarta Selatan", "Jakarta Pusat", "Jakarta Barat", "Jakarta Timur", "Jakarta Utara", "Depok", "Bogor", "Tangerang", "Tangerang Selatan", "Bekasi"]
CITIES_OUTSIDE = ["Surabaya", "Bandung", "Semarang", "Yogyakarta", "Medan", "Malang", "Makassar"]

styles = getSampleStyleSheet()
title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor('#1E3A8A'))
h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=12, leading=15, textColor=colors.HexColor('#2563EB'), spaceBefore=8, spaceAfter=4)
body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#1F2937'))
body_bold = ParagraphStyle('BodyBold', parent=body_style, fontName='Helvetica-Bold')

def create_standard_cv(filepath, name, email, phone, city, edu, edu_major, exp_years, jobs, skills):
    """Generates standard clean 1-page PDF CV"""
    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    # Header
    story.append(Paragraph(f"<b>{name.upper()}</b>", title_style))
    contact_line = f"{email} | {phone} | {city}"
    story.append(Paragraph(contact_line, body_style))
    story.append(Spacer(1, 10))
    
    # Ringkasan Profil
    story.append(Paragraph("<b>RINGKASAN TENTANG SAYA</b>", h2_style))
    story.append(Paragraph(f"Profesional berdedikasi dengan latar belakang pendidikan {edu} {edu_major} dan total pengalaman {exp_years} tahun di bidang rekayasa perangkat lunak. Terampil dalam pengembangan sistem web dan integrasi API.", body_style))
    story.append(Spacer(1, 8))
    
    # Riwayat Kerja
    story.append(Paragraph("<b>PENGALAMAN KERJA</b>", h2_style))
    for job in jobs:
        story.append(Paragraph(f"<b>{job['title']}</b> – {job['company']}", body_bold))
        story.append(Paragraph(f"<i>{job['period']}</i>", body_style))
        story.append(Paragraph(job['desc'], body_style))
        story.append(Spacer(1, 4))
    story.append(Spacer(1, 6))
    
    # Pendidikan
    story.append(Paragraph("<b>PENDIDIKAN FORMAL</b>", h2_style))
    story.append(Paragraph(f"<b>{edu} {edu_major}</b>", body_bold))
    story.append(Paragraph(f"Universitas Terkemuka Indonesia (Lulus)", body_style))
    story.append(Spacer(1, 8))
    
    # Keahlian
    story.append(Paragraph("<b>KEAHLIAN & KOMPETENSI TEKNIS</b>", h2_style))
    story.append(Paragraph(", ".join(skills), body_style))
    
    doc.build(story)

def create_twocolumn_cv(filepath, name, email, phone, city, edu, edu_major, exp_years, jobs, skills):
    """Generates 2-column Canva-style modern layout PDF"""
    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    # Top Header Banner
    story.append(Paragraph(f"<b>{name.upper()}</b>", title_style))
    story.append(Paragraph(f"Portofolio Karir & Pengalaman Profesional | {city}", body_style))
    story.append(Spacer(1, 12))
    
    # Left column content
    left_content = [
        Paragraph("<b>KONTAK PRIBADI</b>", h2_style),
        Paragraph(f"Email: {email}", body_style),
        Paragraph(f"Telp/WA: {phone}", body_style),
        Paragraph(f"Domisili: {city}", body_style),
        Spacer(1, 10),
        Paragraph("<b>PENDIDIKAN</b>", h2_style),
        Paragraph(f"<b>{edu}</b>", body_bold),
        Paragraph(edu_major, body_style),
        Spacer(1, 10),
        Paragraph("<b>KOMPETENSI TEKNIS</b>", h2_style),
        Paragraph("<br/>".join([f"• {s}" for s in skills]), body_style)
    ]
    
    # Right column content
    right_content = [
        Paragraph("<b>PERJALANAN KARIR & PENGALAMAN</b>", h2_style),
        Paragraph(f"Akumulasi Pengalaman: {exp_years} Tahun", body_style),
        Spacer(1, 6)
    ]
    for job in jobs:
        right_content.append(Paragraph(f"<b>{job['title']}</b> - {job['company']}", body_bold))
        right_content.append(Paragraph(f"<i>{job['period']}</i>", body_style))
        right_content.append(Paragraph(job['desc'], body_style))
        right_content.append(Spacer(1, 6))
        
    table_data = [[left_content, right_content]]
    col_table = Table(table_data, colWidths=[200, 340])
    col_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LINEAFTER', (0,0), (0,-1), 1, colors.HexColor('#E5E7EB')),
        ('RIGHTPADDING', (0,0), (0,-1), 12),
        ('LEFTPADDING', (1,0), (1,-1), 12),
    ]))
    story.append(col_table)
    doc.build(story)

def create_scanned_image_cv(filepath, name, email, phone, city, edu, exp_years, skills):
    """Generates raster image-only PDF to test Fallback OCR engine"""
    img = Image.new('RGB', (1200, 1600), color=(250, 250, 250))
    draw = ImageDraw.Draw(img)
    
    # Header
    draw.text((80, 80), f"CURRICULUM VITAE - {name.upper()}", fill=(20, 20, 20))
    draw.text((80, 130), f"Email: {email} | Telepon: {phone} | Kota: {city}", fill=(60, 60, 60))
    draw.line([(80, 170), (1120, 170)], fill=(150, 150, 150), width=2)
    
    # Body
    draw.text((80, 210), "RINGKASAN EKSEKUTIF", fill=(20, 50, 150))
    draw.text((80, 250), f"Tenaga profesional lulusan {edu} dengan akumulasi pengalaman kerja {exp_years} tahun.", fill=(30, 30, 30))
    
    draw.text((80, 330), "RIWAYAT PENGALAMAN KERJA", fill=(20, 50, 150))
    draw.text((80, 370), f"Software Developer di PT Teknologi Nusantara Mandiri (Durasi: {exp_years} Tahun)", fill=(30, 30, 30))
    draw.text((80, 410), "Bertanggung jawab merancang antarmuka pengguna web dan implementasi database.", fill=(60, 60, 60))
    
    draw.text((80, 490), "PENDIDIKAN TERAKHIR", fill=(20, 50, 150))
    draw.text((80, 530), f"{edu} - Fakultas Ilmu Komputer", fill=(30, 30, 30))
    
    draw.text((80, 610), "KEAHLIAN TEKNIS", fill=(20, 50, 150))
    draw.text((80, 650), ", ".join(skills), fill=(30, 30, 30))
    
    img.save(filepath, "PDF", resolution=150.0)

def create_corrupted_file(filepath):
    """Generates corrupted binary file simulating unreadable PDF"""
    with open(filepath, "wb") as f:
        f.write(b"%PDF-1.4\nINVALID_CORRUPTED_STREAM_HEADER_BYTE_ERROR_XYZ\x00\xff\xfe")

def create_non_cv_document(filepath):
    """Generates non-CV PDF (e.g., Certificate of Participation)"""
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    story = [
        Spacer(1, 100),
        Paragraph("<font size=24><b>SERTIFIKAT KELULUSAN</b></font>", title_style),
        Spacer(1, 20),
        Paragraph("Diberikan kepada peserta atas keberhasilan menyelesaikan kursus Bahasa Inggris Tingkat Dasar.", body_style),
        Spacer(1, 10),
        Paragraph("Nomor Registrasi Sertifikat: CERT-2026-887192", body_style),
    ]
    doc.build(story)

# Main Generation Routine
cv_records = []

# Skenario 1: 15 CV Sesuai Ideal (Skor >= 75, Lolos Knockout)
for i in range(1, 16):
    cid = f"cv_{i:03d}"
    name = f"{FIRST_NAMES[i % len(FIRST_NAMES)]} {LAST_NAMES[i % len(LAST_NAMES)]}"
    email = f"{name.lower().replace(' ', '.')}@example.com"
    phone = f"0812{random.randint(10000000, 99999999)}"
    city = CITIES_JABODETABEK[i % len(CITIES_JABODETABEK)]
    edu = "S1"
    edu_major = "Teknik Informatika"
    exp = 2.0 + (i % 3) * 0.5  # 2.0 to 3.0 years
    jobs = [
        {"title": "Fullstack Web Developer", "company": "PT Digital Solusindo", "period": "Jan 2024 - Sekarang", "desc": "Membangun sistem web berskala besar menggunakan React, Node.js, dan database SQL."},
        {"title": "Junior Developer", "company": "CV Kreasi Mandiri", "period": "Jan 2023 - Des 2023", "desc": "Pengembangan fitur antarmuka web, Git version control, dan deployment container Docker."}
    ]
    skills = ["React", "Node.js", "SQL", "Git", "TypeScript", "Docker"]
    filepath = os.path.join(OUTPUT_DIR, f"{cid}.pdf")
    create_standard_cv(filepath, name, email, phone, city, edu, edu_major, exp, jobs, skills)
    cv_records.append({
        "id": cid, "name": name, "email": email, "phone": phone, "edu": edu, "exp": exp,
        "matched_skills": "React, Node.js, SQL, Git, TypeScript, Docker",
        "knockout": "LOLOS", "score": 95.0, "group": "SESUAI",
        "scenario": "Ideal / Memenuhi Seluruh Kriteria", "notes": "Lolos 4 knockout, menguasai seluruh skill wajib & tambahan."
    })

# Skenario 2: 10 CV Batas Bawah / Perlu Dicek (Skor 55-74)
for i in range(16, 26):
    cid = f"cv_{i:03d}"
    name = f"{FIRST_NAMES[i % len(FIRST_NAMES)]} {LAST_NAMES[(i+2) % len(LAST_NAMES)]}"
    email = f"{name.lower().replace(' ', '.')}@example.com"
    phone = f"0813{random.randint(10000000, 99999999)}"
    city = CITIES_JABODETABEK[i % len(CITIES_JABODETABEK)]
    edu = "S1"
    edu_major = "Sistem Informasi"
    exp = 1.0  # batas bawah
    jobs = [
        {"title": "Junior Programmer", "company": "PT Mitra Informatika", "period": "Jan 2025 - Sekarang", "desc": "Membantu pembuatan aplikasi web internal dengan React dan SQL."}
    ]
    skills = ["React", "SQL", "HTML/CSS"] # Kurang Node.js & Git
    filepath = os.path.join(OUTPUT_DIR, f"{cid}.pdf")
    create_standard_cv(filepath, name, email, phone, city, edu, edu_major, exp, jobs, skills)
    cv_records.append({
        "id": cid, "name": name, "email": email, "phone": phone, "edu": edu, "exp": exp,
        "matched_skills": "React, SQL",
        "knockout": "LOLOS", "score": 62.5, "group": "PERLU_DICEK",
        "scenario": "Batas Bawah Skor / Skill Kurang", "notes": "Hanya memenuhi 2 dari 4 skill wajib. Masuk tab Perlu Dicek."
    })

# Skenario 3: 10 CV Gagal Knockout (Tidak Sesuai)
# 4 Gagal Pendidikan (SMK/SMA), 3 Gagal Pengalaman (< 1 thn), 3 Gagal Domisili/Penempatan
for i in range(26, 36):
    cid = f"cv_{i:03d}"
    name = f"{FIRST_NAMES[i % len(FIRST_NAMES)]} {LAST_NAMES[(i+4) % len(LAST_NAMES)]}"
    email = f"{name.lower().replace(' ', '.')}@example.com"
    phone = f"0815{random.randint(10000000, 99999999)}"
    
    if i < 30: # Gagal Pendidikan
        city = "Jakarta Selatan"
        edu = "SMK"
        edu_major = "Rekayasa Perangkat Lunak"
        exp = 1.5
        knockout_reason = "GAGAL_PENDIDIKAN"
        notes = "Pendidikan SMK di bawah batas mutlak S1."
    elif i < 33: # Gagal Pengalaman
        city = "Depok"
        edu = "S1"
        edu_major = "Ilmu Komputer"
        exp = 0.3
        knockout_reason = "GAGAL_PENGALAMAN"
        notes = "Pengalaman 0.3 tahun di bawah syarat minimal 1.0 tahun."
    else: # Gagal Domisili
        city = "Surabaya"
        edu = "S1"
        edu_major = "Teknik Komputer"
        exp = 2.0
        knockout_reason = "GAGAL_DOMISILI"
        notes = "Domisili luar kota dan tidak bersedia relokasi."
        
    jobs = [{"title": "Web Staff", "company": "CV Usaha Mandiri", "period": "2024", "desc": "Desain antarmuka web dan HTML."}]
    skills = ["HTML", "CSS", "JavaScript"]
    filepath = os.path.join(OUTPUT_DIR, f"{cid}.pdf")
    create_standard_cv(filepath, name, email, phone, city, edu, edu_major, exp, jobs, skills)
    cv_records.append({
        "id": cid, "name": name, "email": email, "phone": phone, "edu": edu, "exp": exp,
        "matched_skills": "JavaScript",
        "knockout": knockout_reason, "score": 35.0, "group": "TIDAK_SESUAI",
        "scenario": "Melanggar Syarat Mutlak Knockout", "notes": notes
    })

# Skenario 4: 4 CV Format 2 Kolom Canva (Uji Ketahanan Tata Letak)
for i in range(36, 40):
    cid = f"cv_{i:03d}"
    name = f"CanvaLayout {FIRST_NAMES[i % len(FIRST_NAMES)]}"
    email = f"canva.{i}@example.com"
    phone = f"0817{random.randint(10000000, 99999999)}"
    city = "Tangerang"
    edu = "S1"
    edu_major = "Sistem Komputer"
    exp = 2.5
    jobs = [
        {"title": "Senior Frontend Developer", "company": "PT Desain Teknologi", "period": "2023 - 2026", "desc": "Pengembangan arsitektur React, Node.js, dan optimasi SQL query."}
    ]
    skills = ["React", "Node.js", "SQL", "Git", "TypeScript"]
    filepath = os.path.join(OUTPUT_DIR, f"{cid}.pdf")
    create_twocolumn_cv(filepath, name, email, phone, city, edu, edu_major, exp, jobs, skills)
    cv_records.append({
        "id": cid, "name": name, "email": email, "phone": phone, "edu": edu, "exp": exp,
        "matched_skills": "React, Node.js, SQL, Git, TypeScript",
        "knockout": "LOLOS", "score": 90.0, "group": "SESUAI",
        "scenario": "Tata Letak Modern / 2 Kolom Canva", "notes": "Uji LLM/Parser membaca format 2 kolom secara kontekstual."
    })

# Skenario 5: 2 CV Hasil Scan Gambar (Uji Fallback OCR)
for i in range(40, 42):
    cid = f"cv_{i:03d}"
    name = f"ScannedCandidate {i}"
    email = f"scanned.{i}@example.com"
    phone = f"0818{random.randint(10000000, 99999999)}"
    city = "Jakarta Pusat"
    edu = "S1"
    exp = 2.0
    skills = ["React", "Node.js", "SQL", "Git"]
    filepath = os.path.join(OUTPUT_DIR, f"{cid}.pdf")
    create_scanned_image_cv(filepath, name, email, phone, city, edu, exp, skills)
    cv_records.append({
        "id": cid, "name": name, "email": email, "phone": phone, "edu": edu, "exp": exp,
        "matched_skills": "React, Node.js, SQL, Git",
        "knockout": "LOLOS", "score": 85.0, "group": "SESUAI",
        "scenario": "Raster Scan Image (Fallback OCR)", "notes": "Teks mentah kosong, memicu UiPath Read PDF With OCR."
    })

# Skenario 6: 2 CV Bahasa Inggris (Uji Kamus Bilingual)
for i in range(42, 44):
    cid = f"cv_{i:03d}"
    name = f"Alex Smith {i}"
    email = f"alex.smith{i}@example.com"
    phone = f"+62819{random.randint(10000000, 99999999)}"
    city = "Jakarta Selatan"
    edu = "Bachelor Degree"
    edu_major = "Computer Science"
    exp = 2.0
    jobs = [{"title": "Software Engineer", "company": "Global Tech Corp", "period": "2024 - Present", "desc": "Implemented scalable web interfaces with React, Node.js backend, and relational SQL."}]
    skills = ["ReactJS", "NodeJS", "PostgreSQL", "Git Version Control"]
    filepath = os.path.join(OUTPUT_DIR, f"{cid}.pdf")
    create_standard_cv(filepath, name, email, phone, city, edu, edu_major, exp, jobs, skills)
    cv_records.append({
        "id": cid, "name": name, "email": email, "phone": phone, "edu": "S1", "exp": exp,
        "matched_skills": "React, Node.js, SQL, Git",
        "knockout": "LOLOS", "score": 88.0, "group": "SESUAI",
        "scenario": "Bilingual / Full English CV", "notes": "Uji sinonim: Bachelor Degree=S1, PostgreSQL=SQL, NodeJS=Node.js."
    })

# Skenario 7: 3 CV Data Kontak Kosong (Uji Override Perlu Dicek)
for i in range(44, 47):
    cid = f"cv_{i:03d}"
    name = f"TanpaKontak {i}"
    email = ""
    phone = ""
    city = "Bekasi"
    edu = "S1"
    edu_major = "Teknik Informatika"
    exp = 2.0
    jobs = [{"title": "Web Programmer", "company": "PT Usaha Jaya", "period": "2023 - 2025", "desc": "Mengerjakan modul React dan database SQL."}]
    skills = ["React", "SQL"]
    filepath = os.path.join(OUTPUT_DIR, f"{cid}.pdf")
    create_standard_cv(filepath, name, "[EMAIL TIDAK DICANTUMKAN]", "[TELEPON KOSONG]", city, edu, edu_major, exp, jobs, skills)
    cv_records.append({
        "id": cid, "name": name, "email": "KOSONG", "phone": "KOSONG", "edu": edu, "exp": exp,
        "matched_skills": "React, SQL",
        "knockout": "LOLOS", "score": 58.0, "group": "PERLU_DICEK",
        "scenario": "Data Kontak Kosong", "notes": "Kontak kosong di CV, memicu aturan BR-03 (override ke Perlu Dicek)."
    })

# Skenario 8: 2 Berkas Pengecualian (1 Korup, 1 Non-CV)
cid = "cv_047"
filepath = os.path.join(OUTPUT_DIR, f"{cid}.pdf")
create_corrupted_file(filepath)
cv_records.append({
    "id": cid, "name": "KORUP_FILE", "email": "N/A", "phone": "N/A", "edu": "N/A", "exp": 0.0,
    "matched_skills": "None", "knockout": "ERROR", "score": 0.0, "group": "PERLU_DITINJAU",
    "scenario": "Berkas Korup / Rusak", "notes": "Memicu BusinessRuleException, status web bertransisi ke PERLU_DITINJAU."
})

cid = "cv_048"
filepath = os.path.join(OUTPUT_DIR, f"{cid}.pdf")
create_non_cv_document(filepath)
cv_records.append({
    "id": cid, "name": "BUKAN_CV", "email": "N/A", "phone": "N/A", "edu": "N/A", "exp": 0.0,
    "matched_skills": "None", "knockout": "ERROR", "score": 0.0, "group": "PERLU_DITINJAU",
    "scenario": "Bukan Berkas CV (Sertifikat)", "notes": "Teks tidak memuat struktur CV, memicu PERLU_DITINJAU."
})

# Skenario 9: 2 CV Duplikasi (Uji Filter Integritas BR-04)
for i in range(49, 51):
    cid = f"cv_{i:03d}"
    name = "Budi Santoso Duplikat"
    email = "budi.santoso@example.com" # sama dengan cv_001
    phone = "081299990001"
    city = "Jakarta Selatan"
    edu = "S1"
    edu_major = "Teknik Informatika"
    exp = 2.0
    jobs = [{"title": "Web Dev", "company": "PT Digital", "period": "2024", "desc": "React dan SQL."}]
    skills = ["React", "SQL"]
    filepath = os.path.join(OUTPUT_DIR, f"{cid}.pdf")
    create_standard_cv(filepath, name, email, phone, city, edu, edu_major, exp, jobs, skills)
    cv_records.append({
        "id": cid, "name": name, "email": email, "phone": phone, "edu": edu, "exp": exp,
        "matched_skills": "React, SQL",
        "knockout": "LOLOS", "score": 75.0, "group": "DUPLIKAT",
        "scenario": "Lamaran Duplikat", "notes": "Email duplikat terdeteksi sistem, memicu penanganan ramah BR-04."
    })

# Tulis berkas kunci jawaban CSV
with open(ANSWER_KEY_PATH, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["id", "name", "email", "phone", "edu", "exp", "matched_skills", "knockout", "score", "group", "scenario", "notes"])
    writer.writeheader()
    for row in cv_records:
        writer.writerow(row)

print(f"SUKSES: 50 berkas CV sintetis dibuat di: {OUTPUT_DIR}")
print(f"SUKSES: Kunci jawaban CSV dibuat di: {ANSWER_KEY_PATH}")
