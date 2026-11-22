import sqlite3
from contextlib import closing
from datetime import datetime

import inquirer
from prettytable.prettytable import PrettyTable

from .auth import logout, session
from .database import get_connection
from .utils import clear, enter


def menu_warga():
    clear()
    pertanyaan = [
        inquirer.List(
            "pilihan",
            message="=== Menu Warga ===",
            choices=[
                ("Buat Requests", "1"),
                ("Lihat Status dan Riwayat Pengajuan", "2"),
                ("Batalkan Pengajuan", "3"),
                ("Logout", "4"),
            ],
        )
    ]
    jawaban = inquirer.prompt(pertanyaan)
    return jawaban["pilihan"] if jawaban else "4"


def lihat_riwayat():
    clear()
    print("=== Lihat Riwayat Pengajuan ===")

    with closing(get_connection()) as conn:
        requests = conn.execute(
            """
            SELECT request_id, tanggal_pengajuan, tanggal_penjemputan, berat_sampah, status, catatan
            FROM requests
            WHERE user_id = ?
            ORDER BY request_id DESC
            """,
            (session["user_id"],),
        ).fetchall()

    if not requests:
        print("\nBelum ada pengajuan requests")
        enter()
        return

    table = PrettyTable(["ID", "Tanggal Pengajuan", "Tanggal Penjemputan", "status", "Berat (kg)", "Catatan"])
    for i in requests:
        table.add_row([
            i["request_id"],
            i["tanggal_pengajuan"],
            i["tanggal_penjemputan"] or "-",
            i["status"],
            i["berat_sampah"] or "-",
            i["catatan"] or "-"
        ])
    print(table)
    enter() 

def buat_request():
    clear()
    print("=== Buat Requests ===")
    alamat_default = session["alamat"] or ""
    print(f"Alamat default {alamat_default}")

    while True:
        default = input("Gunakan alamat default?: [y/t]").strip().lower()
        if default == "y":
            alamat = alamat_default
            break
        elif default == "t":
            alamat = input("Masukkan alamat jemput lain: ").strip()
            if not alamat:
                print("Alamat tidak boleh kosong")
                return
            break
        else:
            input("Pilihan hanya 'y' dan 't'") 

    catatan = input("Input catatan, (Opsional)")
    tanggal_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with closing(get_connection()) as conn:
        try:
            conn.execute(
                            """
                            INSERT INTO requests (user_id, tanggal_pengajuan, alamat, status, catatan)
                            VALUES (?, ?, ?, 'menunggu', ?)
                            """,
                            (session["user_id"], tanggal_sekarang, alamat, catatan),
                        )
            conn.commit()
            print("\n[Sukses] Pengajuan penjemputan berhasil dibuat!")
        except sqlite3.Error as e:
            print(f"\n[Gagal] Terjadi kesalahan: {e}")

    enter()

def batalkan_request():
    clear()
    print("=== Batalkan Pengajuan ===")

    try:
        with closing(get_connection()) as conn:
            requests = conn.execute(
                """
                SELECT request_id, tanggal_pengajuan, alamat
                FROM requests
                WHERE user_id = ? AND status = 'menunggu'
                """,
                (session["user_id"],),
            ).fetchall()

    except sqlite3.Error as e:
        print(f"Terjadi kesalahan: {e}")
        enter()
        return

    if not requests:
        print("\nTidak ada pengajuan aktif yang bisa dibatalkan")
        enter()
        return

    choices = [
        (f"[#{r['request_id']} Tanggal: {r['tanggal_pengajuan']} - {r['alamat']}:", r["request_id"])
        for r in requests
    ]
    choices.append(("<< Kembali >> ", None))

    pertanyaan = [
        inquirer.List(
            "request_id",
            message="Pilih pengajuan yang ingin dibatalkan:",
            choices=choices
        )
    ]
    jawaban = inquirer.prompt(pertanyaan)
    req_id = jawaban["request_id"] if jawaban else None

    if req_id is None:
        return

    try:
        with closing(get_connection()) as conn:
            conn.execute("""
                UPDATE requests
                SET status = 'dibatalkan'
                WHERE request_id = ? AND user_id = ?
                """, (req_id, session["user_id"])
            )

            conn.commit()
            print(f"\n[Sukses] Pengajuan #{req_id} berhasil dibatalkan")
            enter()
    except sqlite3.Error as e:
        print("Ada kesalahan", e)
        enter()

def jalankan_menu_warga():
    while True:
        pilihan = menu_warga()
        if pilihan == "1":
            buat_request()
        elif pilihan == "2":
            lihat_riwayat()
        elif pilihan == "3":
            batalkan_request()
        elif pilihan == "4":
            logout()
            break

if __name__ == "__main__":
   jalankan_menu_warga() 
        
            

        