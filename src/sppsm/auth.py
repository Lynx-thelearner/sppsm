import sqlite3

import inquirer
import pwinput

from .database import get_connection
from .utils import clear, enter, hash_password, verify_password

# Session buat nyimpen data user yang lagi login
session = {
    "user_id": None,
    "username": None,
    "nama": None,
    "role": None,
    "alamat": None,
    "no_telepon": None,
    "is_login": False,
}


def login():
    kesempatan = 3

    while kesempatan > 0:
        clear()

        print("\n" + "=" * 40)
        print("            MENU LOGIN SPPSM            ")
        print("=" * 40)
        print(f"Sisa kesempatan login: {kesempatan}")

        username = input("Username (input '0' untuk membatalkan) : ").strip()
        if not username:
            print("Input username tidak boleh kosong.")
            enter()
            continue

        elif username == "0":
            return False

        while True:
            password = pwinput.pwinput(prompt="Password : ", mask="*")
            if not password:
                print("Input password tidak boleh kosong.")
                enter()
                continue
            break

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
        except sqlite3.Error as e:
            print(f"\nGagal memeriksa data login: {e}")
            enter()
            return False
        finally:
            if conn:
                conn.close()

        if user and verify_password(password, user["password"]):
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            session["nama"] = user["nama"]
            session["role"] = user["role"]
            session["alamat"] = user["alamat"]
            session["no_telepon"] = user["no_telepon"]
            session["is_login"] = True

            print("\nLogin Berhasil!")
            print(f"Selamat datang, {session['nama']} ({session['role']}).")
            enter()
            return True

        kesempatan -= 1

        if not user:
            print("\nUsername tidak ditemukan!")
        else:
            print("\nPassword salah!")

        if kesempatan > 0:
            print(f"Sisa percobaan Anda tinggal {kesempatan} kali lagi.")
            enter()
        else:
            print(
                "\nKesempatan login telah habis (3x salah). Akses kembali ke menu utama."
            )
            enter()
            return False

    return False


def register():
    while True:
        clear()

        print("\n" + "=" * 40)
        print("        REGISTRASI WARGA BARU SPPSM       ")
        print("=" * 40)
        print("Ketik '0' pada username untuk kembali ke menu\n")

        username = input(
            "Masukkan username anda (min 3 karakter, maks 20 karakter): "
        ).strip()

        if not username:
            print("Username tidak boleh kosong! Coba lagi.")
            enter()
            continue

        if username == "0":
            return False

        if " " in username:
            print("Username tidak boleh mengandung spasi! Coba lagi.")
            enter()
            continue

        if not (3 <= len(username) <= 20):
            print(
                "Username tidak boleh lebih kecil dari 3 karakter atau lebih besar dari 20 karakter! Coba lagi."
            )
            enter()
            continue

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cek = cursor.execute(
                "SELECT 1 FROM users WHERE username = ?", (username,)
            ).fetchone()
        except sqlite3.Error as e:
            print(f"\nGagal memeriksa username: {e}")
            enter()
            return False
        finally:
            if conn:
                conn.close()

        if cek:
            print("\nUsername sudah dipakai, cari yang lain.")
            enter()
        else:
            break

    while True:
        clear()
        password = pwinput.pwinput(prompt="Password Baru : ", mask="*")
        confirm_password = pwinput.pwinput(prompt="Konfirmasi Password : ", mask="*")

        if not password.strip():
            print("Password tidak boleh kosong! Coba lagi.")
            enter()
            continue

        if " " in password:
            print("Password tidak boleh mengandung spasi! Coba lagi.")
            enter()
            continue

        if len(password) < 6 or len(password) > 64:
            print(
                "Password tidak boleh lebih kecil dari 6 karakter atau lebih besar dari 64 karakter! Coba lagi."
            )
            enter()
            continue

        if not confirm_password.strip():
            print("Password konfirmasi tidak boleh kosong! Coba lagi.")
            enter()
            continue

        if password != confirm_password:
            print("Password tidak cocok! Silakan ulangi dari awal.\n")
            enter()
            continue

        break

    print("\n--- Isi Data Diri ---")

    while True:
        nama = input("Masukkan nama anda (min 3 karakter, maks 100 karakter): ").strip()

        if not nama:
            print("Nama tidak boleh kosong! Coba lagi.")
            enter()
            continue

        if not (3 <= len(nama) <= 100):
            print(
                "Nama tidak boleh lebih kecil dari 3 karakter atau lebih besar dari 100 karakter! Coba lagi."
            )
            enter()
            continue

        break

    while True:
        clear()
        alamat = input(
            "Masukkan alamat anda (min 5 karakter, maks 200 karakter): "
        ).strip()
        if not alamat:
            print("Alamat tidak boleh kosong.")
            enter()
            continue

        if not (5 <= len(alamat) <= 200):
            print(
                "Alamat tidak boleh kurang dari 5 karakter atau lebih dari 200 karakter!"
            )
            enter()
            continue

        break

    while True:
        clear()
        no_telepon = input(
            "Masukkan nomor telepon anda (Opsional, 10-20 digit, tekan Enter jika kosong): "
        ).strip()

        if not no_telepon:
            no_telepon = None
            break

        if not no_telepon.isdigit():
            print("Nomor telepon hanya boleh berisi angka.")
            enter()
            continue

        if not (10 <= len(no_telepon) <= 20):
            print("Nomor telepon harus 10 hingga 20 karakter.")
            enter()
            continue

        break

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (username, password, nama, alamat, no_telepon, role) 
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (username, hash_password(password), nama, alamat, no_telepon, "warga"),
        )
        conn.commit()
        print("\nRegistrasi Berhasil! Silakan login.")
        enter()
        return True
    except sqlite3.Error as e:
        print(f"\nGagal daftar: {e}")
        enter()
        return False
    finally:
        if conn:
            conn.close()


def logout():
    # Reset session jadi kosong lagi
    session["user_id"] = None
    session["username"] = None
    session["nama"] = None
    session["role"] = None
    session["alamat"] = None
    session["no_telepon"] = None
    session["is_login"] = False
    print("\nBerhasil logout.")


def auth_menu():
    clear()
    pertanyaan = [
        inquirer.List(
            "pilihan",
            message="=== Menu Akun ===",
            choices=[
                ("Login", "1"),
                ("Register", "2"),
                ("Exit", "3"),
            ],
        )
    ]

    jawaban = inquirer.prompt(pertanyaan)
    return jawaban["pilihan"] if jawaban else "3"
