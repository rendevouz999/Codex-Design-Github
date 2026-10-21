# Presentation Design Template Guide — Owner Standard (Codex-Design)

Versi / Version: 1.1 — 2026-10-21 (metadata listing addendum; standar desain 2026-10-14 tetap). Pemilik / Owner: Yusuf Muhamad Iqbal (Joe). Status: **mode kalibrasi** (dua PPTX + CSV/JSON metadata; tanpa paket produksi) sampai owner mengatakan persis `kita mulai jalur produksi`.

ID — Dokumen ini adalah panduan tunggal untuk AI (Main + satu Engineer) yang membuat *presentation design template* PPTX dengan plugin `<CODEX_DESIGN_WORKSPACE>` mengikuti cara kerja owner. Ia mengkhususkan, bukan menggantikan, `AGENTS.md` dan skill `skills/presentation-deck`. Jika guide ini dan file plugin bertentangan pada gate, file plugin menang; pada selera desain dan konstruksi file, standar owner di guide ini menang.
EN — This is the single guide for an AI (Main plus one Engineer) building PPTX presentation design templates with the `<CODEX_DESIGN_WORKSPACE>` plugin the owner's way. It specialises `AGENTS.md` and the `skills/presentation-deck` skill; it does not replace them. On gates the plugin files win; on design taste and file construction the owner standard in this guide wins.

Sumber bukti / Evidence sources: `output/Owner-Standard-Study_20261014/OWNER_WORK_PATTERN_STUDY.md` (studi deck owner, render native, XML, forensik build), `Referensi dari User/Marketing Growth Plan Presentation/Presentation.pptx` (SHA-256 `feb1bd52…ec6d`), `output/Ruled-Margin_20261013/` (contoh lengkap jalur plugin yang lulus semua gate, tetapi desainnya BUKAN standar owner).

---

## 0. Cara memakai guide ini / How to use this guide

ID — Baca seluruh file sebelum bertindak. Jalankan bagian 6 berurutan; setiap langkah menulis bukti ke folder proyek. Jangan menyingkat gate. Jangan menanyakan ulang keputusan yang sudah ada di sini. Tanyakan hanya yang ada di bagian 3 (intake) dan ambiguitas material baru, selalu dengan 3 jawaban rekomendasi + 1 kolom bebas.
EN — Read the whole file first. Run section 6 in order; every step writes evidence into the project folder. Never shorten a gate. Never re-ask decisions already recorded here. Ask only section 3 intake questions and genuinely new material ambiguities, always as 3 recommended answers + 1 free column.

Path: `<PLUGIN_ROOT>` = `<CODEX_DESIGN_WORKSPACE>` (di Claude Code juga `~/.claude/skills/codex-design`, junction ke pohon yang sama). Proyek baru: `<PLUGIN_ROOT>/output/<Nama>_<YYYYMMDD>/`. Interpreter: skrip `scripts/*` memakai Python host (`python`); runtime presentasi memakai `<PLUGIN_ROOT>/.venv-presentation/Scripts/python.exe`. Selalu path absolut; jangan mengandalkan CWD.

---

## 1. Aktivasi, tim, dan peran / Activation, team, roles

| Host | Main | Engineer (tepat satu / exactly one) | Cara dispatch / Dispatch |
|---|---|---|---|
| Claude Code (Desktop/CLI) | Claude Fable 5.1 (`claude-fable-5-1`) | Subagent plugin `codex-design:general-design-production-engineer` (`model: claude-opus-5-5`, `effort: xhigh`, definisi di `agents/general-design-production-engineer.md`) | Agent tool dengan `subagent_type="codex-design:general-design-production-engineer"`; revisi ke agent yang sama lewat SendMessage |
| Codex (Desktop/CLI) | GPT-6 Astra | `gpt-6.1-sol` dengan `reasoning_effort="xhigh"` | Subagent tool host dengan `model="gpt-6.1-sol", reasoning_effort="xhigh"` dan role prompt dari `.design-brain/runtime/HOST_DESIGN_PRODUCTION_SPECIALIST.md` |

ID — Main memegang Creative Direction, Delegation dan Approval dengan **auto-full trust** owner: menetapkan arah, menulis brief, memeriksa bukti sendiri, memutuskan PASS/REVISE, tanpa minta persetujuan owner per langkah. Engineer mengerjakan tugas terbatas (authoring SVG, export, render, ukur, cari foto, perbaikan) dan mengembalikan `NEEDS_MAIN_REVIEW` / `REVISE_REQUIRED` / `BLOCKED` / `UNVERIFIED` dengan bukti. Tidak ada reviewer tambahan, tidak ada Engineer kedua, tidak ada panel; mode "ultracode" atau kapasitas host tidak memperbesar tim. Engineer yang sudah selesai di sesi lama bukan anggota aktif; buat instance baru bila transcript hilang, lalu pakai terus instance itu.
EN — Main owns creative direction, delegation and approval under the owner's auto-full trust. The Engineer does bounded work and returns evidence with a status. No extra reviewers, no second Engineer, no panels regardless of host mode or capacity. A finished Engineer from an old session is not active; spawn one new instance when its transcript is gone and reuse it afterwards.

Setiap prompt ke Engineer wajib memuat / Every Engineer prompt must state:

1. Mode aktif host: Ponytail, i-have-adhd, Caveman, RTK, dengan safeguard (tidak memotong deliverable, verifikasi, kualitas desain, analisis referensi).
2. Path otoritatif (guide ini, proyek, brief Main), format/ukuran output, path yang boleh ditulis (eksklusif), deliverable, kriteria verifikasi.
3. Batas: hanya slide yang ditugaskan (pilot = slide 1–3), tidak boleh spawn agent, tidak boleh ganti model, tidak boleh menyetujui hasil sendiri.
4. Memori: Engineer hanya `read`/`search`/`list` lewat `scripts/design_brain_memory_adapter.py --actor engineer …`; Main yang `put`.

---

## 2. Mode kalibrasi dan deliverable / Calibration mode and deliverables

ID — Sampai owner mengatakan persis `kita mulai jalur produksi`: hasil utama tetap **dua PPTX**: (a) `<Nama>_<N>_Slides_v<k>.pptx` berisi foto sumber yang sudah disetujui Main, (b) `<Nama>_<N>_Slides_v<k>_placeholders.pptx` salinan tanpa foto sehingga placeholder menampilkan pola. **Pengecualian deliverable wajib:** setelah kedua PPTX final lolos gate, buat **dua file metadata listing terpisah** di `<P>/exports/`: `product-metadata.csv` untuk review manual dan `product-metadata.json` untuk otomatisasi, mengikuti bagian 6.16. Jadi total deliverable mode kalibrasi adalah dua PPTX + dua metadata, tanpa zip, START_HERE, Editing Guide, Design System kit, atau preview kit. Bukti internal plugin (receipt, manifest, render, pengukuran) tetap wajib dibuat; tetap di folder proyek dan tidak dikemas.
EN — Until the owner says exactly `kita mulai jalur produksi`, keep the two PPTX deliverables (photo-filled and patterned placeholders). After both final decks pass their gates, additionally deliver two separate listing metadata files in `<P>/exports/`: `product-metadata.csv` (manual review) and `product-metadata.json` (automation), per section 6.16. Calibration therefore delivers two PPTX plus two metadata files, but no production package or preview kit. Internal gate evidence stays in the project folder.

ID — Koreksi owner: selesaikan dengan solusi nyata terbaik. Jangan mundur ke baseline aman, jangan menyederhanakan atau meminimaliskan desain sebagai jalan keluar. Catat setiap koreksi lewat `scripts/design_brain_reflect.py`.
EN — Owner corrections get the best real solution; never a safe baseline, never deliberate minimalism. Record each correction with `scripts/design_brain_reflect.py`.

Ukuran / Size: PPTX baru selalu 10 × 5.625 in, `ppt169onscreen`, SVG 960 × 540 unit (1 unit = 0.75 pt; 9144000 × 5143500 EMU). Tidak ditanyakan lagi.

---

## 3. Intake: pertanyaan wajib ke owner / Mandatory intake questions

ID — Sebelum studi referensi, tanyakan hanya yang belum diketahui dari brief. Format: setiap pertanyaan membawa 3 jawaban rekomendasi relevan + 1 kolom bebas (di Claude Code pakai AskUserQuestion; di Codex tulis daftar bernomor dengan opsi A/B/C + "lainnya").
EN — Before the reference study, ask only what the brief does not already answer, always with 3 relevant recommended answers + 1 free column.

| # | Pertanyaan / Question | Catatan / Note |
|---|---|---|
| 1 | Jumlah slide dan roster peran (cover, snapshot, agenda, bab, closing) | Default owner: 20 slide, satu ide per slide |
| 2 | Niche, buyer, tujuan deck, marketplace | Isi cognition receipt |
| 3 | ~~Teks: text box bebas atau placeholder master?~~ **Aturan tetap (owner, 2026-10-15), jangan ditanya lagi** | Master dan semua layout hanya berisi picture placeholder berpola, tanpa teks apa pun; layout 1 `Default` kosong/blank (0 shape); picture placeholder hanya di layout setelah `Default`; semua teks slide = text box bebas berformat eksplisit |
| 4 | Pasangan font (default Archivo Bold + Inter) | Jangan rotasi font tanpa persetujuan |
| 5 | Warna sinyal (default keluarga neon seperti lime) dan tint tenang | Peran warna tetap (bagian 4.3); hue boleh baru |
| 6 | Foto: sumber Unsplash/Pexels; warna vs monokrom **diputuskan Main setelah palet deck tetap** (owner, 2026-10-15: foto harus senada dengan gaya warna yang dibangun; tidak ditentukan di muka) | Kebijakan foto bagian 6.8 |
| 7 | Nama template kandidat | Cek `design_brain_name_check.py` dulu |
| 8 | Referensi tambahan dari owner (gambar, PPTX, video) | Video: ekstrak frame ber-timestamp dengan ffmpeg lalu inspeksi |

Jangan tanya ukuran PPTX, tim, model, effort, mode kalibrasi, atau hal yang sudah ada di guide ini.

---

## 4. Standar desain owner / Owner design standard

Diukur dari deck owner (render native PowerPoint 16.0, pengukuran COM, XML). Pelajari sebagai **sistem**; komposisi tiap slide, palet persis, copy, dan urutan bab harus dibuat baru (gate originalitas tetap berlaku).
Measured from the owner's deck. Learn it as a system; compositions, exact palette, copy and chapter order must be new (originality gates apply).

### 4.1 Kanvas, margin, kolom / Canvas, margins, columns

| Item | Nilai / Value |
|---|---|
| Kanvas | 960 × 540 unit, kanvas bersih, **tanpa grid tergambar** |
| Margin kiri/kanan | 48 unit; konten 48 → 912 (lebar 864) |
| Header meta | kotak teks y = 24 (puncak huruf terlihat ≈ 25) pada komposisi dasar; kiri `BRAND / NAMA DECK`, kanan `NN / <total>`; header ikut bergeser bersama blok (baris berikut) |
| Puncak judul | y ≈ 55–60 pada komposisi dasar |
| Blok terpusat (aturan owner 2026-10-15, video + 2 tangkapan layar + penjelasan tertulis) | **Uji terima owner:** semua isi satu slide dipilih, di-group, lalu Arrange > Align > Align Center + Align Middle (relatif ke slide). Group **tidak boleh bergeser sama sekali**; jarak atas, bawah, kanan, kiri sama. Karena Align memakai frame bentuk, uji ini = gabungan frame semua bentuk pada slide terpusat di slide (`skills/presentation-deck/runtime/design_brain_pptx_group_align_check.py`, toleransi 0,05 pt). Cara memenuhinya: setelah komposisi selesai, geser seluruh isi slide (header, judul, intro, modul, label, nomor halaman, picture placeholder) sebagai satu kesatuan dengan satu offset per slide: dy = (540 − (atas + bawah)) / 2, dx = (480 − (kiri + kanan) / 2). **Ukuran, jarak dalam, font, frame foto tidak diubah.** Frame harus rapat ke isi yang ter-render (text box tanpa inset; chart dengan manual layout agar isi memenuhi frame), supaya uji frame dan mata sepakat. Slide dengan foto full-bleed: foto tetap, blok sisanya terpusat vertikal dan berjarak sama ke tepi panel (`--panel`). Posisi header boleh berbeda antar slide; owner tidak mempermasalahkan. Verifikasi kedua: gate piksel render native (6.9) |
| Batas bawah konten lama | ≈ 500 pada deck owner (celah 25/40) — **bukan aturan**; yang berlaku adalah blok terpusat di atas |
| Gutter | 12 unit |
| Kolom | 4 × 207 · 5 × 163 · 3 × 282 · 2 × 420 · dashboard 530 + 322 |
| Padding kartu | 16 unit |
| Radius kartu | ≈ 8–12 unit (`adj` 4166–12500); pill bulat penuh (`adj` 50000) |

### 4.2 Tipografi / Typography (pt native; unit SVG = pt ÷ 0.75)

| Peran / Role | Spesifikasi / Spec | Unit SVG |
|---|---|---|
| Header meta, eyebrow, label | Inter Bold 6 pt, kapital, tracking +0.75 pt, `#5E5E5A` (gelap: `#A3A29C`) | font-size 8, letter-spacing 1 |
| Judul slide | Archivo Bold 45 pt, 1–2 baris, line spacing 1.0 (Multiple / `spcPct` 100%), tracking −1.13 pt, rata kiri x 48 | font-size 60, letter-spacing −1.5 |
| Judul raksasa | Archivo Bold 74–124 pt (section, angka hero, closing) | 99–165 |
| Angka KPI kartu / stat hero | Archivo Bold 24 pt / 36–45 pt | 32 / 48–60 |
| Judul kartu / item | Archivo Bold 15–18 pt / 12 pt | 20–24 / 16 |
| Intro slide | Inter Regular 9 pt, line spacing **1.5** (aturan owner 2026-10-15, direvisi dari 1.0 pada hari yang sama; sama dengan deck owner), `#5E5E5A`, rata kanan, lebar ±300–330 unit, sejajar puncak judul | 12 |
| Body kartu / body modul | Inter Regular 9 pt, line spacing 1.5 (Multiple / `spcPct` 150%) | 12 |
| **Line spacing per peran (aturan owner 2026-10-15, semua slide, semua deck)** | Nilai PowerPoint *Multiple* (`a:lnSpc/a:spcPct`), eksplisit pada **setiap paragraf** termasuk kotak satu baris dan sel tabel: header meta / running header **1.0**; teks zona margin bawah (footer, kontak, label garis) **1.0**; judul slide / headline / sub-headline / angka display **1.0**; intro / standfirst / lead **1.5** (revisi owner 2026-10-15; semula 1.0); isi modul konten / body text (deskripsi, bullet, caption, bio, kutipan, sel tabel isi) **1.5**. Bukan `spcPts` (poin tetap). 1.0 = tinggi baris alami font (Inter ≈ 1,21 em metrik hhea / 1,43 em metrik win; Archivo Bold ≈ 1,09 / 1,51), jadi ritme vertikal dihitung dari nilai terukur PowerPoint di host, bukan dari ukuran font. Audit file: 0 paragraf tanpa `spcPct`, nilai sesuai peran; setelah itu jalankan ulang gate keseimbangan (6.9) | — |
| Teks kecil | Inter 7 pt | 9.3 |
| Pill | Inter Bold 6 pt kapital tracked; tinggi 16–20 unit; padding ±10–12 | 8 |

Dua font, dua peran: Archivo = suara (judul, angka); Inter = bacaan. Tanpa italic, tanpa serif, kecuali owner meminta.

### 4.3 Peran warna / Colour roles (hue boleh baru, peran tetap)

| Peran / Role | Contoh owner | Pemakaian / Use |
|---|---|---|
| Paper (latar) | `#F6F5F1` | latar semua slide terang; bukan putih murni |
| Ink | `#111111` | teks; permukaan jangkar (kartu, band, panel); slide gelap |
| Signal | `#B9F15A` | **satu sel per modul**: 1 dari 4 kartu, 1 node, 1 bar, sel "Primary", 1 kata judul, tombol CTA |
| Calm tint | `#CFE7DE` | permukaan sekunder lembut |
| White card | `#FFFFFF` | kartu di atas paper, lift tanpa bayangan |
| Body grey | `#5E5E5A` | intro/body |
| Muted on dark | `#A3A29C` | meta di slide gelap |
| Hairline | `#D9D7D0` 0.5 pt | pemisah baris saja |
| Rule kuat | ink 0.75 pt | outline pill, garis stat |
| Track | `#E9E8E2` | track progress bar (6 unit) |
| Chart secondary | `#8C8B86` | seri pembanding |

Flat: nol gradien, nol bayangan, nol glow. Jangan memakai pasangan lime `#B9F15A` + mist `#CFE7DE` persis.

### 4.4 Formula slide dan kepadatan / Slide formula and density

1. Header meta kiri + nomor `NN / total` kanan di setiap slide (pengecualian hanya bila band foto menutup baris atas; pindahkan ke bawah).
2. Judul besar kiri + intro satu kalimat rata kanan di kanan atas.
3. **Satu modul** memenuhi lebar 48 → 912: kartu (3/4/5), tabel native, chart native, alur/timeline, split dengan foto. 4–6 item per modul. Tidak ada dua modul bersaing.
4. Satu sinyal per modul; ink sebagai jangkar, tint sebagai penenang, putih sebagai pengangkat.
5. Bukti angka hampir di setiap slide: label 6 pt kapital → angka 24–45 pt → keterangan 9 pt; baris stat di atas hairline.
6. Ritme gelap: cover dan closing gelap (`p:bg` level slide), plus 1–2 band/panel gelap di tengah.
7. Komponen: kartu membulat, pill (ink / signal / outline / tint), tile KPI, progress bar, node ikon lingkaran 48 unit, panah alur, tabel dengan header band ink 40 unit.
8. Copy pendek dan spesifik: intro satu kalimat, tag 1–2 kata, bullet 3–6 kata, angka konkret; tahun contoh 2046+ sesuai bagian 4.4.1.

### 4.4.1 Tanggal dan tahun konten / Example content dates

Aturan owner, dikonfirmasi 2026-10-17. Untuk konten contoh/fiktif yang dibuat AI dalam template presentasi, **tahun paling awal adalah 2046**. Gunakan 2046, 2047, 2048, dan seterusnya sesuai kebutuhan narasi; jangan mengambil tahun kalender saat ini sebagai default konten contoh.

- Berlaku pada tahun/tanggal contoh di cover, header/footer, timeline, roadmap, milestone, jadwal, periode laporan, label chart, tabel dan catatan presentasi. Contoh: `Q1 2046`, `15 March 2046`, `2046–2048`. Tidak setiap slide harus memuat tanggal.
- Tetapkan satu acuan waktu deck dan pertahankan kronologi yang masuk akal. Tanggal mulai tidak boleh sesudah selesai; periode, kuartal, label dan ringkasan harus selaras. Jika hari dalam minggu ditampilkan, cocokkan dengan tanggal sebenarnya; format tanggal dan zona waktu harus konsisten bila dicantumkan.
- Tahun minimum ini berlaku untuk data contoh buatan. Tanggal faktual/historis dari sumber, dokumen pengguna, atau instruksi tanggal eksplisit tidak boleh diubah diam-diam agar memenuhi 2046. Pertahankan fakta; jika pengguna meminta pengubahan menjadi skenario contoh, tandai sebagai ilustrasi dan selaraskan seluruh dependensinya.
- Jangan menerapkan tahun 2046 pada timestamp sistem, log, audit, provenance, tanggal file atau catatan pengerjaan: semuanya tetap memakai waktu kejadian yang sebenarnya.
- Sebelum penyerahan, periksa konten tanggal yang dihasilkan, termasuk notes dan teks tersembunyi yang ikut dikirim. Pastikan setiap tahun contoh >= 2046 dan tidak ada periode yang saling bertentangan. Aturan ini tidak mengubah peta line spacing bagian 4.2.

EN — AI-authored fictional/example dates in presentation content start in **2046 or later**. Keep one coherent timeline across the deck. Preserve factual/source dates and explicit user dates; do not falsify evidence or system timestamps. Clearly distinguish illustrative data from facts. Keep the confirmed typography role spacing unchanged.

### 4.5 Foto / Photos

Monokrom (default), orang nyata dan kerja nyata, sebagai blok struktural: setengah kanan full-bleed, band atas (±230) atau bawah (±195), sepertiga kanan, blok besar 400 × 420, sisipan membulat 240 × 130 / 180 × 110. Sudut membulat hanya pada band/sisipan; siku pada full-bleed. Teks tidak menimpa foto kecuali kartu solid. Crop di placeholder (`srcRect`), bukan di file.

### 4.6 Batas originalitas / Do-not-copy boundary

Tidak menyalin: komposisi slide owner, copy "Lumen & Co.", palet lime/mist persis, band agenda, lingkaran TAM/SAM/SOM, tangga funnel, susunan dashboard KPI, layout closing. Yang diambil: sistem 4.1–4.5 dan konstruksi file bagian 5.

---

## 5. Standar konstruksi file / File construction standard

ID — Urutan tetap (jawaban owner): **tema (warna + font) → master kosong → layout foto dengan placeholder berpola → slide**. Struktur hasil harus sama dengan file owner.
EN — Fixed order: theme → empty master → photo layouts with pattern-filled picture placeholders → slides. The resulting structure must match the owner's file.

| Bagian / Part | Wajib / Required |
|---|---|
| Tema | `theme1.xml`: font mayor Archivo, minor Inter (atau pasangan yang disetujui); warna tema: dk1/dk2 ink, lt1 putih, lt2 paper, accent1 signal, accent2 tint, accent3 ink, accent4 mid grey, accent5 body grey, accent6 hairline |
| Master | Hanya latar paper. **0 teks, 0 shape, 0 placeholder teks.** Text styles master boleh ada (dari `spec_lock` title/body) |
| Layout | `Default` kosong (0 shape) untuk slide tanpa foto + `Photo Layout 01…NN`, satu per kombinasi frame foto, masing-masing **hanya** 1–3 picture placeholder pada frame foto final |
| Placeholder foto | `type="pic"`, nama `Picture Placeholder 01/02/03`, prompt `Drop photo here`, inset 0, tanpa garis; fill **Pattern fill → Diagonal stripe: light upward** (`pattFill prst="ltUpDiag"`), Foreground **Dark Gray, Accent 5**, Background **White, Background 2** |
| Teks slide | Default: text box bebas berformat eksplisit (inset 0, tanpa autofit), bukan placeholder; placeholder teks hanya bila owner memilihnya untuk produk itu (intake #3). **Tidak ada contoh teks di master/layout** |
| Slide gelap | `p:bg` di level slide menimpa master |
| Nama shape | Semantik: `Header Label`, `Page Number`, `Headline`, `Intro`, `Metric Card 1`, `Metric Value`, `Progress Track`, `Progress Fill`, `Photo 01` |
| Data | Chart native (line/bar/doughnut) dan tabel native; progress bar dari rounded rect; angka total diketik manual bila perlu |
| Foto | Masuk lewat placeholder layout (`blipFill` + `srcRect`), alt text deskriptif, derivatif grayscale di `images/derived/` |
| Tanpa | Transisi, animasi, notes, gradien, bayangan, grup (kecuali perlu) |
| Versi jual | Foto dihapus dari slide; placeholder kembali berpola; layout byte-identik |

Pemetaan ke runtime plugin (jalur `structured`):

| Standar owner | Deklarasi SVG runtime |
|---|---|
| Master = latar saja | Satu `<rect id="master-paper" data-pptx-layer="master" …/>` full-canvas; **tidak ada** atom master lain |
| Layout `Default` kosong | Root `data-pptx-layout="default"` tanpa atom layout dan tanpa slot (layout nol slot sah) |
| `Photo Layout NN` | Root `data-pptx-layout="photo-layout-NN"`; satu `<g id="photo-0k" data-pptx-placeholder="picture" data-pptx-bounds="x y w h">` per foto berisi satu `<image data-pptx-carrier="true" …>` |
| Teks bebas | `<text>` tanpa marker struktur (Slide-local) |
| Placeholder teks (bila dipilih) | `<g data-pptx-placeholder="title|body"><text data-pptx-carrier="true">…</text></g>` |
| Slide gelap | `<rect data-pptx-layer="slide" …fill="#111111"/>` full-canvas |
| Chart/tabel native | Slot `data-pptx-placeholder="chart|table"` + carrier `data-pptx-replace-with` + `data-pptx-native-authority="json"`; export dengan `--native-data` |
| Pattern fill placeholder | **Tidak didukung runtime** → langkah finishing COM (bagian 6.7) |

---

## 6. Pipeline langkah demi langkah / Step-by-step pipeline

Semua perintah dari `<PLUGIN_ROOT>`; `<P>` = folder proyek absolut; `<A>` = `<P>/analysis`. Flag di bawah terbukti pada build Ruled Margin (2026-10-13/14); cek `--help` bila skrip berubah.

### 6.0 Persiapan / Preparation

```bash
python scripts/design_brain_status.py
.venv-presentation/Scripts/python.exe skills/presentation-deck/runtime/presentation.py doctor
python scripts/design_brain_memory_adapter.py --actor main status
python scripts/design_brain_memory_adapter.py --actor main search "<niche atau kata kunci>"
python scripts/design_brain_memory_adapter.py --actor main read owner-standard-marketing-growth-plan-20261014
```

Baca juga: `.design-brain/VISUAL_INSPECTION_PROTOCOL.md`, `.design-brain/LOCAL_MEMORY_POLICY.md`, `skills/presentation-deck/workflows/{native.md,PPTX_SIZE_POLICY.md,PPTX_FIRST_THREE_SLIDES_REVIEW.md,PPTX_IMAGE_SELECTION_POLICY.md,PPTX_LAYOUT_ORIGINALITY_POLICY.md}`, `skills/presentation-deck/design/native/{pptx-structure-interface.md,semantic-svg.md,native-data-interface.md}`.

### 6.1 Studi referensi / Reference study (Main)

ID — Untuk setiap referensi owner: buka setiap gambar/slide satu per satu (overview → crop detail → overview), dan bila PPTX: render native, ukur COM, baca XML (tema, master, layout, placeholder, warna srgb/scheme, font, text box, nama shape, metadata build). Tulis `<A>/main-reference-study.md` (sistem, grammar, kepadatan, bahasa komponen, foto, cara membangun, do-not-copy) dan `<A>/main-reference-fingerprint.json`. Simpan insight:
EN — Inspect every reference individually; for PPTX also render natively, measure, and read the XML (theme, master, layouts, placeholders, colour referencing, fonts, text boxes, names, build metadata). Write the study and fingerprint, then store the insight:

```bash
python scripts/design_brain_reference_insight.py --reference-name "<ref>" --reference-type "<owner-pptx|pinterest|video-frames>" --template-category "presentation-deck" --observed-intent "…" --buyer-decision-model "…" --cognition-evidence "…" --attention-strategy "…" --emotional-rhythm "…" --trust-strategy "…" --density-strategy "…" --conversion-logic "…" --component-reasoning "…" --repeated-designer-pattern "…" --visual-mood "…" --color-role-insight "…" --palette-reconstruction "…" --structural-insight "…" --section-count-judgment "…" --hierarchy-insight "…" --section-flow-insight "…" --marketplace-insight "…" --lesson "…" --do-not-copy "…" --reinterpretation "…"
```

Alat render/ukur PPTX referensi: `powershell -File output/Ruled-Margin_20261013/engineering/inspect_native.ps1 -InputPath <ref.pptx> -ReportPath <A>/reference-native-report.json -RenderDir <A>/reference-render` (salin skrip ke `<P>/engineering/` sebagai alat proyek). Video: `ffmpeg -i <video> -vf fps=1 <A>/frames/f_%04d.png` lalu inspeksi frame ber-timestamp.

### 6.2 Nama dan gate pemakaian referensi / Name and reference-usage gate

```bash
python scripts/design_brain_name_check.py --candidate-name "<Nama>" --niche "<niche>" --template-type "PowerPoint presentation template" --dry-run
python scripts/design_brain_build_session.py start --task "<tugas>" --expected-templates 1 --output-dir <A>/main-session --product-family presentation_deck --mode pptx --json
python scripts/design_brain_build_session.py register-reference-usage-check --session <A>/main-session --template-id <id> --candidate-brand-name "<Nama>" --reference-usage-mode single --reference-group-key <group-key> --json
python scripts/design_brain_build_session.py register-reference --session <A>/main-session --template-id <id> --reference <A>/main-reference-study.md --fingerprint <A>/main-reference-fingerprint.json --json
```

### 6.3 Cognition receipt + simulation (Main)

ID — Tulis `<A>/main-cognition.json` dengan kunci: `task, productFamily, mode, referenceSource, batchItem, routeSource, brandReferenceUsage, styleDNA, referenceStandard, designIntentLock, visualGrammar, referenceBoundary, colorRoleRemapping, visualMoodReinterpretation, structuralReconfiguration, patternDivergence, sectionLogic, marketplaceReadiness, status` (lihat contoh `output/Ruled-Margin_20261013/analysis/main-cognition.json`). `referenceBoundary` wajib memuat kalimat literal "Do not copy exact layout, exact color palette, section order, hero grammar, component scaffold …" dan `sectionLogic`/struktur wajib memuat kata anatomi: hero, proof, service, process, testimonial, cta, footer. Lalu:
EN — Write the cognition receipt with those keys; include the literal do-not-copy sentence and the anatomy keywords, then:

```bash
python scripts/design_brain_design_cognition_check.py --receipt <A>/main-cognition.json --json --strict
python scripts/design_brain_design_simulate.py --task "…" --template-type "PowerPoint presentation template" --niche "…" --target-buyer "…" --visual-mood "…" --marketplace "Envato" --mode pptx --product-family presentation_deck --output-contract "native editable PPTX 10 x 5.625 inches, <N> slides" --proposed-structure "<roster dengan kata anatomi>" --reference-summary "<ringkasan + do-not-copy>" --output-dir <A>/main-simulation
python scripts/design_brain_build_session.py register-cognition --session <A>/main-session --template-id <id> --receipt <A>/main-cognition.json --json
python scripts/design_brain_build_session.py register-simulation --session <A>/main-session --template-id <id> --verdict <A>/main-simulation/report/design_verdict.json --json
```

`design_verdict.json` harus `PASS`; `REVISE` → perbaiki lalu ulang; `BLOCKED` → jangan build.

### 6.4 Rencana, fingerprint, audit layout / Plan, fingerprint, layout audit

ID — Tulis `<A>/main-fingerprint.json` (kunci seperti `output/Ruled-Margin_20261013/analysis/main-fingerprint.json`: heroGrammar, sectionOrder, gridSystem, layoutRhythm, cardCadence, componentPatterns, ctaPlacement, imageTreatment, typographyBehavior, colorRoles, effectLanguage, navigationPattern, footerPattern, …) dan brief Engineer `<A>/main-engineer-brief-pilot.md` berisi: sistem bagian 4 dengan hue/font yang dipilih, roster slide dengan peran dan modul, layout foto dan frame, daftar text box per slide, aturan konstruksi bagian 5, path yang boleh ditulis.

```bash
python scripts/design_brain_build_session.py register-plan --session <A>/main-session --template-id <id> --plan <A>/main-engineer-brief-pilot.md --fingerprint <A>/main-fingerprint.json --json
python scripts/design_brain_build_session.py audit-layout --session <A>/main-session --template-id <id> --json
```

### 6.5 Proyek runtime dan authoring SVG / Runtime project and SVG authoring (Engineer)

```bash
.venv-presentation/Scripts/python.exe skills/presentation-deck/runtime/presentation.py init <P> --format ppt169onscreen
```

`spec_lock.md` (dibuat/dilengkapi Engineer dari brief Main; contoh lengkap `output/Ruled-Margin_20261013/spec_lock.md`):

```
## canvas
- viewBox: 0 0 960 540
- format: ppt169onscreen
## colors
- bg: #<paper>            # menjadi lt1
- secondary_bg: #<paper>  # menjadi lt2 = "Background 2" untuk pola placeholder
- text: #<ink>
- text_secondary: #<body-grey>
- primary: #<ink>
- accent: #<signal>
- secondary_accent: #<tint>
- border: #<hairline>
## typography
- font_family: Inter
- title_family: Archivo
- body_family: Inter
- title: 60      # 45 pt
- body: 12       # 9 pt
## pptx_structure
- mode: structured
## pptx_masters
- <master-key>: <Master Name>
## pptx_layouts
- default: <master-key> | Default | P03
- photo-layout-01: <master-key> | Photo Layout 01 | P01
## page_pptx_layouts
- P01: photo-layout-01
- P03: default
```

Halaman `svg_output/P<NN>_<slug>.svg` (satu per slide). Kerangka slide foto / photo-slide skeleton:

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="960" height="540" viewBox="0 0 960 540" lang="en-US" font-family="Inter"
     data-pptx-master="<master-key>" data-pptx-master-name="<Master Name>"
     data-pptx-layout="photo-layout-01" data-pptx-layout-name="Photo Layout 01">
  <rect id="master-paper" data-pptx-layer="master" data-pptx-editable="false" x="0" y="0" width="960" height="540" fill="#F6F5F1"/>
  <g id="photo-01" data-pptx-placeholder="picture" data-pptx-bounds="648 192 264 287">
    <image id="photo-01-carrier" data-pptx-carrier="true" href="../images/derived/cover.jpg" x="648" y="192" width="264" height="287" preserveAspectRatio="xMidYMid slice"/>
  </g>
  <text id="header-label" x="48" y="30" font-family="Inter" font-weight="700" font-size="8" letter-spacing="1" fill="#5E5E5A">BRAND / DECK NAME</text>
  <text id="page-number" x="912" y="30" text-anchor="end" font-family="Inter" font-weight="700" font-size="8" letter-spacing="1" fill="#5E5E5A">01 / 20</text>
  <text id="headline" x="48" y="110" font-family="Archivo" font-weight="700" font-size="60" letter-spacing="-1.5" fill="#111111">Marketing</text>
  <!-- kartu: rect rx="10" + text box terpisah; slide gelap: tambahkan <rect data-pptx-layer="slide" … fill="#111111"/> tepat setelah master-paper -->
</svg>
```

Aturan authoring / Authoring rules:

1. Satu-satunya atom master = `master-paper`. Tidak ada garis, teks, logo di master/layout.
2. Slide tanpa foto memakai `data-pptx-layout="default"` tanpa slot. Frame foto yang berbeda = layout baru `photo-layout-NN`; frame identik berbagi key.
3. Semua teks Slide-local `<text>` kecuali owner memilih placeholder teks (intake #3). `id` semantik (menjadi nama shape).
4. Ukuran font dalam unit (pt ÷ 0.75); tracking label +1 unit; judul −1.5 unit; leading body 150%.
5. Kartu = `rect rx` 8–12 + text box terpisah; pill = `rect rx` = ½ tinggi; progress = track 6 unit + fill.
6. Chart/tabel: slot `chart|table` dengan carrier `data-pptx-replace-with` + metadata JSON (lihat `native-data-interface.md`), export `--native-data`.
7. Foto: derivatif grayscale di `<P>/images/derived/`, `href="../images/derived/<file>"`. Alt text deskriptif diambil dari `image_review.json` → `handoff.alt_text` dan ditulis ke `Shape.AlternativeText` pada langkah finishing COM (6.7); verifikasi `descr="…"` pada `ppt/slides/*.xml`.
8. Nomor slide: `NN / total` sebagai teks Slide-local (owner memakai teks, bukan field).

Build:

```bash
.venv-presentation/Scripts/python.exe skills/presentation-deck/runtime/presentation.py check <P>
.venv-presentation/Scripts/python.exe skills/presentation-deck/runtime/presentation.py export <P> --output <P>/engineering/<Nama>_raw_v<k>.pptx --native-data
.venv-presentation/Scripts/python.exe skills/presentation-deck/runtime/presentation.py finalize <P>
```

### 6.6 Pilot slide 1–3 / First-three-slides pilot

ID — Engineer hanya membuat slide 1, 2, 3 (urutan asli) + aset, export, finishing COM (6.7), render native, ukur. Main membuka setiap render (overview → crop → overview), menilai pesan, arah visual, tipografi, spasi, keterbacaan, foto, editabilitas, dan originalitas (6.10 pada draft), lalu menulis `<A>/first_three_slides_review.md` berisi PASS/REVISE/BLOCKED per slide, hash sumber, path render, jenis bukti. Simpan keputusan ke memori bersama (`put`). **Slide 4+ hanya setelah PASS tiga slide.** REVISE → Engineer yang sama memperbaiki → review ulang.
EN — Engineer authors slides 1–3 only; Main inspects every render, records PASS/REVISE/BLOCKED with hashes and evidence, saves the decision to shared memory; slides 4+ only after PASS.

### 6.7 Finishing COM: pola placeholder dan tema / COM finishing pass (verified 2026-10-14)

ID — Runtime tidak menulis pattern fill. Setelah setiap export, jalankan di PowerShell (PowerPoint harus terpasang). Skrip menyetel accent5/accent6 tema (hanya bila tidak dirujuk shape; cek dulu dengan `grep -c 'schemeClr val="accent5"' ppt/slides/*.xml` = 0), lalu pola pada semua picture placeholder di layout. Hasil XML: `<a:pattFill prst="ltUpDiag"><a:fgClr><a:schemeClr val="accent5"/></a:fgClr><a:bgClr><a:schemeClr val="bg2"/></a:bgClr></a:pattFill>` — identik dengan langkah UI owner.
EN — Run after every export; it writes exactly what the owner's Format Shape step writes.

```powershell
param([Parameter(Mandatory=$true)][string]$Path, [string]$Accent5 = '5E5E5A', [string]$Accent6 = 'D9D7D0', [string]$Prompt = 'Drop photo here')
function BGR([string]$hex) { [int]('0x' + $hex.Substring(4,2) + $hex.Substring(2,2) + $hex.Substring(0,2)) }
$app = New-Object -ComObject PowerPoint.Application
$deck = $app.Presentations.Open((Resolve-Path -LiteralPath $Path).Path, 0, 0, 0)
$scheme = $deck.SlideMaster.Theme.ThemeColorScheme
$scheme.Colors(9).RGB = BGR $Accent5    # msoThemeAccent5  -> "Dark Gray, Accent 5"
$scheme.Colors(10).RGB = BGR $Accent6   # msoThemeAccent6  -> hairline
$n = 0
foreach ($layout in $deck.SlideMaster.CustomLayouts) {
  foreach ($shape in $layout.Shapes) {
    $ph = $null; try { if ($shape.Type -eq 14) { $ph = [int]$shape.PlaceholderFormat.Type } } catch {}
    if ($ph -eq 18) {                                  # ppPlaceholderPicture
      $shape.Fill.Patterned(22)                        # msoPatternLightUpwardDiagonal = "Diagonal stripe: light upward"
      $shape.Fill.ForeColor.ObjectThemeColor = 9       # msoThemeColorAccent5     = "Dark Gray, Accent 5"
      $shape.Fill.BackColor.ObjectThemeColor = 16      # msoThemeColorBackground2 = "White, Background 2" (lt2 = paper)
      $shape.Line.Visible = 0
      try { $shape.TextFrame.TextRange.Text = $Prompt } catch {}   # prompt opsional; verifikasi pada render
      $n++
    }
  }
}
$deck.Save(); $deck.Close(); $app.Quit()
"patterned picture placeholders: $n"
```

Alt text (dalam sesi COM yang sama, sebelum `Save`): untuk setiap slide, shape `Type -eq 14` dengan `PlaceholderFormat.Type -eq 18` dan `ContainedType -eq 13`, set `$shape.AlternativeText = <handoff.alt_text slot itu>` (peta slot → slide dari `image_review.json`). Verifikasi `grep -o 'descr="[^"]*"' ppt/slides/*.xml` setelah unzip.

Setelah finishing: `delivery-check`, render, ukur, dan semua receipt dihitung dari **file hasil finishing** (hash baru). Simpan sebagai `<P>/exports/<Nama>_<N>_Slides_v<k>.pptx`.

```bash
.venv-presentation/Scripts/python.exe skills/presentation-deck/runtime/presentation.py delivery-check <P>/exports/<Nama>_<N>_Slides_v<k>.pptx
powershell -File skills/presentation-deck/runtime/render_powerpoint.ps1 -InputPath <deck> -OutputDirectory <P>/engineering/v<k>-native-render
powershell -File <P>/engineering/inspect_native.ps1 -InputPath <deck> -ReportPath <P>/engineering/v<k>-native-text.json -RenderDir <P>/engineering/v<k>-native-render-1920
```

Pengukuran wajib 0 `text-exceeds-native-frame`, 0 `off-canvas-text`, nomor slide benar, kanvas 720 × 405 pt.

### 6.8 Foto / Photos (`PPTX_IMAGE_SELECTION_POLICY.md`)

ID — Ledger `<P>/images/image_review.json` (schema v2) + `<P>/images/image_sources.json`. Engineer mencari (Unsplash/Pexels/web, browser tersembunyi, Firecrawl bila berguna; tanpa AI generation), mengembalikan lembar kandidat per slot. Main membuka kandidat dan merekam verdict `accept`/`reject` (huruf kecil) dengan temuan tone, content, purpose terpisah; `visual_evidence` objek dengan path relatif ke `images/`, `asset_sha256`, `placement_sha256` dari `placement_digest`. Dua ronde ditolak pada satu slot → Main mencari sendiri dan memberi handoff (slide, frame, crop, fokus). Setelah render final: `final_review` per slot dengan screenshot, `deck_sha256`, `native_picture_editable: true`, `native_picture_evidence`. Credit di `image_sources.json`, `source_record_sha256` via `json_digest`.
EN — Engineer searches, Main accepts/rejects each candidate with separate tone/content/purpose findings; Main takes over after two rejected rounds per slot; final review binds screenshot and deck hash.

```bash
python scripts/design_brain_pptx_image_review.py <P>/images/image_review.json --stage progress
python scripts/design_brain_pptx_image_review.py <P>/images/image_review.json --stage handoff
python scripts/design_brain_pptx_image_review.py <P>/images/image_review.json --stage final
```

### 6.9 Deck penuh dan review / Full deck and review

ID — Setelah pilot PASS, Engineer membuat slide 4+ dalam arah yang disetujui (komposisi bervariasi, bukan tiga slide pilot sebagai scaffold), export, finishing, render, ukur. Main meninjau 20 render satu per satu dan menulis `<A>/full<N>_review.md` (tabel per slide: verdict + temuan, foto, chrome, originalitas), memberi brief perbaikan `<A>/main-engineer-brief-repair-v<k>.md`; loop sampai 0 defect. Versi raw di `engineering/`, versi final di `exports/`.
EN — After the pilot passes, the Engineer authors the rest; Main reviews every slide render, writes the review, briefs repairs to the same Engineer, loops to zero defects.

Gate keseimbangan (wajib sebelum review Main, aturan owner 2026-10-15) / Balance gates (required before Main review):

```bash
python skills/presentation-deck/runtime/design_brain_pptx_group_align_check.py <P>/exports/<deck>.pptx --panel <N-cover>:<x0>:<x1> --exclude-pictures <N-cover> --json <P>/engineering/<stage>-v<k>-group-align.json
python skills/presentation-deck/runtime/design_brain_pptx_visual_balance.py <P>/engineering/<stage>-v<k>-native-render --side 48 --tol 2 --ignore <N-cover>:0:0:<x-photo>:540 --left <N-cover>:<x-block> --right <N-cover>:<gap-panel> [--tol-slide <N>:<unit>] --json <P>/engineering/<stage>-v<k>-visual-balance.json
```

ID — Gate 1 = uji terima owner pada file: gabungan frame semua bentuk tiap slide harus terpusat (Align Center + Align Middle tidak menggeser; toleransi 0,05 pt). Gate 2 = tepi ter-render (ambang 8, hairline terhitung): celah atas = celah bawah (±2) dan sisi 48 (±2); `--tol-slide` mencatat kelonggaran per slide yang terdokumentasi (mis. `14:4` untuk padding chart-space PowerPoint). Keduanya harus PASS di semua slide. Bila keduanya beda > 2 unit pada satu slide, penyebabnya frame yang tidak rapat ke isi (mis. chart dengan padding internal): rapatkan frame/isinya, jangan ambil tengah. Perbaikan posisi = geser blok utuh dengan satu offset; bukan membesarkan, bukan mengubah jarak dalam. Skrip gate standar ada di plugin (`skills/presentation-deck/runtime/`, jalankan dengan interpreter runtime; `--self-check` membuktikan gate itu sendiri); jangan salin ke proyek. Salinan asal di `output/Fathom_20261015/analysis/main-group-align-check.py` dan `main-visual-balance.py` hanya arsip.
EN — Gate 1 is the owner's acceptance test on the file: the union of all shape frames on each slide must be centred (Align Center + Align Middle would not move it; tolerance 0.05 pt). Gate 2 measures rendered extents (threshold 8, hairlines count): gap above = gap below (±2) and sides 48 (±2); `--tol-slide` records a documented per-slide allowance (for example `14:4` for PowerPoint chart-space padding). Both must PASS on every slide. If they disagree by more than 2 units on a slide, a frame is not tight to its rendered content (for example a chart with internal padding): tighten it, never split the difference. A placement repair is one offset for the whole slide block; never enlarge or respace. The standard gate scripts live in the plugin (`skills/presentation-deck/runtime/`, run with the runtime interpreter; `--self-check` proves the gate itself); do not copy them into the project. The originals in `output/Fathom_20261015/analysis/` are archive only.

### 6.10 Inspeksi visual (manifest) / Visual inspection manifest

```bash
python scripts/design_brain_visual_inspect.py prepare --image <render>/slide-001.png --artifact <deck> --frame-id slide-001 --output-dir <P>/engineering/v<k>-views --manifest <P>/engineering/v<k>-visual-inspection.json   # ulangi untuk setiap slide
python scripts/design_brain_visual_inspect.py crop --manifest <manifest> --frame-id slide-001 --view-id overview --box x1 y1 x2 y2 --name <detail-name>
python scripts/design_brain_visual_inspect.py verify --manifest <manifest> --artifact <deck> --stage final --json
```

Manifest: `checks[]` (satu pertanyaan kritis per frame), `reviews[]` role `engineer` dan `main` dengan `actual_views` kronologis (overview → detail → overview, `viewed_at` naik, `tool: host_image_tool`), `main_approval` hanya oleh Main setelah membuka bukti sendiri. Hash artefak berubah → inspeksi ulang.

### 6.11 Originalitas layout / Layout originality (`PPTX_LAYOUT_ORIGINALITY_POLICY.md`)

```bash
python scripts/design_brain_pptx_layout_audit.py extract <deck> --deck-id <id> --output <A>/<id>-fingerprint.json
python scripts/design_brain_memory_adapter.py --actor main search "layout_case"      # ambil fingerprint deck terdahulu dari evidence pointer
python scripts/design_brain_pptx_layout_audit.py compare <A>/<id>-fingerprint.json --previous <prev1.json> --previous <prev2.json> --output <A>/<id>-layout-comparison.json
python scripts/design_brain_pptx_layout_audit.py verify <A>/<id>-layout-comparison.json
```

Main membuka pasangan render yang ditandai dan memutuskan; 0 komposisi identik. Ganti warna/teks/foto/ukuran saja bukan originalitas.

### 6.12 Design-system receipt

Tulis `<P>/design-system-receipt.json` (kunci lengkap lihat `output/Ruled-Margin_20261013/design-system-receipt.json`; `components` wajib memuat kata: button, card, navigation, header, footer, cta, placeholder; token warna/tipe/spasi; states; placeholderRules; sourceHygiene; layouts; artifactEvidence dengan hash deck final).

```bash
python scripts/design_brain_design_system_check.py --receipt <P>/design-system-receipt.json --json
```

### 6.13 Post-build receipt dan gate penutup / Post-build receipt and closing gates

ID — `<A>/main-human-post-build.json` (= `<P>/completion-receipt.json`): `finalStatus, reviewer, source{path,sha256}, templatesBuilt, designSystemsBuilt, auditPasses{pass1,pass2,pass3}, batchSimilarity, repairCycles, remainingIssues, visualVerificationStatus, evidence[], limitations[], visualInspectionManifests[{path absolut, sha256}], cognitionComparison, layoutOriginality{…}`. Lalu jalankan berurutan (buat skrip resumable seperti `output/Ruled-Margin_20261013/analysis/main-close-gates.py`):

```bash
python skills/presentation-deck/runtime/design_brain_pptx_group_align_check.py <deck> --panel <N-cover>:<x0>:<x1> --exclude-pictures <N-cover> --json <P>/engineering/final-group-align.json   # gate keseimbangan 6.9, diulang pada export final
python skills/presentation-deck/runtime/design_brain_pptx_visual_balance.py <render-final> --side 48 --tol 2 --ignore <N-cover>:0:0:<x-photo>:540 --left <N-cover>:<x-block> --right <N-cover>:<gap-panel> --json <P>/engineering/final-visual-balance.json
python scripts/design_brain_design_system_check.py --receipt <P>/design-system-receipt.json --json
python scripts/design_brain_pptx_image_review.py <P>/images/image_review.json --stage final
python scripts/design_brain_visual_inspect.py verify --manifest <manifest> --artifact <deck> --stage final --json
python scripts/design_brain_build_session.py register-build --session <A>/main-session --template-id <id> --artifact <deck> --fingerprint <A>/main-final-fingerprint.json --json
python scripts/design_brain_build_session.py register-design-system --session <A>/main-session --template-id <id> --receipt <P>/design-system-receipt.json --json
python scripts/design_brain_build_session.py register-post-build --session <A>/main-session --template-id <id> --receipt <A>/main-human-post-build.json --json
python scripts/design_brain_build_session.py lock-template --session <A>/main-session --template-id <id> --json
python scripts/design_brain_build_session.py finalize --session <A>/main-session --json
python scripts/design_brain_reference_usage_gate.py record --candidate-brand-name "<Nama>" --reference-ids <ref-ids> --reference-mode single --template-id <id> --template-type "PowerPoint presentation template" --product-family presentation_deck --niche "<niche>" --write-receipt --receipt-output <A>/main-reference-usage-record.json --json
python scripts/design_brain_build_session.py register-reference-usage-record --session <A>/main-session --template-id <id> --receipt <A>/main-reference-usage-record.json --json
python scripts/design_brain_build_session.py verify-final --session <A>/main-session --json
python scripts/design_brain_post_build_audit.py --build-dir <P> --session <A>/main-session --expected-templates 1 --design-system <P>/design-system-receipt.json --cognition-receipt <A>/main-cognition.json --require-cognition --visual-inspection <manifest> --visual-artifact <deck> --output-dir <A>/main-post-build --mode presentation --product-family presentation_deck --strict --json
```

Semua harus READY/PASS sebelum kata "selesai".

### 6.14 Salinan tanpa foto / Photo-less copy (verified 2026-10-14)

ID — Pada PowerPoint, `Delete()` pada picture placeholder berisi foto hanya membuang fotonya; placeholder kosong berpola tetap ada (persis versi jual owner). Jalankan pada salinan deck final:
EN — Deleting a filled picture placeholder via COM removes only the picture; the patterned empty placeholder stays.

```powershell
param([Parameter(Mandatory=$true)][string]$Source, [Parameter(Mandatory=$true)][string]$Target)
Copy-Item -LiteralPath $Source -Destination $Target
$app = New-Object -ComObject PowerPoint.Application
$deck = $app.Presentations.Open((Resolve-Path -LiteralPath $Target).Path, 0, 0, 0)
$removed = 0
foreach ($slide in $deck.Slides) {
  $filled = @(); foreach ($s in $slide.Shapes) { try { if ($s.Type -eq 14 -and [int]$s.PlaceholderFormat.Type -eq 18 -and [int]$s.PlaceholderFormat.ContainedType -eq 13) { $filled += $s } } catch {} }
  foreach ($s in $filled) { $s.Delete(); $removed++ }   # hanya foto yang hilang; placeholder tetap
}
$deck.Save(); $deck.Close(); $app.Quit()
"pictures removed: $removed"
```

Verifikasi: 0 `<p:pic>` di slide, jumlah `<p:ph type="pic"` tetap, `ppt/media/` kosong, render menunjukkan pola; `delivery-check` PASS.

### 6.15 Catatan dan laporan akhir / Records and final report

```bash
python scripts/design_brain_memory_adapter.py --actor main put --file <A>/main-memory-<topic>.json --expected-revision <rev> --operation-id <uuid>   # task, pilot, full-deck, layout_case
python scripts/design_brain_memory_adapter.py --actor main read <record-id>
python scripts/design_brain_build_record.py --template-name "<Nama>" --template-type "PowerPoint presentation template" --niche "<niche>"
python scripts/design_brain_reflect.py --task "…" --feedback "…" --went-wrong "…" --lesson "…" --rule "…"   # setiap koreksi owner
```

Laporan akhir ke owner (singkat, Indonesia): path dua PPTX + SHA-256; path `product-metadata.csv` dan `product-metadata.json` + hasil pemeriksaan kesamaan keduanya (6.16); Templates built; Design systems built; Audit Pass 1 (originalitas), 2 (design system/source hygiene), 3 (visual/layout QA); Batch similarity (N/A untuk satu template); Repair cycles; Remaining issues; Visual verification (render native, pengukuran); Final status READY / READY_WITH_LIMITATIONS / REVISE_REQUIRED / BLOCKED. Tidak ada paket, tidak ada guide, tidak ada preview kit.

### 6.16 Metadata listing produk / Product listing metadata — WAJIB DI KEDUA MODE

ID — Setelah **dua PPTX final** lolos gate, Main membuat **tepat dua file metadata terpisah dari PPTX** pada `<P>/exports/`: `product-metadata.csv` (review manusia) dan `product-metadata.json` (otomatisasi). Berlaku **baik mode kalibrasi maupun produksi**, tanpa perlu frasa aktivasi produksi. Ini metadata **listing marketplace**, bukan metadata teknis internal PowerPoint; tidak disisipkan ke PPTX.
EN — After both final PPTX pass their gates, Main must produce exactly two separate marketplace-listing metadata files in `<P>/exports/`, for manual review (CSV) and automation (JSON). This obligation applies in calibration and production alike; it does not activate packaging or modify internal PPTX document properties.

Kontrak data / Data contract (satu produk = satu record):
1. `title` — judul produk yang natural, deskriptif, unik secara wajar, dan SEO-friendly; dasarkan pada niche, tampilan, isi, dan kegunaan deck final, bukan hanya nama file. Hindari keyword stuffing, klaim palsu, atau nama brand buatan yang tidak terdapat pada desain.
2. `description` — deskripsi listing orisinal, informatif, dan ringkas; jelaskan manfaat, gaya visual, jumlah slide, format/editabilitas dan fitur **hanya bila dibuktikan pada PPTX final**. Jangan menjanjikan format lain, lisensi aset, atau fitur yang belum ada.
3. `category` — **satu kategori marketplace yang valid** sesuai marketplace tujuan pada intake #2; jangan mengarang taksonomi resmi atau memakai kategori generik bila kategori aktual belum diketahui.
4. `tags` — **tepat 15 keyword/tag** yang relevan dengan subjek, gaya visual, niche, kegunaan, dan tipe aset; unik (case-insensitive), tidak repetitif, tidak berisi klaim/brand tidak relevan, disusun menurut prioritas penelusuran.

Format wajib / Required serialization:
- **CSV:** UTF-8; header **`title,description,category,tags`**, diikuti **tepat satu record produk**. Kolom `tags` berisi **15 tag dipisahkan koma dalam satu sel CSV** dengan quoting/escaping CSV standar; setiap tag tidak boleh mengandung koma internal agar parsing tidak ambigu. Tanda koma, kutipan, dan newline pada description juga harus di-escape sesuai CSV.
- **JSON:** UTF-8, **satu objek valid** dengan kunci tepat `title`, `description`, `category`, `tags`; `tags` adalah **array berisi tepat 15 string**. Nilai ketiga field lain adalah string (bukan `null`).
- **Satu sumber data:** susun record listing satu kali dari PPTX final, lalu serialisasi ke kedua format. Setelah parsing CSV, pisahkan kolom `tags` pada koma; bandingkan ke array JSON secara berurutan beserta `title`, `description`, `category`. Harus **identik**; jangan sekadar membandingkan tampilan teks/byte.
- **Review/revisi:** revisi pada CSV harus diikuti regenerasi JSON (atau sebaliknya) dari record yang telah disetujui. Jangan kirim versi yang tidak sinkron. Pastikan encoding/parsing valid, 4 field lengkap, 15 tag unik, dan tidak ada placeholder/dummy claim.
- **Source dan blocker:** Main membaca/menilai **PPTX hasil final** (bukan metadata `core.xml`, draft, atau referensi). Bila kategori marketplace belum dapat dipastikan, selesaikan intake/klasifikasi yang kurang dahulu; jangan membuat file seolah final dengan kategori tebakan. Jika validasi gagal, status deliverable **REVISE_REQUIRED**, bukan READY.
- **Handoff:** kedua file harus benar-benar ada dan terbaca di `exports/`, disebutkan bersama path dua PPTX pada laporan 6.15. Tidak ada upload/publish otomatis; tidak ada ZIP/paket produksi dalam kalibrasi.

---

## 7. Jalur produksi / Production track — **NONAKTIF / INACTIVE**

ID — Aktif hanya setelah owner mengatakan persis `kita mulai jalur produksi`. Langkah di bawah terbaca dari artefak owner; detail finishing PowerPoint dan alat buatan owner akan dilengkapi setelah owner menjelaskan/membawa alatnya. Jangan menjalankan bagian ini dalam mode kalibrasi.
EN — Active only after the owner says exactly `kita mulai jalur produksi`. Steps are reconstructed from the owner's artefacts; the owner's own tool and the PowerPoint finishing details are pending. Do not run this in calibration mode.

1. Finishing PowerPoint (owner): ±45 menit, beberapa kali simpan, guide tengah kanvas, grid 1/12 in. **Detail menyusul dari owner.**
2. Ekspor JPG tiap slide 960 × 540 ke `JPG/Slide1…N.jpeg`.
3. Versi jual tanpa foto (6.14) → `PPTX/Presentation.pptx`; salinan sama untuk `GSL/` (impor Google Slides oleh pembeli).
4. Keynote: impor PPTX versi jual di Keynote (owner memakai Keynote 15.3.1) → `KEYNOTE/Presentation.key`.
5. Preview marketplace: Photoshop, `Preview 1.jpg` 4500 × 3000 @300 dpi (mosaik 9 slide + badge format), `Preview 2.jpg` 1370 × 913 (mosaik 16 slide); satu komposisi dipakai untuk tiga varian.
6. Metadata listing **wajib** dibuat melalui bagian 6.16 sebagai dua file terpisah `product-metadata.csv` + `product-metadata.json` (title, description, category, tepat 15 tags), juga dalam mode kalibrasi. Saat jalur produksi aktif, `deskripsi dan tag.txt` dapat dibuat sebagai turunan legacy dari metadata yang sama (bukan sumber kebenaran berbeda), disertai `Read Me.txt` (fitur + font + link Google Fonts) dan `Help File Presentation.pdf` (panduan generik; perbarui font agar sesuai deck).
7. Struktur paket: `PPTX/`, `KEYNOTE/`, `GSL/`, `JPG/`, `Referensi/` (internal, tidak dijual).
8. Alat konversi buatan owner: **placeholder — sebagian langkah konversi dikerjakan alat owner, bukan AI** (jawaban owner 2026-10-14).

---

## 8. Checklist selesai / Definition of done (mode kalibrasi)

- [ ] Intake dijawab; nama lolos name check; sesi build dimulai.
- [ ] Studi referensi + insight tersimpan; cognition strict PASS; simulation PASS; plan + fingerprint terdaftar; audit-layout dijalankan.
- [ ] `spec_lock` structured; master hanya latar; `Default` kosong; `Photo Layout NN` hanya picture placeholder; teks sesuai intake #3.
- [ ] Pilot 1–3 PASS tercatat (`first_three_slides_review.md` + memori) sebelum slide 4.
- [ ] Foto: ledger progress/handoff/final PASS; semua slot diterima Main; monokrom; alt text.
- [ ] Finishing COM dijalankan pada export final: pola `ltUpDiag` accent5/bg2 pada semua picture placeholder; tema accent5/accent6 benar.
- [ ] `delivery-check` PASS; render native semua slide; pengukuran 0 overflow, nomor slide benar.
- [ ] Gate keseimbangan PASS di semua slide: uji group + Align Center/Middle tidak bergeser (frame, 0,05 pt) dan tepi ter-render seimbang (±2); perbaikan = geser blok utuh, bukan membesarkan.
- [ ] Manifest inspeksi visual: semua frame, review engineer + main, `main_approval` accept.
- [ ] Originalitas: extract/compare/verify + putusan Main; 0 identik.
- [ ] Design-system receipt PASS; post-build receipt; gate penutup semua READY; post-build audit strict PASS.
- [ ] Dua PPTX final di `exports/` (dengan foto; tanpa foto) + SHA-256; tidak ada paket.
- [ ] Dua metadata listing di `exports/`: `product-metadata.csv` (header + satu record) dan `product-metadata.json` (objek valid), masing-masing punya `title`, `description`, `category`, dan **tepat 15 tags**; dibuat sesudah finalisasi kedua PPTX (6.16).
- [ ] CSV/JSON berhasil dibaca ulang, 4 field dan urutan 15 tags **identik**, tanpa duplikat/klaim tidak terbukti; kategori sesuai marketplace. Jika gagal, status **REVISE_REQUIRED**.
- [ ] Memori bersama diperbarui (task, pilot, full, layout_case); build record; reflection untuk setiap koreksi.
- [ ] Laporan akhir sesuai 6.15 mencantumkan kedua PPTX dan kedua metadata berikut status validasinya.

---

## 9. Referensi cepat / Quick reference

| Kebutuhan / Need | Path |
|---|---|
| Studi standar owner | `output/Owner-Standard-Study_20261014/OWNER_WORK_PATTERN_STUDY.md` |
| Deck owner (standar) | `Referensi dari User/Marketing Growth Plan Presentation/Presentation.pptx` |
| Contoh proyek lulus gate (desain bukan standar owner) | `output/Ruled-Margin_20261013/` (`spec_lock.md`, `svg_output/`, `analysis/`, `engineering/inspect_native.ps1`, `analysis/main-close-gates.py`, `analysis/main-final-receipts.py`) |
| Role prompt Engineer | `.design-brain/runtime/HOST_DESIGN_PRODUCTION_SPECIALIST.md`; definisi Claude Code `agents/general-design-production-engineer.md` |
| Protokol inspeksi | `.design-brain/VISUAL_INSPECTION_PROTOCOL.md` |
| Memori bersama | `.design-brain/LOCAL_MEMORY_POLICY.md`; record `owner-standard-marketing-growth-plan-20261014`, `policy-pptx-output-only-calibration-20261014` |
| Kebijakan PPTX | `skills/presentation-deck/workflows/PPTX_*.md`, `native.md`, `generate-pptx.md` |
| Kontrak SVG | `skills/presentation-deck/design/native/pptx-structure-interface.md`, `semantic-svg.md`, `native-data-interface.md` |
| Runtime | `skills/presentation-deck/runtime/presentation.py` (`doctor, init, check, export --native-data, finalize, delivery-check`), `render_powerpoint.ps1` |
| Gate keseimbangan (6.9, 6.13) | `skills/presentation-deck/runtime/design_brain_pptx_group_align_check.py` (frame, 0,05 pt), `design_brain_pptx_visual_balance.py` (render, ±2); keduanya punya `--self-check` |
