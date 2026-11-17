import sqlite3
import inquirer
from .database import get_connection
from .utils import hash_password


# buat tampilkan user (read)
def get_user():
    conn = get_connection()
    try:
        return conn.execute("SELECT * FROM users").fetchall()
    except sqlite3.Error as e:
        print(f"Gagal mengambil data user: {e}")
        return []
    finally:
        conn.close()


# buat create user
def create_user(role="warga"):
    print("\n=== REGISTRASI AKUN BARU ===")

    if role not in ("warga", "petugas", "admin"):
        print(f"Role '{role}' Tidak valid!")
        return

    while True:
        username = input("Masukkan username anda: ").strip()
        if not username:
            print("Username tidak boleh kosong! Coba lagi.")
            continue

        conn = get_connection()
        cek = conn.execute(
            "SELECT 1 FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()

        if cek:
            print(f"Username {username} sudah terpakai! Pilih yang lain.")
        else:
            break

    while True:
        password = input("Masukkan password anda: ").strip()
        if not password:
            print("Password tidak boleh kosong! Coba lagi.")
        else:
            break

    while True:
        nama = input("Masukkan nama anda: ").strip()
        if not nama:
            print("Nama tidak boleh kosong! Coba lagi.")
        else:
            break

    while True:
        alamat = input("Masukkan alamat anda: ").strip()
        if not alamat:
            print("Alamat tidak boleh kosong! Coba lagi.")
        else:
            break

    no_telepon = input(
        "Masukkan nomor telepon anda (Opsional, tekan Enter jika kosong): "
    ).strip()
    no_telepon = no_telepon if no_telepon else None

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
        print(f"\nAkun '{username}' sebagai {role} berhasil dibuat!")
    except sqlite3.Error as e:
        print(f"\nGagal menyimpan data: {e}")
    finally:
        conn.close()


# update user (update)
def update_user():
    print("\n=== UPDATE DATA USER ===")
    users = get_user()
    if not users:
        print("Belum ada data user di database.")
        return

    for u in users:
        print(
            f"ID: {u['user_id']} | Username: {u['username']} | Nama: {u['nama']} | Role: {u['role']}"
        )

    while True:
        try:
            target_id = int(input("\nMasukkan user_id yang ingin diupdate: ").strip())
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
        return

    print(
        f"\nMengedit user: {user_lama['username']} (Tekan enter jika tidak ingin mengubah kolom)"
    )

    nama_baru = input(f"Nama [{user_lama['nama']}]: ").strip() or user_lama["nama"]
    alamat_baru = (
        input(f"Alamat [{user_lama['alamat']}]: ").strip() or user_lama["alamat"]
    )

    telp_lama = user_lama["no_telepon"] or ""
    telp_input = input(f"No. Telepon [{telp_lama}]: ").strip()
    telp_baru = telp_input if telp_input else user_lama["no_telepon"]

    pass_input = input("Password baru (Kosongkan jika tidak diganti): ").strip()
    pass_baru = hash_password(pass_input) if pass_input else user_lama["password"]

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
        print(f"\nData user ID {target_id} berhasil diperbarui!")
    except sqlite3.Error as e:
        print(f"\nGagal mengupdate user: {e}")
    finally:
        conn.close()


# delete user (delete)
def delete_user():
    print("\n=== HAPUS DATA USER ===")
    users = get_user()
    if not users:
        print("Belum ada data user di database.")
        return

    for u in users:
        print(
            f"ID: {u['user_id']} | Username: {u['username']} | Nama: {u['nama']} | Role: {u['role']}"
        )

    while True:
        try:
            target_id = int(input("\nMasukkan user_id yang ingin dihapus: ").strip())
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


# MENU TESTING CRUD (INI BUAT NGE TES AJA, HAPUS AJA NANTI)
if __name__ == "__main__":
    while True:
        print("\n=== TEST CRUD USERS ===")
        print("1. Lihat semua user (Read)")
        print("2. Tambah user baru (Create)")
        print("3. Edit user (Update)")
        print("4. Hapus user (Delete)")
        print("0. Keluar")

        pilihan = input("Pilih menu [0-4]: ").strip()

        if pilihan == "1":
            print("\n=== DAFTAR USER ===")
            for row in get_user():
                print(dict(row))
        elif pilihan == "2":
            create_user()
        elif pilihan == "3":
            update_user()
        elif pilihan == "4":
            delete_user()
        elif pilihan == "0":
            print("Selesai testing.")
            break
        else:
            print("Pilihan tidak valid!")
