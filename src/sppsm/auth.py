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
    print("\n" + "=" * 40)
    print("            MENU LOGIN SPPSM            ")
    print("=" * 40)

    while True:
        username = input("Username : (input '0' untuk membatalkan)").strip()
        if not username:
            print("Input username tidak boleh kosong.")
            enter()
            continue

        elif username == "0":
            return False

        else:
            break
    while True:
        password = pwinput.pwinput(prompt="Password : ", mask="*")
        if not password:
            print("Input password tidak boleh kosong.")
            enter()
            continue

        else:
            break

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user:
        # PAKAI VERIFY_PASSWORD DARI UTILS
        if verify_password(password, user["password"]):
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
            conn.close()
            return True
        else:
            print("\nPassword salah.")
            enter()
    else:
        print("\nUsername tidak ditemukan, silakan daftar dulu.")
        enter()

    conn.close()
    return False


def register():
    print("\n" + "=" * 40)
    print("        REGISTRASI WARGA BARU SPPSM       ")
    print("=" * 40)

    while True:
        username = input("Username Baru (input '0' untuk membatalkan)  : ").strip()

        if not username:
            print("Username tidak boleh kosong.")
            enter()
            continue

        if username == "0":
            return

        if not (2 < len(username) <= 20):
            print("Username minimal 3 karakter dan maksimal 20 karakter")
            enter()
            continue

        conn = get_connection()
        cursor = conn.cursor()

        # Cek username udah dipake apa belum
        cek = cursor.execute(
            "SELECT 1 FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()

        if cek:
            print("\nUsername sudah dipakai, cari yang lain.")
            enter()
        else:
            break

    while True:
        password = pwinput.pwinput(prompt="Password Baru : ", mask="*")
        confirm_password = pwinput.pwinput(prompt="Konfirmasi Password : ", mask="*")

        if not password.strip():
            print("Password tidak boleh kosong.")
            enter()
            continue

        elif len(password) < 6:
            print("Password tidak boleh kurang dari 6")
            enter()
            continue

        elif not confirm_password.strip():
            print("Password tidak boleh kosong.")
            enter()
            continue

        elif password != confirm_password:
            print("\nPassword tidak cocok.")
            enter()
            continue

        else:
            break

    print("\n--- Isi Data Diri ---")

    while True:
        nama = input("Nama Lengkap    : ").strip()

        if not nama:
            print("Nama Tidak boleh kosong.")
            enter()

        elif not (3 <= len(nama) <= 100):
            print("Nama minimal 3 hingga 100 karakter")
            enter()
        else:
            break

    while True:
        alamat = input("Alamat (Blok/No): ").strip()
        if not alamat:
            print("Alamat tidak boleh kosong.")
            enter()

        elif not (5 <= len(alamat) <= 200):
            print("Input alamat minimal 5 hingga 200 karakter")
            enter()

        else:
            break

    while True:
        no_telepon = input("No. Telepon (Opsional)    : ").strip()

        if not no_telepon:
            no_telepon = None
            break

        elif not (10 <= len(no_telepon) <= 20):
            print("Nomor telepon harus 10 hingga 20 karakter.")
            enter()
            continue

        elif not no_telepon.isdigit():
            print("Nomor telepon hanya boleh berisi angka.")
            enter()
            continue

        else:
            break

    try:
        # Masukin data ke database
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
