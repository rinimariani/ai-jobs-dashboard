# PRD: Dashboard Analisis Dampak AI terhadap Pekerjaan 2030

## 1. Latar Belakang & Tujuan

Dataset `AI_Impact_on_Jobs_2030.csv` berisi 3.000 baris data pekerjaan sintetis dengan 20 kolom, mencakup risiko otomatisasi, permintaan masa depan, gaji, kepuasan kerja, dan kebutuhan upskilling di berbagai industri dan negara.

**Tujuan proyek:** Membangun pipeline end-to-end yang mengubah data mentah menjadi dashboard web interaktif yang dapat diakses publik, dengan data tersimpan di database SQL dan kode tersimpan di GitHub sebagai single source of truth.

**Bukan tujuan proyek ini:** analisis prediktif/ML, real-time data ingestion, atau multi-user authentication. Ini adalah dashboard analitik read-only untuk eksplorasi data.

## 2. Sumber Data

| Atribut | Detail |
|---|---|
| File | `AI_Impact_on_Jobs_2030.csv` |
| Jumlah baris | 3.000 |
| Kolom | 20 (lihat lampiran skema) |
| Sifat data | Sintetis/simulasi — aman dipublikasikan (tidak ada PII nyata) |

**Kolom kunci:**
- Identitas: `Employee_ID`, `Job_Title`, `Industry`, `Country`
- Profil: `Education_Level`, `Years_Experience`, `Company_Size`
- Risiko AI: `AI_Replacement_Risk`, `Automation_Level`, `Future_Demand_Score`, `AI_Tool_Usage`
- Kompensasi & kesejahteraan: `Average_Salary_USD`, `Work_Hours_Per_Week`, `Job_Satisfaction`, `Performance_Score`
- Tren: `Job_Growth_2030`, `Hiring_Trend_2026`, `Upskilling_Needed`, `Remote_Work_Possibility`
- Lainnya: `Required_Skills` (multi-value, dipisah koma)

**Catatan validasi (harus dicek Claude Code di awal, bukan diasumsikan):**
- Cek duplikasi `Employee_ID`
- Cek missing value per kolom
- `Required_Skills` perlu di-parse jadi bentuk ternormalisasi (tabel terpisah) jika mau dianalisis per skill
- Validasi rentang nilai: `AI_Replacement_Risk` dan `Future_Demand_Score` harus 0–1; `Performance_Score`/`Job_Satisfaction` cek skala aslinya (tampak 0–5)

## 3. Arsitektur Sistem

```
CSV (sumber) 
   -> Python ETL script (cleaning + validasi)
   -> PostgreSQL (Supabase, hosted)
   -> Python (SQLAlchemy) query layer
   -> Streamlit dashboard
   -> Streamlit Community Cloud (hosting publik)
   -> GitHub repo (source of truth kode, bukan hosting app)
```

**Keputusan desain penting:**
- Dashboard **tidak** live-query on-demand dari user langsung ke DB tanpa lapisan aman — koneksi DB pakai read-only user, credentials disimpan sebagai Streamlit Secrets (bukan hardcode di repo).
- Data bersifat statis (tidak berubah real-time), jadi caching query (`st.cache_data`) wajib dipakai untuk mengurangi beban DB.
- File `.env`/secrets **tidak pernah** di-commit ke GitHub — gunakan `.gitignore` + `.env.example`.

## 4. Tech Stack

| Layer | Pilihan | Alasan |
|---|---|---|
| Bahasa | Python 3.11+ | Requirement Anda |
| Database | PostgreSQL (Supabase free tier) | Gratis, mudah diakses publik dengan aman, native support Python |
| ORM/Connector | SQLAlchemy + psycopg2 | Standar, portable jika pindah DB provider |
| Dashboard | Streamlit | Deploy tercepat ke publik, integrasi langsung dari GitHub |
| Visualisasi | Plotly (via Streamlit) | Interaktif, lebih baik dari matplotlib untuk web |
| Hosting kode | GitHub (public repo) | Sesuai requirement Anda |
| Hosting app | Streamlit Community Cloud | Gratis, auto-deploy dari GitHub |

## 5. Struktur Dashboard

**Landing / Overview:**
- KPI cards: total data, rata-rata risiko AI, rata-rata gaji, % butuh upskilling
- Filter global: Industry, Country, Company Size (sidebar, mempengaruhi semua section)

**Section 1 — Risk & Automation**
- Distribusi `AI_Replacement_Risk` per industri (box plot / bar)
- `Future_Demand_Score` vs `Automation_Level`
- Heatmap risiko per negara x industri

**Section 2 — Workforce Profile**
- Komposisi Education Level, Years of Experience
- Breakdown by Company Size dan Country

**Section 3 — Compensation & Wellbeing**
- Scatter: `Average_Salary_USD` vs `AI_Replacement_Risk`
- `Job_Satisfaction` vs `Work_Hours_Per_Week`
- Distribusi gaji per industri

**Section 4 — Trends**
- `Hiring_Trend_2026` breakdown (Growing/Stable/Declining)
- `Job_Growth_2030` per industri
- `Upskilling_Needed` — proporsi Yes/No per risk band

## 6. Struktur Repo GitHub (yang harus dibuat Claude Code)

```
ai-jobs-dashboard/
├── README.md                  # cara run lokal + link demo live
├── .gitignore                 # exclude .env, __pycache__, dll
├── .env.example                # template env var (tanpa isi asli)
├── requirements.txt
├── data/
│   └── AI_Impact_on_Jobs_2030.csv
├── etl/
│   └── load_to_db.py           # baca CSV -> validasi -> insert ke Postgres
├── dashboard/
│   ├── app.py                  # entry point Streamlit
│   ├── db.py                   # koneksi & query layer
│   └── pages/                  # kalau multi-page
└── .streamlit/
    └── config.toml
```

## 7. Tahapan Kerja (untuk diserahkan ke Claude Code)

1. **Setup & validasi data** — baca CSV, cek duplikat/missing/rentang nilai, laporkan temuan sebelum lanjut
2. **Provisioning database** — buat project Supabase, definisikan skema tabel, buat read-only role untuk dashboard
3. **ETL script** — script idempotent (aman dijalankan ulang tanpa duplikasi) untuk load CSV ke Postgres
4. **Query layer** — fungsi-fungsi query terpisah dari UI, dengan caching
5. **Dashboard UI** — bangun per section sesuai struktur di atas, mulai dari Overview
6. **Local testing** — jalankan `streamlit run` lokal, verifikasi semua chart & filter
7. **GitHub setup** — init repo, `.gitignore` benar sebelum commit pertama (supaya secrets tidak pernah masuk histori git)
8. **Deploy ke Streamlit Community Cloud** — hubungkan ke GitHub repo, set secrets di dashboard Streamlit Cloud (bukan di kode)
9. **Dokumentasi README** — cara setup lokal, link demo live, screenshot

## 8. Batasan & Risiko yang Perlu Disadari

- **Free tier Supabase** punya batas koneksi & bandwidth — cukup untuk proyek personal/portofolio, bukan untuk trafik tinggi.
- **Streamlit Community Cloud** app publik bisa sleep jika tidak diakses dalam waktu lama (butuh reload beberapa detik saat wake-up) — bukan bug, ini karakteristik tier gratis.
- Karena data sintetis, dashboard ini cocok untuk **portofolio/demo skill**, bukan untuk pengambilan keputusan bisnis nyata — sebaiknya disebutkan di README agar audiens tidak salah paham.

## 9. Definition of Done

- [ ] Data tervalidasi dan berhasil di-load ke PostgreSQL
- [ ] Dashboard berjalan lokal tanpa error
- [ ] Repo GitHub publik, tanpa credential ter-expose di histori commit manapun
- [ ] Dashboard live dan bisa diakses lewat URL publik Streamlit Cloud
- [ ] README lengkap dengan link demo dan instruksi setup
