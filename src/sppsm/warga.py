import sqlite3
from contextlib import closing
from datetime import datetime

import inquirer
from prettytable import PrettyTable

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

    table = PrettyTable(
        [
            "ID",
            "Tanggal Pengajuan",
            "Tanggal Penjemputan",
            "Status",
            "Berat (kg)",
            "Catatan",
        ]
    )
    for row in requests:
        berat_tampil = row["berat_sampah"] if row["berat_sampah"] is not None else "-"
        table.add_row(
            [
                row["request_id"],
                row["tanggal_pengajuan"],
                row["tanggal_penjemputan"] or "-",
                row["status"],
                berat_tampil,
                row["catatan"] or "-",
            ]
        )
    print(table)
    enter()


def buat_request():
    clear()
    print("=== Buat Requests ===")
    alamat_default = (session["alamat"] or "").strip()
    print(f"Alamat default: {alamat_default or '-'}")

    alamat = None
    while True:
        pilihan_alamat = input("\nGunakan alamat default? [y/n]: ").strip().lower()
        if pilihan_alamat == "y":
            if not alamat_default or not (5 <= len(alamat_default) <= 200):
                print(
                    "\nAlamat default tidak valid (harus 5–200 karakter). Silakan pilih 'n' untuk memasukkan alamat lain."
                )
                enter()
                continue
            alamat = alamat_default
            break
        elif pilihan_alamat == "n":
            alamat_input = input(
                "Masukkan alamat jemput lain (5–200 karakter): "
            ).strip()

            if not alamat_input:
                print("Alamat tidak boleh kosong.")
                enter()
                continue

            if not any(c.isalnum() for c in alamat_input):
                print("Alamat harus mengandung huruf atau angka!")
                enter()
                continue

            if not (5 <= len(alamat_input) <= 200):
                print("Alamat harus terdiri dari 5 hingga 200 karakter.")
                enter()
                continue
            alamat = alamat_input
            break
        else:
            print("\nPilihan hanya 'y' dan 'n'.")
            enter()

    catatan = None
    while True:
        catatan_input = input(
            "Input catatan (Opsional, maksimal 250 karakter): "
        ).strip()
        if len(catatan_input) > 250:
            print("Catatan maksimal 250 karakter. Silakan ulangi.")
            enter()
            continue
        catatan = catatan_input if catatan_input else None
        break

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
                ORDER BY request_id ASC
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
        (
            f"[#{r['request_id']}] Tanggal: {r['tanggal_pengajuan']} - {r['alamat']}",
            r["request_id"],
        )
        for r in requests
    ]
    choices.append(("<< Kembali >>", None))

    pertanyaan = [
        inquirer.List(
            "request_id",
            message="Pilih pengajuan yang ingin dibatalkan:",
            choices=choices,
        )
    ]
    jawaban = inquirer.prompt(pertanyaan)
    req_id = jawaban["request_id"] if jawaban else None

    if req_id is None:
        return

    try:
        with closing(get_connection()) as conn:
            cursor = conn.execute(
                """
                UPDATE requests
                SET status = 'dibatalkan'
                WHERE request_id = ? AND user_id = ? AND status = 'menunggu'
                """,
                (req_id, session["user_id"]),
            )
            if cursor.rowcount == 0:
                print("\nPengajuan tidak ditemukan atau statusnya sudah berubah.")
                enter()
                return

            conn.commit()
            print(f"\n[Sukses] Pengajuan #{req_id} berhasil dibatalkan")
            enter()
    except sqlite3.Error as e:
        print("Ada kesalahan:", e)
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
