import pwinput
import sqlite3
from typing import Any

from .database import get_connection
from .utils import clear_screen, hash_password, pause, verify_password

session: dict[str, Any] = {
    "user_id": None,
    "username": None,
    "nama": None,
    "role": None,
    "alamat": None,
    "no_telepon": None,
    "is_login": False,
}

def set_session(user_row: Any) -> None:
    session["user_id"] = user_row["user_id"]
    session["username"] = user_row["username"]
    session["nama"] = user_row["nama"]
    session["role"] = user_row["role"]
    session["alamat"] = user_row["alamat"]
    session["no_telepon"] = user_row["no_telepon"]
    session["is_login"] = True

def login() -> bool:
    clear_screen()
    print("=" * 40)
    print("            MENU LOGIN SPPSM            ")
    print("=" * 40)

    username = input("Username : ").strip()
    password = pwinput.pwinput(prompt="Password : ", mask="*")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user:
        if verify_password(password, user["password"]):
            set_session(user)
            print("\nLogin Berhasil!")
            print(f"Selamat datang, {session['nama']} ({session['role'].capitalize()}).")
            conn.close()
            pause()
            return True
        else:
            print("\nPassword salah. Silakan coba lagi.")
    else:
        print("\nUsername tidak ditemukan. Silakan daftar terlebih dahulu.")

    conn.close()
    pause()
    return False

def register() -> bool:
    clear_screen()
    print("=" * 40)
    print("        REGISTRASI WARGA BARU SPPSM       ")
    print("=" * 40)

    username = input("Username Baru : ").strip()
    
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        print("\nUsername sudah digunakan. Silakan pilih yang lain.")
        conn.close()
        pause()
        return False

    password = pwinput.pwinput(prompt="Password Baru : ", mask="*")
    confirm_password = pwinput.pwinput(prompt="Konfirmasi Password : ", mask="*")

    if password != confirm_password:
        print("\nPassword tidak cocok. Silakan ulangi.")
        conn.close()
        pause()
        return False

    print("\n--- Lengkapi Data Diri Anda ---")
    nama = input("Nama Lengkap    : ").strip()
    alamat = input("Alamat (Blok/No): ").strip()
    no_telepon = input("No. Telepon     : ").strip()

    hashed_pw = hash_password(password)

    try:
        cursor.execute(
            """
            INSERT INTO users (username, password, nama, alamat, no_telepon, role) 
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (username, hashed_pw, nama, alamat, no_telepon, "warga")
        )
        conn.commit()
        print("\nRegistrasi Berhasil! Silakan login menggunakan akun baru Anda.")
        pause()
        return True
    except sqlite3.Error as e:
        print(f"\nTerjadi kesalahan database: {e}")
        pause()
        return False
    finally:
        conn.close()
        