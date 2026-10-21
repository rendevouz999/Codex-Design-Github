> **HISTORICAL DONOR BASELINE 2.8.0 (2026-10-17).** Not proof that current Codex-Design 2.9.0 reconciliation passed. See the 2026-10-21 reconciliation report for current source/test evidence.

# Codex-Design-Github — implementasi efisiensi token

Baseline source: `a7c3cb6594ce7ecbd71ca9ebf5ceb4852c5aef36`, versi sumber 2.8.0.
Branch lokal: `improvement/token-efficiency-20261017`.
Scope disetujui pemilik 17 Oktober 2026. Owner verification berhasil; tidak ada password/verifier pribadi dalam perubahan atau paket.

## Perubahan langsung pada pemilik modul

- Memory adapter: search/list/history summary-first, `--full` eksplisit dan `read` tetap lengkap; origin/conflict/coverage/review status dipertahankan. Local browse full projection dipakai ulang untuk menghilangkan pembacaan kedua per record legacy. Filter/pagination multi-origin masih mempertahankan scan untuk coverage; ini bukan indeks semantic baru atau klaim seluruh biaya I/O sudah hilang.
- Context packet: stage planning/authoring/review/delivery/diagnostic; presentation stage memakai workflow pemiliknya, tidak selalu seluruh katalog generic. Mode dual meliputi native dan web; path kondisi dideduplikasi; label tidak lagi mengaku telah membaca file/jurnal.
- Hook: field root dan daftar path utuh, tidak dipotong pada batas kata; narasi modality-specific hanya bila relevan. Root dengan spasi didukung.
- Authoring/delivery: Main atau satu Engineer dapat mengerjakan unit; Main tetap creative direction dan final review. Quick tidak otomatis mengulang seluruh deck setelah compaction. Calibration hanya menyerahkan PPTX lengkap, tetap menyimpan evidence internal.
- Visual QA: reuse observasi frame hanya dengan manifest original yang accepted/current, context sama, render aktual sama, view/questions sama, dependency PPTX sama. Resolver memakai urutan presentation→relationship, bukan mengasumsikan ordinal selalu nama slideN.xml. Shared/unknown/metadata changes menginvalidasi secara konservatif. External dependency atau struktur tidak dikenali menonaktifkan reuse. Final approval selalu baru, provenance dan timestamp original tidak dipalsukan.

## Batas kualitas dan cakupan

Tidak mengurangi effort/model pilihan pemilik, jumlah slide yang diminta, originality, native editability, first-three review atau final visual approval. Engine export/primitives existing dipertahankan; tidak ada subproject atau mesin paralel baru. Tidak ada deployment Windows, reload plugin atau push ke GitHub pada tahap ini.

Ini implementasi pada baseline source yang diperiksa. File yang hanya disebut dalam manifest 2.9.0 tidak direka ulang dan versi terpasang di Windows belum dibuktikan. Persentase hemat token dan kemampuan menyelesaikan satu sesi produksi belum diukur; hasil test lokal hanya membuktikan perilaku yang dinyatakan per kasus.

## Pemeriksaan awal yang telah dijalankan

- Projection regression: sebelum perubahan, kasus summary default gagal karena body lengkap hadir; sesudah perbaikan suite 21 kasus lulus (termasuk regresi adapter existing).
- Loading regression: tiga kasus awal gagal sebelum perbaikan; setelah perbaikan dan penambahan stage check, 4 kasus lulus. Test long-root diperbaiki agar menunjuk direktori nyata dengan spasi, bukan root nonexistent.
- Visual reuse: 4 synthetic cases lulus; tidak merupakan review visual produk nyata.
- Combined token-efficiency suite: 29 kasus lulus.
- Local memory suite: 15 kasus lulus.
- Node syntax hook: lulus.
- Router smoke: 160/162 lulus; dua package-sanity failures menunjuk file yang tidak ada sejak baseline Git, bukan file yang dihapus oleh perubahan ini.

File baseline yang hilang:

- `.design-brain/REFERENCE_INSIGHT_JOURNAL.md`
- `.design-brain/REFLECTION_LOG.md`
- `reports/brain-design-web-deck-integration/WEB_DECK_INTEGRATION_RECEIPT.md`
- `reports/brain-design-web-deck-integration/web-deck-capability-boundary.md`

`git ls-tree` pada baseline tidak memuat keempat path tersebut. Tidak dibuat jurnal/receipt palsu dan tidak dilonggarkan assertion package-sanity agar terlihat lulus.

## Status

Implementasi scope source dan pemeriksaan terarah selesai. Runtime/checkpoint/repair telah digabung pada pemilik modul existing. Baca RUNTIME-IMPLEMENTATION.md untuk kontrak lengkap. Belum terpasang/deployed di Windows dan belum dipublikasikan ke GitHub.

Hasil pemeriksaan akhir setelah perbaikan review:
- Token-efficiency: 32 kasus PASS.
- Runtime continuity/repair: 25 kasus PASS.
- Visual existing: 35 kasus PASS.
- Local memory: 15 kasus PASS (tidak berubah setelah run itu).
- Runtime smoke: 22 checks PASS dalam snapshot terisolasi.
- Post-build smoke: 35 checks PASS dalam snapshot terisolasi.
- Router: 160/162 PASS, dua kegagalan baseline package-sanity tetap dilaporkan.
- Node syntax kedua hook dan git diff --check PASS.
Jangan menjumlahkan angka suite sebagai kasus unik; sejumlah regresi existing tercakup lagi dalam suite gabungan.

Review menemukan tiga kekurangan implementasi awal dan semuanya diperbaiki dengan reproduksi gagal lalu lulus: pemanggilan stage helper pada build_packet belum terhubung; cross-slide relationship dapat lolos dependency key; exact legacy revision hilang pada jalur read. Versi akhir sudah menghubungkan CLI sebenarnya, menolak reuse untuk cross-slide dependencies, dan mempertahankan exact revision beserta origin lokalnya.

## Integritas baseline dan batas aktivasi

Native integrity baseline memiliki 23 ketidakcocokan hash sebelum perubahan ini. Pemeriksaan representasi menunjukkan 19 cocok persis jika LF diubah menjadi CRLF; empat lainnya tidak cocok melalui normalisasi LF/CRLF/BOM yang diperiksa:
- workflows/stages/web-image-review.md
- workflows/PPTX_IMAGE_SELECTION_POLICY.md
- workflows/PPTX_FIRST_THREE_SLIDES_REVIEW.md
- workflows/PPTX_LAYOUT_ORIGINALITY_POLICY.md

Tidak menyimpulkan keempat file rusak atau aman hanya dari mismatch. Tidak merebase semua hash diam-diam. Hanya hash tiga critical files yang benar-benar diubah oleh task ini diperbarui, dengan baseline/result hash dicatat dalam OWNED-INTEGRITY-CHANGES.json. Upstream sourceSha256 pada provenance donor dipertahankan. Dua dari tiga file itu sebelumnya termasuk mismatch CRLF; perubahan baru kini memiliki identity result tersendiri.

THIRD_PARTY_NOTICES.md untuk ikon memang tidak ada sebagai loose tracked file, tetapi ditemukan di icons.tar.gz dan hash cocok dengan manifest; jangan menyebut aset ini hilang. Unpack activation existing tetap menjadi pemiliknya.

Karena batas baseline tersebut dan Windows belum diuji, paket perubahan ini bukan klaim plugin terpasang/production-ready atau native integrity keseluruhan PASS. Jangan mengganti file dari paket 2.9.0 yang berbeda secara buta. Baseline paket perubahan adalah a7c3cb6; manifest perubahan menyertakan hash sebelum/sesudah untuk rekonsiliasi.

## Pembatasan desain yang sengaja dipertahankan

Guide penuh pada fresh context masih merupakan standar pemilik. Penghematan diterapkan pada tahap berikutnya, discovery summaries, pilihan referensi, resume dan reuse evidence yang sah; tidak diklaim menghilangkan seluruh initial-context cost. Memory scan multi-origin masih konservatif untuk coverage. Dependency visual juga sengaja konservatif: perubahan metadata/shared parts dapat menuntut review lebih banyak, daripada menyatakan unchanged tanpa bukti.


## Tambahan owner — tanggal konten, 17 Oktober 2026

PRESENTATION_TEMPLATE_GUIDE.md bagian 4.4.1 kini menetapkan tahun konten contoh/fiktif mulai 2046, kronologi konsisten, pengecualian untuk fakta/instruksi tanggal eksplisit, serta pemisahan dari timestamp sistem. Bagian 4.2 line spacing tidak diubah. Ini aturan authoring dan pemeriksaan konten; tidak diklaim sebagai validator otomatis baru.

Klarifikasi owner setelah laporan awal: dua laporan web sengaja dihapus untuk fokus PPTX; jangan dipulihkan. Kedua jurnal telah diberikan sebagai lampiran, tetapi belum ditambahkan ke clone atau paket publik. Referensi manifest lama masih perlu diselaraskan. Ada pengerjaan Windows terpisah; gabungkan berdasarkan baseline hash, jangan replace seluruh folder.
