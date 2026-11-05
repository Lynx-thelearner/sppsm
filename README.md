# SPPSM (Sistem Pengelolaan & Penjemputan Sampah Mandiri)

Proyek Akhir untuk tugas kampus.
Wajarnya ini pakai uv [uv](https://docs.astral.sh/uv/) tapi bisa juga pakai pip (nanti aku urus)

---

# Cara install uv

```bash
pip install uv
```

### 1. Clone repository & install dependencies:
```bash
git clone https://github.com/Lynx-thelearner/sppsm.git
cd sppsm
uv sync
```

### 2. Jalankan aplikasi:
```bash
uv run sppsm
```

---

## Aturan Kelompok gweh (WAJIB DIBACA!)

Karena kita kerja bareng dalam satu repo, **IKUTI ATURAN INI** biar kodingan kita enggak *conflict*

---

### 1. HARAM Push Langsung ke `main` (`origin main`)
- Branch `main` adalah branch utama yang kodenya harus selalu fix, work, bener, aman, tentram, stabil, dan bisa dijalankan tanpa error.
- **Dilarang** melakukan `git push origin main`.
- Semua perubahan harus masuk lewat fitur **Pull Request (PR)** di GitHub.

---

### 2. 1 Fitur / Entitas = 1 Branch Baru
Jangan pernah ngoding di branch `main`. Selalu buat branch baru setiap kali mau mengerjakan fitur, fungsi, atau entitas baru.

**Format penamaan branch:**
- Fitur baru: `feat/<nama-fitur>`  
  *Contoh:* `feat/login`, `feat/menu-transaksi`, `feat/crud-data`
- Perbaikan bug: `fix/<nama-bug>`  
  *Contoh:* `fix/hitung-total`, `fix/tampilan-tabel`
- Penyesuaian: `refactor/<nama-tugas>`  
  *Contoh:* `refactor/struktur-database`

---

### 3. Selalu Update Branch Sebelum & Sesudah Koding
Sebelum mulai ngetik kode baru, samakan dulu kodemu yang ada di vscode (lokal) yang ada di `main` agar tidak terjadi *merge conflict*:

```bash
# Pindah ke main dan tarik update terbaru dari GitHub
git checkout main
git pull origin main

# Pindah kembali ke branch fiturmu dan gabungkan update dari main
git checkout feat/<nama-fitur-kamu>
git merge main
```

---

### 4. Pesan Commit yang Jelas
Jangan ngasih pesan commit gajelas kek `"update"`, `"fix"`, `"aowkwoak"`, atau `"selesai"`. Gunakan pesan yang menjelaskan apa yang kamu ubah:

- ✅ `git commit -m "feat: tambah validasi password menggunakan pwinput"`
- ✅ `git commit -m "fix: perbaiki urutan kolom pada prettytable transaksi"`
- ❌ `git commit -m "asdasd"`
- ❌ `git commit -m "bisa jalan"`

---

### 5. Tes Sebelum Push
Sebelum kamu melakukan push ke GitHub:
1. Pastikan program kamu jalan tanpa error dengan menjalankan:
   ```bash
   uv run sppsm
   ```
2. Jangan push kode yang sengaja dibiarkan error atau masih setengah jalan tanpa konfirmasi ke tim.

---

### 6. Alur Pull Request (PR) & Code Review
1. Setelah fitur selesai di-push ke branch kamu di GitHub, buka repository di browser.
2. Buat **Pull Request (PR)** dari branch kamu ke branch `main`.
3. Beri deskripsi singkat mengenai apa saja yang baru dibuat/diubah.
4. Chat Diaz buat ngereview, dan nanti bakal di-**Merge** ke brach `main`

---

### 7. Kalau Terjadi *Merge Conflict*!
- *Conflict* adalah hal normal (biasanya terjadi kalau 2 orang mengedit baris kode yang sama di file yang sama).
- **JANGAN** pernah jalankan `git push --force` atau `git push -f`.
- Jika bingung menyelesaikan conflict, **bicarain langsung dengan orang yang mengedit file tersebut**.
- Panggil Diaz njir kalau bingung

---

## Alur Kerja Sehari-hari

Langkah-langkah:

```bash
# 1. Pastikan main kamu update
git checkout main
git pull origin main

# 2. Buat branch baru untuk fitur yang mau dikerjakan
git checkout -b feat/nama-fitur-kamu

# 3. Koding... tes program sampai jalan:
uv run sppsm

# 4. Simpan perubahan ke git
git add .
git commit -m "feat: deskripsi perubahan yang dibuat"

# 5. Push branch kamu ke GitHub (hanya branch kamu, BUKAN main!)
git push -u origin feat/nama-fitur-kamu

# 6. Buka GitHub -> Klik "Compare & pull request" -> Minta review Diaz
```

### Kalau kamu baca ampe akhir

Pada akhirnya yang bener bener penting cuma peraturan nomor 1, 3, 5, 6, 7, yang lainnya opsional, tapi ya bagus kalau semuanya diikutin

---
