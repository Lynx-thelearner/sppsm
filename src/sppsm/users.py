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


# Tampilkan user (Read)
def read_user():
    clear()
    users = get_user()
    if not users:
        print("\nBelum ada data users di database.")
        input("\nTekan Enter untuk kembali ke menu...")
        return

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

    print("\n=== DAFTAR USER ===")
    print(tabel)
    input("\nTekan Enter untuk kembali ke menu...")


# Buat user baru (Create)
def create_user(role="warga"):
    clear()
    print("\n=== REGISTRASI AKUN BARU ===")
    print("(Ketik '0' pada username untuk kembali ke menu)\n")

    if role not in ("warga", "petugas", "admin"):
        print(f"Role '{role}' tidak valid!")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    # Input & validasi username
    while True:
        username = input(
            "Masukkan username anda (min 3 karakter, maks 20 karakter): "
        ).strip()
        if username == "0":
            return
        if not username:
            print("Username tidak boleh kosong! Coba lagi.")
            continue
        if len(username) > 20 or len(username) < 3:
            print(
                "Username tidak boleh lebih kecil dari 3 karakter atau lebih besar dari 20 karakter! Coba lagi."
            )
            continue

        conn = get_connection()
        cek = conn.execute(
            "SELECT 1 FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()

        if cek:
            print(f"Username '{username}' sudah terpakai! Pilih yang lain.")
        else:
            break

    # Input & konfirmasi password (pakai masking "*")
    while True:
        password = pwinput.pwinput(prompt="Masukkan password anda: ", mask="*")
        if not password.strip():
            print("Password tidak boleh kosong! Coba lagi.")
            continue
        if len(password) > 64 or len(password) < 6:
            print(
                "Password tidak boleh lebih kecil dari 6 karakter atau lebih besar dari 64 karakter! Coba lagi."
            )
            continue

        konfirmasi_password = pwinput.pwinput(
            prompt="Konfirmasi password anda: ", mask="*"
        )

        if password != konfirmasi_password:
            print("Password tidak cocok! Silakan ulangi dari awal.\n")
        else:
            break

    # Input nama
    while True:
        nama = input("Masukkan nama anda (min 3 karakter, maks 100 karakter): ").strip()
        if not nama:
            print("Nama tidak boleh kosong! Coba lagi.")
            continue
        if len(nama) > 100 or len(nama) < 3:
            print(
                "Nama tidak boleh lebih kecil dari 3 karakter atau lebih besar dari 100 karakter! Coba lagi."
            )
            continue
        break

    # Input alamat
    while True:
        alamat = input(
            "Masukkan alamat anda (min 5 karakter, maks 200 karakter): "
        ).strip()
        if not alamat:
            print("Alamat tidak boleh kosong! Coba lagi.")
            continue
        if len(alamat) > 200 or len(alamat) < 5:
            print(
                "Alamat tidak boleh kurang dari 5 karakter atau lebih dari 200 karakter! Coba lagi."
            )
            continue
        break

    # Input nomor telepon (opsional)
    while True:
        no_telepon = input(
            "Masukkan nomor telepon anda (Opsional, maks 20 karakter, tekan Enter jika kosong): "
        ).strip()
        if len(no_telepon) > 20:
            print("Nomor telepon tidak boleh lebih dari 20 karakter! Coba lagi.")
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
    clear()
    print("\n=== UPDATE DATA USER ===")
    users = get_user()
    if not users:
        print("Belum ada data user di database.")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    for u in users:
        print(
            f"ID: {u['user_id']} | Username: {u['username']} | Nama: {u['nama']} | Role: {u['role']}"
        )

    while True:
        try:
            target_id = int(
                input(
                    "\nMasukkan user_id yang ingin diupdate (Tekan 0 untuk kembali ke menu): "
                ).strip()
            )
            if target_id == 0:
                return
            if target_id < 0 or target_id > 9223372036854775807:
                print("user_id tidak valid atau terlalu besar!")
                continue
            break
        except ValueError:
            print("user_id harus berupa angka!")

    conn = get_connection()
    user_lama = conn.execute(
        "SELECT * FROM users WHERE user_id = ?", (target_id,)
    ).fetchone()
    conn.close()

    if not user_lama:
        print(f"User dengan ID {target_id} tidak ditemukan!")
        input("\nTekan Enter untuk kembali ke menu...")
        return

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
            while True:
                input_nama = input(
                    "\nMasukkan nama baru (min 3 karakter, maks 100 karakter): "
                ).strip()
                if not input_nama:
                    print("Nama tidak boleh kosong! Coba lagi.")
                    continue
                if len(input_nama) > 100 or len(input_nama) < 3:
                    print(
                        "Nama tidak boleh lebih kecil dari 3 karakter atau lebih besar dari 100 karakter! Coba lagi."
                    )
                    continue
                nama_baru = input_nama
                print("Nama berhasil diubah sementara.")
                break

        elif pilihan == "2":
            while True:
                input_alamat = input(
                    "\nMasukkan alamat baru (min 5 karakter, maks 200 karakter): "
                ).strip()
                if not input_alamat:
                    print("Alamat tidak boleh kosong! Coba lagi.")
                    continue
                if len(input_alamat) > 200 or len(input_alamat) < 5:
                    print(
                        "Alamat tidak boleh kurang dari 5 karakter atau lebih dari 200 karakter! Coba lagi."
                    )
                    continue
                alamat_baru = input_alamat
                print("Alamat berhasil diubah sementara.")
                break

        elif pilihan == "3":
            while True:
                input_telp = input(
                    "\nMasukkan nomor telepon baru (maks 20 karakter, Kosongkan/Enter untuk menghapus nomor): "
                ).strip()
                if len(input_telp) > 20:
                    print(
                        "Nomor telepon tidak boleh lebih dari 20 karakter! Coba lagi."
                    )
                    continue
                telp_baru = input_telp if input_telp else None
                print("No. Telepon berhasil diubah sementara.")
                break

        elif pilihan == "4":
            while True:
                pass_input = pwinput.pwinput(
                    prompt="\nMasukkan password baru (min 6 karakter, maks 20 karakter): ",
                    mask="*",
                )
                if not pass_input.strip():
                    print("Password tidak boleh kosong! Coba lagi.")
                    continue
                if len(pass_input) > 20 or len(pass_input) < 6:
                    print(
                        "Password tidak boleh lebih kecil dari 6 karakter atau lebih besar dari 20 karakter! Coba lagi."
                    )
                    continue

                konfirmasi_pass = pwinput.pwinput(
                    prompt="Konfirmasi password baru: ", mask="*"
                )
                if pass_input != konfirmasi_pass:
                    print("Password tidak cocok! Silakan ulangi.\n")
                else:
                    pass_baru = hash_password(pass_input)
                    print("Password berhasil diubah sementara.")
                    break

        elif pilihan == "5":
            break

        elif pilihan == "6":
            print("\nPerubahan dibatalkan. Data tidak disimpan.")
            input("\nTekan Enter untuk kembali ke menu...")
            return

        lanjut = (
            input("\nMasih ingin mengupdate data lainnya pada user ini? [y/n]: ")
            .strip()
            .lower()
        )
        if lanjut != "y":
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
def delete_user():
    clear()
    print("\n=== HAPUS DATA USER ===")
    users = get_user()
    if not users:
        print("Belum ada data user di database.")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    for u in users:
        print(
            f"ID: {u['user_id']} | Username: {u['username']} | Nama: {u['nama']} | Role: {u['role']}"
        )

    while True:
        try:
            target_id = int(
                input(
                    "\nMasukkan user_id yang ingin dihapus (Tekan 0 untuk kembali ke menu): "
                ).strip()
            )
            if target_id == 0:
                return
            if target_id < 0 or target_id > 9223372036854775807:
                print("user_id tidak valid atau terlalu besar!")
                continue
            break
        except ValueError:
            print("user_id harus berupa angka!")

    conn = get_connection()
    user_target = conn.execute(
        "SELECT username, role FROM users WHERE user_id = ?", (target_id,)
    ).fetchone()
    conn.close()

    if not user_target:
        print(f"User dengan ID {target_id} tidak ditemukan!")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    konfirmasi = (
        input(
            f"Yakin ingin menghapus user '{user_target['username']}' ({user_target['role']})? [y/n]: "
        )
        .strip()
        .lower()
    )
    if konfirmasi != "y":
        print("Penghapusan dibatalkan.")
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
def menu_crud_user():
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
                elif role_pilihan == "4":
                    break
                else:
                    clear()

        elif pilihan == "2":
            read_user()
        elif pilihan == "3":
            update_user()
        elif pilihan == "4":
            delete_user()
        else:
            clear()
            break


if __name__ == "__main__":
    menu_crud_user()
