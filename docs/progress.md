# HargaRumah — Progress Tracker

> **Baca file ini PERTAMA** sebelum melanjutkan pekerjaan apapun.
> Update file ini setiap kali memulai/menyelesaikan sebuah task.

---

## Status Phase

| Phase | Status | Catatan |
|---|---|---|
| Phase 1: Project Setup | ✅ Complete | Semua scaffolding, docs, dependencies |
| Phase 2: Website Exploration | 🔲 Not Started | |
| Phase 3: Scraper Implementation | 🔲 Not Started | Butuh Phase 2 selesai dulu |
| Phase 4: Full Scraping Run | 🔲 Not Started | |

---

## Phase 2: Website Exploration Status

Update kolom **Status** dan **Last Action** setiap kali mulai/berhenti mengerjakan sebuah website.

| Website | Status | Agent Session | Last Action | Catatan |
|---|---|---|---|---|
| Rumah123 | 🔲 Not started | — | — | |
| PasHouses | 🔲 Not started | — | — | |
| OLX Indonesia | 🔲 Not started | — | — | |
| Dekoruma | 🔲 Not started | — | — | |
| Pinhome | 🔲 Not started | — | — | |
| CariProperti | 🔲 Not started | — | — | |
| 99.co | 🔲 Not started | — | — | |
| EasyFind | 🔲 Not started | — | — | |

### Status Legend
- 🔲 `Not started` — Belum dikerjakan
- 🔨 `In progress` — Sedang dikerjakan (update dengan nama/tanggal agent session)
- ✅ `Exploration done` — `docs/websites/<site>.md` sudah lengkap
- 🛠️ `Scraper in progress` — `src/scrapers/<site>.py` sedang diimplementasi
- ✅✅ `Scraper done` — Implementasi selesai, sudah di-test
- ❌ `Blocked` — Ada masalah (login wall, heavy bot protection, dll) — lihat catatan

---

## Phase 3: Scraper Implementation Status

| Website | Doc Ready? | Scraper File | Status | Test Result |
|---|---|---|---|---|
| Rumah123 | 🔲 | `src/scrapers/rumah123.py` | 🔲 Not started | — |
| PasHouses | 🔲 | `src/scrapers/pashouses.py` | 🔲 Not started | — |
| OLX Indonesia | 🔲 | `src/scrapers/olx.py` | 🔲 Not started | — |
| Dekoruma | 🔲 | `src/scrapers/dekoruma.py` | 🔲 Not started | — |
| Pinhome | 🔲 | `src/scrapers/pinhome.py` | 🔲 Not started | — |
| CariProperti | 🔲 | `src/scrapers/cariproperti.py` | 🔲 Not started | — |
| 99.co | 🔲 | `src/scrapers/99co.py` | 🔲 Not started | — |
| EasyFind | 🔲 | `src/scrapers/easyfind.py` | 🔲 Not started | — |

---

## Handoff Protocol (WAJIB dibaca saat ganti agent)

### Jika kamu adalah agent baru yang mengambil alih:

1. **Baca file ini** — lihat di mana pekerjaan terakhir berhenti
2. **Cek file yang "In progress"**:
   - Kalau website exploration: buka `docs/websites/<site>.md` — lihat section mana yang sudah diisi vs masih template
   - Kalau scraper: buka `src/scrapers/<site>.py` — cek apakah class sudah complete atau ada `...` / `TODO`
3. **Lanjutkan dari titik terakhir** — jangan restart dari awal
4. **Update tabel di atas** sebelum mulai kerja (ganti status jadi `In progress`)
5. **Update lagi** setelah selesai (ganti status jadi `done`)

### Jika kamu adalah agent lama yang akan berhenti (quota hampir habis):

1. **Update tabel di atas** — tandai di mana kamu berhenti
2. **Tulis catatan di kolom "Last Action"** — spesifik, contoh: "Sudah explore halaman search, belum document CSS selectors"
3. **Commit semua file yang sudah dikerjakan** — jangan tinggalkan file setengah jadi tanpa commit
4. **Kalau file setengah jadi**, tambahkan comment di dalamnya:
   ```
   # TODO: AGENT HANDOFF - Lanjutkan dari sini
   # Sudah: [deskripsi apa yang sudah dikerjakan]
   # Belum: [deskripsi apa yang belum]
   ```

---

## Session Log

Catat setiap agent session di sini untuk audit trail.

| Tanggal | Agent/Model | Pekerjaan | Hasil |
|---|---|---|---|
| 2026-06-05 | Setup session | Phase 1: Project scaffolding | ✅ Selesai — 51 files |

---

## Blocked Items

Website atau fitur yang blocked dan butuh perhatian khusus:

_(kosong sementara — isi kalau ada website yang tidak bisa di-scrape)_

---

## Data Scraping Sessions

Setiap kali melakukan full scraping run, catat di sini:

| Tanggal | Koordinat | Radius | Total Listings | Output Files | Catatan |
|---|---|---|---|---|---|
| — | — | — | — | — | — |
