import math
import sqlite3
from datetime import datetime

import inquirer
from prettytable import PrettyTable

from .database import get_connection
from .utils import clear


# Buat ambil semua data requests beserta nama & username pengaju (JOIN)
def get_requests():
    conn = get_connection()
    try:
        return conn.execute(
            """
            SELECT r.*, u.username, u.nama
            FROM requests r
            LEFT JOIN users u ON r.user_id = u.user_id
            ORDER BY r.request_id ASC
            """
        ).fetchall()
    except sqlite3.Error as e:
        print(f"Gagal mengambil data requests: {e}")
        return []
    finally:
        conn.close()


# Helper untuk mencetak tabel PrettyTable daftar requests (dipakai di Read, Update, Delete)
def _tampilkan_tabel_requests(data):
    tabel = PrettyTable()
    tabel.field_names = [
        "ID",
        "Pengaju",
        "Tgl Pengajuan",
        "Tgl Jemput",
        "Berat (kg)",
        "Alamat",
        "Status",
        "Catatan",
    ]
    tabel.align["Pengaju"] = "l"
    tabel.align["Tgl Pengajuan"] = "l"
    tabel.align["Tgl Jemput"] = "l"
    tabel.align["Berat (kg)"] = "r"
    tabel.align["Alamat"] = "l"
    tabel.align["Status"] = "l"
    tabel.align["Catatan"] = "l"

    # Batasi lebar kolom teks panjang agar tabel tidak hancur
    tabel._max_width = {"Alamat": 25, "Catatan": 20}

    for r in data:
        pengaju = (
            f"{r['nama']} ({r['username']})"
            if r["username"]
            else f"User ID {r['user_id']}"
        )
        berat = f"{r['berat_sampah']:.1f}" if r["berat_sampah"] is not None else "-"
        tabel.add_row(
            [
                r["request_id"],
                pengaju,
                r["tanggal_pengajuan"],
                r["tanggal_penjemputan"] or "-",
                berat,
                r["alamat"],
                r["status"],
                r["catatan"] or "-",
            ]
        )

    print(tabel)


# Ambil daftar user yang bisa dipilih sebagai pengaju
def _get_daftar_user():
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT user_id, username, nama, alamat, role FROM users ORDER BY user_id ASC"
        ).fetchall()
    except sqlite3.Error as e:
        print(f"\nGagal mengambil daftar user: {e}")
        return []
    finally:
        conn.close()


# Cetak tabel daftar user yang sudah diambil
def _cetak_tabel_user(users):
    tabel = PrettyTable()
    tabel.field_names = ["ID", "Username", "Nama", "Alamat", "Role"]
    tabel.align["Username"] = "l"
    tabel.align["Nama"] = "l"
    tabel.align["Alamat"] = "l"
    tabel.align["Role"] = "l"
    tabel._max_width = {"Alamat": 30}

    for u in users:
        tabel.add_row(
            [
                u["user_id"],
                u["username"],
                u["nama"],
                u["alamat"],
                u["role"],
            ]
        )

    print("\n--- Daftar User Tersedia ---")
    print(tabel)


# Tampilkan Requests (Read)
def read_requests():
    clear()
    data = get_requests()
    if not data:
        print("\nBelum ada data request penjemputan sampah di database.")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    print("\n=== DAFTAR REQUEST PENJEMPUTAN SAMPAH ===")
    _tampilkan_tabel_requests(data)
    input("\nTekan Enter untuk kembali ke menu...")


# Buat Request Baru (Create)
def create_request():
    users = _get_daftar_user()
    if not users:
        clear()
        print("\n=== BUAT REQUEST PENJEMPUTAN BARU ===")
        print("Belum ada user di database. Buat user terlebih dahulu!")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    pesan_error = ""
    while True:
        clear()
        print("\n=== BUAT REQUEST PENJEMPUTAN BARU ===")
        print("(Ketik '0' pada user_id untuk kembali ke menu)")
        _cetak_tabel_user(users)

        if pesan_error:
            print(f"\n[!] {pesan_error}")
            pesan_error = ""

        # Pilih user_id pengaju
        try:
            user_id = int(
                input(
                    "\nMasukkan user_id pengaju (Tekan 0 untuk kembali ke menu): "
                ).strip()
            )
            if user_id == 0:
                return
            if user_id < 0 or user_id > 9223372036854775807:
                pesan_error = "user_id tidak valid atau terlalu besar!"
                continue
        except ValueError:
            pesan_error = "user_id harus berupa angka!"
            continue

        conn = get_connection()
        try:
            user_target = conn.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()
        except sqlite3.Error as e:
            print(f"\nGagal memeriksa user: {e}")
            input("\nTekan Enter untuk kembali ke menu...")
            return
        finally:
            conn.close()

        if not user_target:
            pesan_error = f"User dengan ID {user_id} tidak ditemukan!"
        else:
            break

    # Tanggal pengajuan otomatis waktu sekarang
    tanggal_pengajuan = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # tanggal penjemputan belum ada saat request dibuat
    tanggal_penjemputan = None

    # Berat sampah (opsional, >0 - 250 kg, dibulatkan 2 desimal)
    pesan_error = ""
    while True:
        clear()
        print("\n=== BUAT REQUEST PENJEMPUTAN BARU ===")
        print(
            f"Pengaju: {user_target['nama']} ({user_target['username']}) | Tgl Pengajuan: {tanggal_pengajuan}\n"
        )
        if pesan_error:
            print(f"[!] {pesan_error}\n")
            pesan_error = ""

        berat_input = input(
            "Perkiraan berat sampah dalam kg (Opsional, >0-250 kg, Enter jika kosong): "
        ).strip()
        if not berat_input:
            berat_sampah = None
            break
        try:
            nilai_berat = float(berat_input)
            if not math.isfinite(nilai_berat) or nilai_berat <= 0:
                pesan_error = (
                    "Berat sampah harus lebih dari 0 kg dan berupa angka valid!"
                )
                continue
            if nilai_berat > 250:
                pesan_error = "Berat sampah maksimal 250 kg (rentang >0-250 kg)!"
                continue
            berat_sampah = round(nilai_berat, 2)
            break
        except ValueError:
            pesan_error = "Berat sampah harus berupa angka (>0-250 kg, contoh: 2.5)!"

    # Alamat penjemputan (default ambil dari alamat user)
    pesan_error = ""
    while True:
        clear()
        print("\n=== BUAT REQUEST PENJEMPUTAN BARU ===")
        print(f"Pengaju: {user_target['nama']} ({user_target['username']})\n")
        if pesan_error:
            print(f"[!] {pesan_error}\n")
            pesan_error = ""

        alamat_input = input(
            f"Alamat penjemputan [Enter untuk '{user_target['alamat']}']: "
        ).strip()
        alamat = alamat_input if alamat_input else user_target["alamat"]
        if len(alamat) > 200 or len(alamat) < 5:
            pesan_error = "Alamat tidak boleh kurang dari 5 karakter atau lebih dari 200 karakter!"
            continue
        break

    # Status request (otomatis menunggu)
    status = "menunggu"

    # Catatan (opsional, maks 250 karakter)
    pesan_error = ""
    while True:
        clear()
        print("\n=== BUAT REQUEST PENJEMPUTAN BARU ===")
        print(f"Pengaju: {user_target['nama']} ({user_target['username']})\n")
        if pesan_error:
            print(f"[!] {pesan_error}\n")
            pesan_error = ""

        catatan_input = input(
            "Catatan tambahan (Opsional, maks 250 karakter, Enter jika kosong): "
        ).strip()
        if len(catatan_input) > 250:
            pesan_error = "Catatan tidak boleh lebih dari 250 karakter!"
            continue
        catatan = catatan_input if catatan_input else None
        break

    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO requests (
                user_id, tanggal_pengajuan, tanggal_penjemputan,
                berat_sampah, alamat, status, catatan
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                tanggal_pengajuan,
                tanggal_penjemputan,
                berat_sampah,
                alamat,
                status,
                catatan,
            ),
        )
        conn.commit()
        print(
            f"\n[Sukses] Request untuk '{user_target['username']}' berhasil ditambahkan!"
        )
    except sqlite3.Error as e:
        print(f"\nGagal menyimpan request: {e}")
    finally:
        conn.close()

    input("\nTekan Enter untuk kembali ke menu...")


# Ubah Data Request (Update - Admin)
def update_request():
    data = get_requests()
    if not data:
        clear()
        print("\n=== UPDATE DATA REQUEST ===")
        print("Belum ada data request di database.")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    pesan_error = ""
    while True:
        clear()
        print("\n=== UPDATE DATA REQUEST ===")
        _tampilkan_tabel_requests(data)
        if pesan_error:
            print(f"\n[!] {pesan_error}")
            pesan_error = ""

        try:
            target_id = int(
                input(
                    "\nMasukkan request_id yang ingin diupdate (Tekan 0 untuk kembali ke menu): "
                ).strip()
            )
            if target_id == 0:
                return
            if target_id < 0 or target_id > 9223372036854775807:
                pesan_error = "request_id tidak valid atau terlalu besar!"
                continue
            break
        except ValueError:
            pesan_error = "request_id harus berupa angka!"

    conn = get_connection()
    try:
        req_lama = conn.execute(
            "SELECT * FROM requests WHERE request_id = ?", (target_id,)
        ).fetchone()
    except sqlite3.Error as e:
        print(f"\nGagal mengambil data request: {e}")
        input("\nTekan Enter untuk kembali ke menu...")
        return
    finally:
        conn.close()

    if not req_lama:
        clear()
        print(f"\nRequest dengan ID {target_id} tidak ditemukan!")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    # Simpan nilai sementara sebelum disimpan permanen
    tanggal_baru = req_lama["tanggal_penjemputan"]
    berat_baru = req_lama["berat_sampah"]
    alamat_baru = req_lama["alamat"]
    status_baru = req_lama["status"]
    catatan_baru = req_lama["catatan"]

    conn = get_connection()
    try:
        u_info = conn.execute(
            "SELECT username, nama FROM users WHERE user_id = ?",
            (req_lama["user_id"],),
        ).fetchone()
    except sqlite3.Error:
        u_info = None
    finally:
        conn.close()

    label_pengaju = (
        f"{u_info['nama']} ({u_info['username']}) [ID: {req_lama['user_id']}]"
        if u_info
        else f"ID: {req_lama['user_id']}"
    )

    while True:
        clear()
        print("=== UPDATE DATA REQUEST ===")
        print(f"Request ID          : {target_id}")
        print(f"Pengaju             : {label_pengaju}")
        print(f"Tanggal Pengajuan   : {req_lama['tanggal_pengajuan']}")
        print(f"Tanggal Penjemputan : {tanggal_baru or '-'}")
        print(f"Berat Sampah (kg)   : {berat_baru if berat_baru is not None else '-'}")
        print(f"Alamat              : {alamat_baru}")
        print(f"Status              : {status_baru}")
        print(f"Catatan             : {catatan_baru or '-'}")
        print("-" * 45)

        pertanyaan = [
            inquirer.List(
                "kolom",
                message="Pilih data yang ingin diubah:",
                choices=[
                    "1. Tanggal Penjemputan",
                    "2. Berat Sampah (kg)",
                    "3. Alamat Penjemputan",
                    "4. Status Request",
                    "5. Catatan",
                    "6. Simpan perubahan dan selesai",
                    "7. Batal (buang perubahan)",
                ],
            )
        ]

        jawaban = inquirer.prompt(pertanyaan)
        pilihan = jawaban["kolom"][0] if jawaban else "7"

        if pilihan == "1":
            clear()
            print("=== UPDATE TANGGAL PENJEMPUTAN ===")
            print(f"Request ID                  : {target_id}")
            print(f"Tanggal Penjemputan Saat Ini: {tanggal_baru or '-'}")
            tanggal_baru = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"Tanggal Penjemputan Baru    : {tanggal_baru} (otomatis waktu sekarang)"
            )
            input("\nTekan Enter untuk melanjutkan...")

        elif pilihan == "2":
            pesan_error = ""
            while True:
                clear()
                print("=== UPDATE BERAT SAMPAH (KG) ===")
                print(f"Request ID         : {target_id}")
                print(
                    f"Berat Saat Ini     : {berat_baru if berat_baru is not None else '-'}\n"
                )
                if pesan_error:
                    print(f"[!] {pesan_error}\n")
                    pesan_error = ""

                input_berat = input(
                    "Masukkan berat sampah baru dalam kg (>0-250 kg, Enter untuk mengosongkan): "
                ).strip()
                if not input_berat:
                    berat_baru = None
                    break
                try:
                    nilai_berat = float(input_berat)
                    if not math.isfinite(nilai_berat) or nilai_berat <= 0:
                        pesan_error = (
                            "Berat sampah harus lebih dari 0 kg dan berupa angka valid!"
                        )
                        continue
                    if nilai_berat > 250:
                        pesan_error = (
                            "Berat sampah maksimal 250 kg (rentang >0-250 kg)!"
                        )
                        continue
                    berat_baru = round(nilai_berat, 2)
                    break
                except ValueError:
                    pesan_error = "Berat sampah harus berupa angka (>0-250 kg)!"

        elif pilihan == "3":
            pesan_error = ""
            while True:
                clear()
                print("=== UPDATE ALAMAT PENJEMPUTAN ===")
                print(f"Request ID      : {target_id}")
                print(f"Alamat Saat Ini : {alamat_baru}\n")
                if pesan_error:
                    print(f"[!] {pesan_error}\n")
                    pesan_error = ""

                input_alamat = input(
                    "Masukkan alamat penjemputan baru (min 5 karakter, maks 200 karakter): "
                ).strip()
                if not input_alamat:
                    pesan_error = "Alamat tidak boleh kosong!"
                    continue
                if len(input_alamat) > 200 or len(input_alamat) < 5:
                    pesan_error = "Alamat tidak boleh kurang dari 5 karakter atau lebih dari 200 karakter!"
                    continue
                alamat_baru = input_alamat
                break

        elif pilihan == "4":
            clear()
            print("=== UPDATE STATUS REQUEST ===")
            print(f"Request ID     : {target_id}")
            print(f"Status Saat Ini: {status_baru}\n")
            tanya_status = [
                inquirer.List(
                    "status_baru",
                    message="Pilih status baru:",
                    choices=["menunggu", "selesai", "ditolak"],
                )
            ]
            jwb_status = inquirer.prompt(tanya_status)
            if jwb_status:
                status_baru = jwb_status["status_baru"]

        elif pilihan == "5":
            pesan_error = ""
            while True:
                clear()
                print("=== UPDATE CATATAN REQUEST ===")
                print(f"Request ID      : {target_id}")
                print(f"Catatan Saat Ini: {catatan_baru or '-'}\n")
                if pesan_error:
                    print(f"[!] {pesan_error}\n")
                    pesan_error = ""

                catatan_input = input(
                    "Masukkan catatan baru (maks 250 karakter, Enter untuk mengosongkan): "
                ).strip()
                if len(catatan_input) > 250:
                    pesan_error = "Catatan tidak boleh lebih dari 250 karakter!"
                    continue
                catatan_baru = catatan_input if catatan_input else None
                break

        elif pilihan == "6":
            break

        elif pilihan == "7":
            print("\nPerubahan dibatalkan. Data tidak disimpan.")
            input("\nTekan Enter untuk kembali ke menu...")
            return

        pesan_error = ""
        while True:
            clear()
            print("=== UPDATE DATA REQUEST ===")
            print(f"Request ID          : {target_id}")
            print(f"Pengaju             : {label_pengaju}")
            print(f"Tanggal Penjemputan : {tanggal_baru or '-'}")
            print(
                f"Berat Sampah (kg)   : {berat_baru if berat_baru is not None else '-'}"
            )
            print(f"Alamat              : {alamat_baru}")
            print(f"Status              : {status_baru}")
            print(f"Catatan             : {catatan_baru or '-'}")
            print("-" * 45)
            if pesan_error:
                print(f"\n[!] {pesan_error}")
                pesan_error = ""

            lanjut = (
                input("\nMasih ingin mengupdate data lainnya pada request ini? [y/n]: ")
                .strip()
                .lower()
            )
            if lanjut in ("y", "n"):
                break
            pesan_error = "Input tidak valid! Masukkan 'y' atau 'n'."

        if lanjut == "n":
            break

    # Cek apakah ada data yang benar-benar berubah sebelum menulis ke database
    if (
        tanggal_baru == req_lama["tanggal_penjemputan"]
        and berat_baru == req_lama["berat_sampah"]
        and alamat_baru == req_lama["alamat"]
        and status_baru == req_lama["status"]
        and catatan_baru == req_lama["catatan"]
    ):
        print("\nTidak ada data yang diubah.")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE requests
            SET tanggal_penjemputan = ?,
                berat_sampah = ?,
                alamat = ?,
                status = ?,
                catatan = ?
            WHERE request_id = ?
            """,
            (
                tanggal_baru,
                berat_baru,
                alamat_baru,
                status_baru,
                catatan_baru,
                target_id,
            ),
        )
        conn.commit()
        print(
            f"\n[Sukses] Data request ID {target_id} berhasil diperbarui secara permanen."
        )
    except sqlite3.Error as e:
        print(f"\nGagal mengupdate request: {e}")
    finally:
        conn.close()

    input("\nTekan Enter untuk kembali ke menu...")


# Hapus Request (Delete)
def delete_request():
    data = get_requests()
    if not data:
        clear()
        print("\n=== HAPUS DATA REQUEST ===")
        print("Belum ada data request di database.")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    pesan_error = ""
    while True:
        clear()
        print("\n=== HAPUS DATA REQUEST ===")
        _tampilkan_tabel_requests(data)
        if pesan_error:
            print(f"\n[!] {pesan_error}")
            pesan_error = ""

        try:
            target_id = int(
                input(
                    "\nMasukkan request_id yang ingin dihapus (Tekan 0 untuk kembali ke menu): "
                ).strip()
            )
            if target_id == 0:
                return
            if target_id < 0 or target_id > 9223372036854775807:
                pesan_error = "request_id tidak valid atau terlalu besar!"
                continue
            break
        except ValueError:
            pesan_error = "request_id harus berupa angka!"

    conn = get_connection()
    try:
        req_target = conn.execute(
            """
            SELECT r.request_id, r.status, r.tanggal_pengajuan, u.username
            FROM requests r
            LEFT JOIN users u ON r.user_id = u.user_id
            WHERE r.request_id = ?
            """,
            (target_id,),
        ).fetchone()
    except sqlite3.Error as e:
        print(f"\nGagal memeriksa data request: {e}")
        input("\nTekan Enter untuk kembali ke menu...")
        return
    finally:
        conn.close()

    if not req_target:
        clear()
        print(f"\nRequest dengan ID {target_id} tidak ditemukan!")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    pengaju = req_target["username"] or "User tidak diketahui"
    pesan_error = ""
    while True:
        clear()
        print("\n=== HAPUS DATA REQUEST ===")
        print(
            f"Target Request : ID {target_id} milik '{pengaju}' (Status: {req_target['status']})\n"
        )
        if pesan_error:
            print(f"[!] {pesan_error}\n")
            pesan_error = ""

        konfirmasi = (
            input(
                f"Yakin ingin menghapus request ID {target_id} milik '{pengaju}' (Status: {req_target['status']})? [y/n]: "
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
        conn.execute("DELETE FROM requests WHERE request_id = ?", (target_id,))
        conn.commit()
        print(f"\n[Sukses] Request ID {target_id} berhasil dihapus!")
    except sqlite3.Error as e:
        print(f"\nGagal menghapus request: {e}")
    finally:
        conn.close()

    input("\nTekan Enter untuk kembali ke menu...")


# Menu utama CRUD Requests
def menu_crud_requests():
    while True:
        clear()
        pertanyaan = [
            inquirer.List(
                "pilihan",
                message="=== MENU CRUD REQUESTS (ADMIN) ===",
                choices=[
                    "1. Create request",
                    "2. Read requests",
                    "3. Update request",
                    "4. Delete request",
                    "5. Kembali",
                ],
            )
        ]

        jawaban = inquirer.prompt(pertanyaan)
        pilihan = jawaban["pilihan"][0] if jawaban else "5"

        if pilihan == "1":
            create_request()
        elif pilihan == "2":
            read_requests()
        elif pilihan == "3":
            update_request()
        elif pilihan == "4":
            delete_request()
        else:
            clear()
            break


if __name__ == "__main__":
    menu_crud_requests()
