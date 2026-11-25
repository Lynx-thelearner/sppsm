import sqlite3

import inquirer
import pwinput
from prettytable import PrettyTable

from .database import get_connection
from .utils import clear, hash_password


# Ambil semua data user dari database
def get_user():
    conn = get_connection()
    try:
        return conn.execute("SELECT * FROM users").fetchall()
    except sqlite3.Error as e:
        print(f"Gagal mengambil data user: {e}")
        return []
    finally:
        conn.close()


# Helper untuk mencetak tabel PrettyTable daftar user
def _tampilkan_tabel_user(users):
    tabel = PrettyTable()
    tabel.field_names = ["ID", "Username", "Nama", "Alamat", "No. Telepon", "Role"]
    tabel.align["Username"] = "l"
    tabel.align["Nama"] = "l"
    tabel.align["Alamat"] = "l"
    tabel.align["Role"] = "l"
    tabel._max_width = {"Nama": 25, "Alamat": 30}

    for u in users:
        tabel.add_row(
            [
                u["user_id"],
                u["username"],
                u["nama"],
                u["alamat"],
                u["no_telepon"] or "-",
                u["role"],
            ]
        )

    print(tabel)


# Tampilkan user (Read)
def read_user():
    clear()
    users = get_user()
    if not users:
        print("\nBelum ada data users di database.")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    print("\n=== DAFTAR USER ===")
    _tampilkan_tabel_user(users)
    input("\nTekan Enter untuk kembali ke menu...")


# Buat user baru (Create)
def create_user(role="warga"):
    if role not in ("warga", "petugas", "admin"):
        clear()
        print(f"\nRole '{role}' tidak valid!")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    # Input & validasi username
    pesan_error = ""
    while True:
        clear()
        print("\n=== REGISTRASI AKUN BARU ===")
        print(
            f"Role: {role.capitalize()} | Ketik '0' pada username untuk kembali ke menu\n"
        )
        if pesan_error:
            print(f"[!] {pesan_error}\n")
            pesan_error = ""

        username = input(
            "Masukkan username anda (min 3 karakter, maks 20 karakter): "
        ).strip()
        if username == "0":
            return
        if not username:
            pesan_error = "Username tidak boleh kosong! Coba lagi."
            continue
        if " " in username:
            pesan_error = "Username tidak boleh mengandung spasi! Coba lagi."
            continue
        if len(username) > 20 or len(username) < 3:
            pesan_error = "Username tidak boleh lebih kecil dari 3 karakter atau lebih besar dari 20 karakter! Coba lagi."
            continue
        if not username.isalnum():
            pesan_error = "Username hanya boleh berisi huruf dan angka! Coba lagi."
            continue

        conn = get_connection()
        try:
            cek = conn.execute(
                "SELECT 1 FROM users WHERE username = ?", (username,)
            ).fetchone()
        except sqlite3.Error as e:
            print(f"\nGagal memeriksa username: {e}")
            input("\nTekan Enter untuk kembali ke menu...")
            return
        finally:
            conn.close()

        if cek:
            pesan_error = f"Username '{username}' sudah terpakai! Pilih yang lain."
        else:
            break

    # Input & konfirmasi password (pakai masking "*")
    pesan_error = ""
    while True:
        clear()
        print("\n=== REGISTRASI AKUN BARU ===")
        print(f"Role: {role.capitalize()} | Username: {username}\n")
        if pesan_error:
            print(f"[!] {pesan_error}\n")
            pesan_error = ""

        password = pwinput.pwinput(
            prompt="Masukkan password anda (min 6 karakter, maks 64 karakter): ",
            mask="*",
        )
        if not password.strip():
            pesan_error = "Password tidak boleh kosong! Coba lagi."
            continue
        if " " in password:
            pesan_error = "Password tidak boleh mengandung spasi! Coba lagi."
            continue
        if len(password) > 64 or len(password) < 6:
            pesan_error = "Password tidak boleh lebih kecil dari 6 karakter atau lebih besar dari 64 karakter! Coba lagi."
            continue

        konfirmasi_password = pwinput.pwinput(
            prompt="Konfirmasi password anda: ", mask="*"
        )

        if password != konfirmasi_password:
            pesan_error = "Password tidak cocok! Silakan ulangi dari awal."
            continue
        else:
            break

    # Input nama
    pesan_error = ""
    while True:
        clear()
        print("\n=== REGISTRASI AKUN BARU ===")
        print(f"Role: {role.capitalize()} | Username: {username}\n")
        if pesan_error:
            print(f"[!] {pesan_error}\n")
            pesan_error = ""

        nama = input("Masukkan nama anda (min 3 karakter, maks 100 karakter): ").strip()

        if not nama:
            pesan_error = "Nama tidak boleh kosong! Coba lagi."
            continue

        cek_nama = (
            nama.replace(" ", "")
            .replace("'", "")
            .replace("-", "")
            .replace(".", "")
            .replace("`", "")
        )

        if not cek_nama.isalpha():
            pesan_error = "Nama hanya boleh berisi huruf dan tanda baca yang wajar (', -, .)! Coba lagi."
            continue

        if len(nama) > 100 or len(nama) < 3:
            pesan_error = "Nama tidak boleh lebih kecil dari 3 karakter atau lebih besar dari 100 karakter! Coba lagi."
            continue
        break

    # Input alamat
    pesan_error = ""
    while True:
        clear()
        print("\n=== REGISTRASI AKUN BARU ===")
        print(f"Role: {role.capitalize()} | Username: {username} | Nama: {nama}\n")
        if pesan_error:
            print(f"[!] {pesan_error}\n")
            pesan_error = ""

        alamat = input(
            "Masukkan alamat anda (min 5 karakter, maks 200 karakter): "
        ).strip()

        if not alamat:
            pesan_error = "Alamat tidak boleh kosong! Coba lagi."
            continue

        if not any(c.isalnum() for c in alamat):
            pesan_error = "Alamat harus mengandung huruf atau angka!"
            continue

        if len(alamat) > 200 or len(alamat) < 5:
            pesan_error = "Alamat tidak boleh kurang dari 5 karakter atau lebih dari 200 karakter! Coba lagi."
            continue
        break

    # Input nomor telepon (opsional)
    pesan_error = ""
    while True:
        clear()
        print("\n=== REGISTRASI AKUN BARU ===")
        print(f"Role: {role.capitalize()} | Username: {username} | Nama: {nama}\n")
        if pesan_error:
            print(f"[!] {pesan_error}\n")
            pesan_error = ""

        no_telepon = input(
            "Masukkan nomor telepon anda (Opsional, 10-20 digit, tekan Enter jika kosong): "
        ).strip()
        if no_telepon:
            if not no_telepon.isdigit():
                pesan_error = "Nomor telepon hanya boleh berisi angka! Coba lagi."
                continue
            if len(no_telepon) > 20 or len(no_telepon) < 10:
                pesan_error = "Nomor telepon harus 10 hingga 20 karakter! Coba lagi."
                continue
        no_telepon = no_telepon if no_telepon else None
        break

    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO users (username, password, nama, alamat, no_telepon, role)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (username, hash_password(password), nama, alamat, no_telepon, role),
        )
        conn.commit()
        print(f"\n[Sukses] Akun '{username}' sebagai {role} berhasil dibuat!")
    except sqlite3.Error as e:
        print(f"\nGagal menyimpan data: {e}")
    finally:
        conn.close()

    input("\nTekan Enter untuk kembali ke menu...")


# Ubah data user (Update)
def update_user():
    users = get_user()
    if not users:
        clear()
        print("\n=== UPDATE DATA USER ===")
        print("Belum ada data user di database.")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    pesan_error = ""
    while True:
        clear()
        print("\n=== UPDATE DATA USER ===")
        _tampilkan_tabel_user(users)
        if pesan_error:
            print(f"\n[!] {pesan_error}")
            pesan_error = ""

        try:
            target_id = int(
                input(
                    "\nMasukkan user_id yang ingin diupdate (Tekan 0 untuk kembali ke menu): "
                ).strip()
            )
            if target_id == 0:
                return
            if target_id < 0 or target_id > 9223372036854775807:
                pesan_error = "user_id tidak valid atau terlalu besar!"
                continue
        except ValueError:
            pesan_error = "user_id harus berupa angka!"
            continue

        conn = get_connection()
        try:
            user_lama = conn.execute(
                "SELECT * FROM users WHERE user_id = ?", (target_id,)
            ).fetchone()
        except sqlite3.Error as e:
            print(f"\nGagal mengambil data user: {e}")
            input("\nTekan Enter untuk kembali ke menu...")
            return
        finally:
            conn.close()

        if not user_lama:
            pesan_error = f"User dengan ID {target_id} tidak ditemukan!"
            continue

        break

    # Simpan data sementara agar bisa di edit berkali kali sebelum di commit
    nama_baru = user_lama["nama"]
    alamat_baru = user_lama["alamat"]
    telp_baru = user_lama["no_telepon"]
    pass_baru = user_lama["password"]

    while True:
        clear()
        print("=== UPDATE DATA USER ===")
        print(f"Target User : {user_lama['username']} (ID: {target_id})")
        print(f"Nama        : {nama_baru}")
        print(f"Alamat      : {alamat_baru}")
        print(f"No. Telepon : {telp_baru or '-'}")
        print("-" * 35)

        pertanyaan = [
            inquirer.List(
                "kolom",
                message="Pilih data yang ingin diubah:",
                choices=[
                    "1. Nama",
                    "2. Alamat",
                    "3. No. Telepon",
                    "4. Password",
                    "5. Simpan perubahan dan selesai",
                    "6. Batal (buang perubahan)",
                ],
            )
        ]

        jawaban = inquirer.prompt(pertanyaan)
        pilihan = jawaban["kolom"][0] if jawaban else "6"

        if pilihan == "1":
            pesan_error = ""
            while True:
                clear()
                print("=== UPDATE NAMA USER ===")
                print(f"Target User : {user_lama['username']} (ID: {target_id})")
                print(f"Nama Saat Ini: {nama_baru}\n")
                if pesan_error:
                    print(f"[!] {pesan_error}\n")
                    pesan_error = ""

                input_nama = input(
                    "Masukkan nama baru (min 3 karakter, maks 100 karakter): "
                ).strip()

                cek_nama = (
                    input_nama.replace(" ", "")
                    .replace("'", "")
                    .replace("-", "")
                    .replace(".", "")
                    .replace("`", "")
                )

                if not cek_nama.isalpha():
                    pesan_error = "Nama hanya boleh berisi huruf dan tanda baca yang wajar (', -, .)! Coba lagi."
                    continue

                if not input_nama:
                    pesan_error = "Nama tidak boleh kosong! Coba lagi."
                    continue
                if len(input_nama) > 100 or len(input_nama) < 3:
                    pesan_error = "Nama tidak boleh lebih kecil dari 3 karakter atau lebih besar dari 100 karakter! Coba lagi."
                    continue
                nama_baru = input_nama
                print("\nNama berhasil diubah sementara.")
                break

        elif pilihan == "2":
            pesan_error = ""
            while True:
                clear()
                print("=== UPDATE ALAMAT USER ===")
                print(f"Target User  : {user_lama['username']} (ID: {target_id})")
                print(f"Alamat Saat Ini: {alamat_baru}\n")
                if pesan_error:
                    print(f"[!] {pesan_error}\n")
                    pesan_error = ""

                input_alamat = input(
                    "Masukkan alamat baru (min 5 karakter, maks 200 karakter): "
                ).strip()

                if not input_alamat:
                    pesan_error = "Alamat tidak boleh kosong! Coba lagi."
                    continue

                if not any(c.isalnum() for c in input_alamat):
                    pesan_error = "Alamat harus mengandung huruf atau angka!"
                    continue

                if len(input_alamat) > 200 or len(input_alamat) < 5:
                    pesan_error = "Alamat tidak boleh kurang dari 5 karakter atau lebih dari 200 karakter! Coba lagi."
                    continue
                alamat_baru = input_alamat
                print("\nAlamat berhasil diubah sementara.")
                break

        elif pilihan == "3":
            pesan_error = ""
            while True:
                clear()
                print("=== UPDATE NO. TELEPON USER ===")
                print(f"Target User     : {user_lama['username']} (ID: {target_id})")
                print(f"No. Telepon Saat Ini: {telp_baru or '-'}\n")
                if pesan_error:
                    print(f"[!] {pesan_error}\n")
                    pesan_error = ""

                input_telp = input(
                    "Masukkan nomor telepon baru (10-20 digit, Kosongkan/Enter untuk menghapus nomor): "
                ).strip()
                if input_telp:
                    if not input_telp.isdigit():
                        pesan_error = (
                            "Nomor telepon hanya boleh berisi angka! Coba lagi."
                        )
                        continue
                    if len(input_telp) > 20 or len(input_telp) < 10:
                        pesan_error = (
                            "Nomor telepon harus 10 hingga 20 karakter! Coba lagi."
                        )
                        continue
                telp_baru = input_telp if input_telp else None
                print("\nNo. Telepon berhasil diubah sementara.")
                break

        elif pilihan == "4":
            pesan_error = ""
            while True:
                clear()
                print("=== UPDATE PASSWORD USER ===")
                print(f"Target User : {user_lama['username']} (ID: {target_id})\n")
                if pesan_error:
                    print(f"[!] {pesan_error}\n")
                    pesan_error = ""

                pass_input = pwinput.pwinput(
                    prompt="Masukkan password baru (min 6 karakter, maks 64 karakter): ",
                    mask="*",
                )
                if not pass_input.strip():
                    pesan_error = "Password tidak boleh kosong! Coba lagi."
                    continue
                if " " in pass_input:
                    pesan_error = "Password tidak boleh mengandung spasi! Coba lagi."
                    continue
                if len(pass_input) > 64 or len(pass_input) < 6:
                    pesan_error = "Password tidak boleh lebih kecil dari 6 karakter atau lebih besar dari 64 karakter! Coba lagi."
                    continue

                konfirmasi_pass = pwinput.pwinput(
                    prompt="Konfirmasi password baru: ", mask="*"
                )
                if pass_input != konfirmasi_pass:
                    pesan_error = "Password tidak cocok! Silakan ulangi."
                    continue
                else:
                    pass_baru = hash_password(pass_input)
                    print("\nPassword berhasil diubah sementara.")
                    break

        elif pilihan == "5":
            break

        elif pilihan == "6":
            print("\nPerubahan dibatalkan. Data tidak disimpan.")
            input("\nTekan Enter untuk kembali ke menu...")
            return

        pesan_error = ""
        while True:
            clear()
            print("=== UPDATE DATA USER ===")
            print(f"Target User : {user_lama['username']} (ID: {target_id})")
            print(f"Nama        : {nama_baru}")
            print(f"Alamat      : {alamat_baru}")
            print(f"No. Telepon : {telp_baru or '-'}")
            print("-" * 35)
            if pesan_error:
                print(f"\n[!] {pesan_error}")
                pesan_error = ""

            lanjut = (
                input("\nMasih ingin mengupdate data lainnya pada user ini? [y/n]: ")
                .strip()
                .lower()
            )
            if lanjut in ("y", "n"):
                break
            pesan_error = "Input tidak valid! Masukkan 'y' atau 'n'."

        if lanjut == "n":
            break

    # Cek apakah ada data yang berubah sebelum menulis ke database
    if (
        nama_baru == user_lama["nama"]
        and alamat_baru == user_lama["alamat"]
        and telp_baru == user_lama["no_telepon"]
        and pass_baru == user_lama["password"]
    ):
        print("\nTidak ada data yang diubah.")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE users
            SET nama = ?, alamat = ?, no_telepon = ?, password = ?
            WHERE user_id = ?
            """,
            (nama_baru, alamat_baru, telp_baru, pass_baru, target_id),
        )
        conn.commit()
        print(
            f"\n[Sukses] Data user '{user_lama['username']}' berhasil diperbarui secara permanen."
        )
    except sqlite3.Error as e:
        print(f"\nGagal mengupdate user: {e}")
    finally:
        conn.close()

    input("\nTekan Enter untuk kembali ke menu...")


# Hapus user (Delete)
def delete_user(current_user_id=None):
    users = get_user()
    if not users:
        clear()
        print("\n=== HAPUS DATA USER ===")
        print("Belum ada data user di database.")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    pesan_error = ""
    while True:
        clear()
        print("\n=== HAPUS DATA USER ===")
        _tampilkan_tabel_user(users)
        if pesan_error:
            print(f"\n[!] {pesan_error}")
            pesan_error = ""

        try:
            target_id = int(
                input(
                    "\nMasukkan user_id yang ingin dihapus (Tekan 0 untuk kembali ke menu): "
                ).strip()
            )
            if target_id == 0:
                return
            if target_id < 0 or target_id > 9223372036854775807:
                pesan_error = "user_id tidak valid atau terlalu besar!"
                continue
            if current_user_id is not None and target_id == current_user_id:
                print(
                    "\n[Gagal] Anda tidak dapat menghapus akun Anda sendiri yang sedang digunakan!"
                )
                input("\nTekan Enter untuk kembali ke menu...")
                return
        except ValueError:
            pesan_error = "user_id harus berupa angka!"
            continue

        conn = get_connection()
        try:
            user_target = conn.execute(
                "SELECT username, role FROM users WHERE user_id = ?", (target_id,)
            ).fetchone()
        except sqlite3.Error as e:
            print(f"\nGagal memeriksa data user: {e}")
            input("\nTekan Enter untuk kembali ke menu...")
            return
        finally:
            conn.close()

        if not user_target:
            pesan_error = f"User dengan ID {target_id} tidak ditemukan!"
            continue

        break

    # Cegah penghapusan jika user tersebut adalah satu-satunya admin
    if user_target["role"] == "admin":
        conn = get_connection()
        try:
            jumlah_admin = conn.execute(
                "SELECT COUNT(*) FROM users WHERE role = 'admin'"
            ).fetchone()[0]
        finally:
            conn.close()

        if jumlah_admin <= 1:
            print(
                "\n[Gagal] Tidak dapat menghapus admin terakhir! Sistem harus memiliki minimal 1 admin."
            )
            input("\nTekan Enter untuk kembali ke menu...")
            return

    pesan_error = ""
    while True:
        clear()
        print("\n=== HAPUS DATA USER ===")
        print(f"Target User : {user_target['username']} ({user_target['role']})\n")
        if pesan_error:
            print(f"[!] {pesan_error}\n")
            pesan_error = ""

        konfirmasi = (
            input(
                f"Yakin ingin menghapus user '{user_target['username']}' ({user_target['role']})? [y/n]: "
            )
            .strip()
            .lower()
        )
        if konfirmasi in ("y", "n"):
            break
        pesan_error = "Input tidak valid! Masukkan 'y' atau 'n'."

    if konfirmasi == "n":
        print("\nPenghapusan dibatalkan.")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    conn = get_connection()
    try:
        conn.execute("DELETE FROM users WHERE user_id = ?", (target_id,))
        conn.commit()
        print(f"\n[Sukses] User '{user_target['username']}' berhasil dihapus!")
    except sqlite3.Error as e:
        print(f"\nGagal menghapus user: {e}")
    finally:
        conn.close()

    input("\nTekan Enter untuk kembali ke menu...")


# Menu utama CRUD User
def menu_crud_user(current_user_id=None):
    while True:
        clear()
        pertanyaan = [
            inquirer.List(
                "pilihan",
                message="=== MENU CRUD USER ===",
                choices=[
                    "1. Create user",
                    "2. Read user",
                    "3. Update user",
                    "4. Delete user",
                    "5. Kembali / Keluar",
                ],
            )
        ]

        jawaban = inquirer.prompt(pertanyaan)
        pilihan = jawaban["pilihan"][0] if jawaban else "5"

        if pilihan == "1":
            while True:
                clear()
                role_pertanyaan = [
                    inquirer.List(
                        "pilihan",
                        message="Mau buat akun role apa?",
                        choices=[
                            "1. Warga",
                            "2. Admin",
                            "3. Petugas",
                            "4. Kembali",
                        ],
                    )
                ]

                role_jawaban = inquirer.prompt(role_pertanyaan)
                role_pilihan = role_jawaban["pilihan"][0] if role_jawaban else "4"
                if role_pilihan == "1":
                    create_user()
                elif role_pilihan == "2":
                    create_user("admin")
                elif role_pilihan == "3":
                    create_user("petugas")
                else:
                    break

        elif pilihan == "2":
            read_user()
        elif pilihan == "3":
            update_user()
        elif pilihan == "4":
            delete_user(current_user_id)
        else:
            clear()
            break


if __name__ == "__main__":
    menu_crud_user()
