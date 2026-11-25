import math
import sqlite3
from contextlib import closing
from datetime import datetime

import inquirer
from prettytable import PrettyTable

from .auth import logout
from .database import get_connection
from .utils import clear, enter


def menu_petugas():
    clear()

    pertanyaan = [
        inquirer.List(
            "pilihan",
            message="=== Menu Petugas ===",
            choices=[
                ("Lihat Request", "1"),
                ("Update Request", "2"),
                ("Logout", "3"),
            ],
        )
    ]

    jawaban = inquirer.prompt(pertanyaan)
    return jawaban["pilihan"] if jawaban else "3"


def get_menunggu_request():
    clear()

    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                r.request_id,
                u.nama AS nama_warga,
                u.no_telepon,
                r.alamat,
                r.tanggal_pengajuan,
                r.status
            FROM requests r
            JOIN users u ON r.user_id = u.user_id
            WHERE r.status = 'menunggu'
            ORDER BY r.tanggal_pengajuan ASC
            """)
        data = cursor.fetchall()

    if not data:
        print("Belum ada request penjemputan yang menunggu.")
        return []

    table = PrettyTable(
        ["ID", "Nama Warga", "No. HP", "Alamat", "Tgl Pengajuan", "Status"]
    )
    table.align["Nama Warga"] = "l"
    table.align["Alamat"] = "l"
    table.align["Tgl Pengajuan"] = "l"
    table.align["Status"] = "l"
    table._max_width = {"Nama Warga": 25, "Alamat": 30}

    for row in data:
        table.add_row(
            [
                row["request_id"],
                row["nama_warga"],
                row["no_telepon"] or "-",
                row["alamat"],
                row["tanggal_pengajuan"],
                row["status"],
            ]
        )
    print(table)
    return data


def edit_requests_petugas():
    clear()

    data = get_menunggu_request()
    if not data:
        print("Tidak ada data yang bisa diubah.")
        enter()
        return

    pesan_error = ""
    while True:
        clear()
        print("=== UPDATE REQUEST PENJEMPUTAN ===")
        get_menunggu_request()
        if pesan_error:
            print(f"\n[!] {pesan_error}")
            pesan_error = ""

        try:
            req_id = int(
                input(
                    "\nMasukkan request_id yang ingin diproses (Tekan 0 untuk kembali ke menu): "
                ).strip()
            )
            if req_id == 0:
                return
            if req_id < 0 or req_id > 9223372036854775807:
                pesan_error = "request_id tidak valid atau terlalu besar!"
                continue
        except ValueError:
            pesan_error = "request_id harus berupa angka!"
            continue

        try:
            with closing(get_connection()) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT r.request_id, r.status, r.alamat, r.tanggal_pengajuan, u.nama AS nama_warga
                    FROM requests r
                    JOIN users u ON r.user_id = u.user_id
                    WHERE r.request_id = ?
                    """,
                    (req_id,),
                )
                req_target = cursor.fetchone()
        except sqlite3.Error as e:
            print(f"\nTerjadi kesalahan pada database: {e}")
            enter()
            return

        if not req_target:
            pesan_error = f"Request dengan ID {req_id} tidak ditemukan!"
            continue

        if req_target["status"] != "menunggu":
            pesan_error = f"Request #{req_id} sudah berstatus '{req_target['status']}' dan tidak bisa diproses lagi!"
            continue

        break

    pertanyaan_status = [
        inquirer.List(
            "status",
            message=f"Pilih status baru untuk request #{req_id} ({req_target['nama_warga']})",
            choices=[
                ("Selesai", "selesai"),
                ("Ditolak", "ditolak"),
                ("Kembali", "kembali"),
            ],
        )
    ]
    jawaban_status = inquirer.prompt(pertanyaan_status)
    status_baru = jawaban_status["status"] if jawaban_status else "kembali"

    if status_baru == "kembali":
        enter()
        return

    tanggal_jemput = None
    berat = None
    catatan = None

    if status_baru == "selesai":
        pesan_error = ""
        while True:
            clear()
            print(f"=== PROSES REQUEST #{req_id} (SELESAI) ===")
            print(f"Warga  : {req_target['nama_warga']}")
            print(f"Alamat : {req_target['alamat']}\n")
            if pesan_error:
                print(f"[!] {pesan_error}\n")
                pesan_error = ""

            berat_input = (
                input("Masukkan berat sampah (kg, >0-250): ").strip().replace(",", ".")
            )
            try:
                berat = float(berat_input)
                if not math.isfinite(berat) or not (0 < berat <= 250):
                    pesan_error = "Berat sampah harus di atas 0 hingga 250 kg."
                    continue
                berat = round(berat, 2)
                break
            except ValueError:
                pesan_error = "Input tidak valid, harap masukkan angka."

        pesan_error = ""
        while True:
            clear()
            print(f"=== PROSES REQUEST #{req_id} (SELESAI) ===")
            print(f"Warga  : {req_target['nama_warga']}")
            print(f"Berat  : {berat} kg\n")
            if pesan_error:
                print(f"[!] {pesan_error}\n")
                pesan_error = ""

            catatan = input(
                "Masukkan catatan dari penjemputan (maks 250 karakter, kosongkan untuk default): "
            ).strip()
            if len(catatan) > 250:
                pesan_error = "Catatan maksimal 250 karakter. Silakan ulangi."
                continue
            if not catatan:
                catatan = "Sampah telah dijemput dan ditimbang"
            break

        tanggal_jemput = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    elif status_baru == "ditolak":
        pesan_error = ""
        while True:
            clear()
            print(f"=== PROSES REQUEST #{req_id} (DITOLAK) ===")
            print(f"Warga  : {req_target['nama_warga']}")
            print(f"Alamat : {req_target['alamat']}\n")
            if pesan_error:
                print(f"[!] {pesan_error}\n")
                pesan_error = ""

            catatan = input("Masukkan alasan penolakan (maks 250 karakter): ").strip()

            if not any(c.isalpha() for c in catatan):
                    pesan_error = "Alasan penolakan harus berupa kalimat yang jelas (mengandung huruf)!"
                    continue
                    
            if not catatan:
                pesan_error = "Input tidak boleh kosong."
                continue
            if len(catatan) > 250:
                pesan_error = "Alasan penolakan maksimal 250 karakter. Silakan ulangi."
                continue
            break

    try:
        with closing(get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE requests
                SET status = ?, berat_sampah = ?, catatan = ?, tanggal_penjemputan = ?
                WHERE request_id = ? AND status = 'menunggu'
                """,
                (status_baru, berat, catatan, tanggal_jemput, req_id),
            )

            if cursor.rowcount == 0:
                print("Request tidak ditemukan atau sudah diproses")
                enter()
                return

            conn.commit()

            print(
                f"\n[SUKSES] request #{req_id} berhasil diupdate menjadi '{status_baru}'"
            )
            if berat is not None:
                print(f"Total berat: {berat} kg")
            enter()

    except sqlite3.Error as e:
        print(f"Terjadi kesalahan pada database: {e}")
        enter()
        return


def jalankan_menu_petugas():
    while True:
        pilihan = menu_petugas()
        if pilihan == "1":
            get_menunggu_request()
            enter()
        elif pilihan == "2":
            edit_requests_petugas()
        elif pilihan == "3":
            print("\nLogout berhasil.")
            logout()
            break


if __name__ == "__main__":
    jalankan_menu_petugas()
