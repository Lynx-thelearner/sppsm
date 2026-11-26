# SPPSM (Sistem Pengelolaan & Penjemputan Sampah Mandiri)

Aplikasi *Command Line Interface* (CLI) untuk manajemen penjemputan dan pengelolaan sampah mandiri warga, menghubungkan Warga, Petugas kebersihan, dan Administrator dalam satu sistem terpadu.

Proyek Akhir untuk mata kuliah **Algoritma dan Pemrograman Dasar (APD)**.

---

## Fitur Utama Berdasarkan Role

Sistem ini menerapkan *Role-Based Access Control* (RBAC) dengan 3 peran pengguna:

### 1. Warga
- **Registrasi & Login Mandiri**: Pendaftaran akun warga dengan validasi input yang ketat dan enkripsi password.
- **Pengajuan Penjemputan**: Mengajukan permintaan jemput sampah baru dengan opsi fleksibel: alamat default profil atau alamat penjemputan khusus, beserta catatan deskripsi sampah.
- **Riwayat Penjemputan Real-time**: Memantau perkembangan status penjemputan (`menunggu`, `selesai`, `ditolak`), termasuk informasi tanggal jemput, berat timbangan, dan catatan petugas.

### 2. Petugas Kebersihan
- **Antrean Request**: Melihat daftar seluruh permintaan sampah warga yang siap dijemput (berstatus `menunggu`).
- **Konfirmasi Penjemputan**: Menimbang dan memasukkan berat sampah (kg) serta catatan hasil penjemputan, yang otomatis memperbarui status menjadi `selesai`.
- **Penolakan Request**: Menolak permintaan jika sampah tidak layak/tidak memenuhi ketentuan dengan mencantumkan alasan penolakan yang jelas.

### 3. Administrator
- **Manajemen User (CRUD Penuh)**: Menambahkan akun baru (Warga, Petugas, Admin), melihat data user, memperbarui informasi profil/password, dan menghapus akun.
- **Manajemen Request (CRUD Penuh)**: Memantau seluruh transaksi penjemputan, memperbarui data request (berat, alamat, status, catatan), atau menghapus data request.

---

## Tech Stack & Arsitektur Keamanan

- **Bahasa**: Python 3.13+
- **Database**: SQLite3 (Relasional dengan integritas *Foreign Key* dan `ON DELETE CASCADE`)
- **Keamanan Password**:
  - Hashing menggunakan standar industri **PBKDF2 HMAC SHA-256** dengan *Salt* acak 16-byte (`hashlib` + `secrets`). Password tidak disimpan dalam bentuk *plain text*.
  - Masking input password saat pengetikan menggunakan library `pwinput`.
- **Antarmuka CLI**:
  - `inquirer`: Menu navigasi interaktif berbasis panah keyboard.
  - `prettytable`: Penyajian data tabel yang terstruktur dan rapi.
- **Standar & Kualitas Kode**:
  - Validasi ketat terhadap input teks bebas (mencegah input simbol murni/kosong seperti `!!!!` pada username, nama, alamat, dan catatan).
  - Standarisasi format kode dan linting menggunakan `ruff` (standar PEP 8).

---

## Struktur Direktori Proyek

```text
src/sppsm/
├── main.py        # Entry point utama aplikasi & manajemen sesi login
├── auth.py        # Logika autentikasi (login, register, session)
├── warga.py       # Alur antarmuka dan menu role Warga
├── petugas.py     # Alur antarmuka dan pemrosesan request oleh Petugas
├── admin.py       # Alur antarmuka dashboard Administrator
├── requests.py    # Logika bisnis dan query CRUD data request penjemputan
├── users.py       # Logika bisnis dan query CRUD data user
├── database.py    # Skema SQLite, inisialisasi tabel, dan seeding data awal
└── utils.py       # Helper functions (hashing PBKDF2, verify, clear, enter)
```

---

## Cara Menjalankan Aplikasi

Kamu dapat menjalankan aplikasi ini menggunakan **`uv`** (sangat direkomendasikan) atau menggunakan **`pip` standar bawaan Python**.

### Opsi A: Menggunakan `uv` (Direkomendasikan)

1. **Install uv** (jika belum terpasang):
   ```bash
   pip install uv
   ```

2. **Clone repository & install dependencies:**
   ```bash
   git clone https://github.com/Lynx-thelearner/sppsm.git
   cd sppsm
   uv sync
   ```

3. **Jalankan aplikasi:**
   ```bash
   uv run sppsm
   ```

---

### Opsi B: Menggunakan Python & `pip` Standar

Jika di komputer penguji tidak terpasang `uv`, kamu tetap bisa menjalankannya menggunakan virtual environment standar:

1. **Clone repository:**
   ```bash
   git clone https://github.com/Lynx-thelearner/sppsm.git
   cd sppsm
   ```

2. **Buat & aktifkan virtual environment:**
   - **Linux / macOS:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .venv\Scripts\activate
     ```
     > **Catatan Keamanan (Jika muncul error `running scripts is disabled`):**  
     > Ini adalah proteksi keamanan bawaan PowerShell. Kamu dapat mengizinkan script lokal berjalan secara aman menggunakan standar resmi Microsoft (cukup jalankan sekali):
     > ```powershell
     > Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
     > ```
     > *(Aman karena `-Scope CurrentUser` hanya berlaku untuk akunmu sendiri, dan `RemoteSigned` hanya membolehkan script yang dibuat di komputer lokal sementara script unduhan asing dari internet tetap diblokir).*  
     > **Atau tanpa ubah izin:** Buka terminal **Command Prompt (CMD)** dan jalankan `.venv\Scripts\activate.bat`.

3. **Install dependensi & jalankan:**
   ```bash
   pip install -r requirements.txt
   pip install .
   sppsm
   ```
   *(Alternatif jika tidak ingin build package: cukup `pip install -r requirements.txt` lalu jalankan `python -m sppsm.main`)*

---

## Akun Demo / Dummy untuk Pengujian

Gunakan akun bawaan database berikut untuk mencoba berbagai hak akses (*role*):

| Role | Username | Password | Nama | Keterangan / Hak Akses |
| :--- | :--- | :--- | :--- | :--- |
| **Admin** | `Fysortheguy` | `hafizh123` | Hafizh | Mengelola seluruh data User & Request (CRUD penuh) |
| **Petugas** | `Tomgun` | `tom123` | Tommy | Memproses request jemput (timbang berat/tolak request) |
| **Warga** | `BennyAdventureTeam` | `ben123` | Bennet | Membuat request penjemputan & melihat riwayat |
| **Warga** | `lynxstilllearning` | `lynxlynxy` | Lynx | Akun warga alternatif |
| **Warga** | `kikirakira` | `kiki123` | Kiki | Akun warga alternatif |

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
