import sqlite3

import inquirer
import pwinput

from .database import get_connection
from .utils import clear, hash_password, verify_password, enter

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

    username = input("Username : ").strip()
    password = pwinput.pwinput(prompt="Password : ", mask="*").strip()

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

    username = input("Username Baru : ").strip()

    conn = get_connection()
    cursor = conn.cursor()

    # Cek username udah dipake apa belum
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        print("\nUsername sudah dipakai, cari yang lain.")
        conn.close()
        return False

    password = pwinput.pwinput(prompt="Password Baru : ", mask="*")
    confirm_password = pwinput.pwinput(prompt="Konfirmasi Password : ", mask="*")

    if password != confirm_password:
        print("\nPassword tidak cocok.")
        conn.close()
        return False

    print("\n--- Isi Data Diri ---")
    nama = input("Nama Lengkap    : ").strip()
    alamat = input("Alamat (Blok/No): ").strip()
    no_telepon = input("No. Telepon     : ").strip()

    try:
        # Masukin data ke database
        cursor.execute(
            """
            INSERT INTO users (username, password, nama, alamat, no_telepon, role) 
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (username, hash_password(password), nama, alamat, no_telepon, "warga"),
        )
        conn.commit()
        print("\nRegistrasi Berhasil! Silakan login.")
        return True
    except sqlite3.Error as e:
        print(f"\nGagal daftar: {e}")
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
