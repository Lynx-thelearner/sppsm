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
    else:
        table = PrettyTable(
            ["ID", "Nama Warga", "No. HP", "Alamat", "Tgl Pengajuan", "Status"]
        )
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

    choices_request = [
        (
            f"[#{row['request_id']}] {row['nama_warga']} - {row['alamat']} ({row['tanggal_pengajuan']})",
            row["request_id"],
        )
        for row in data
    ]

    choices_request.append(("<< Kembali >>", None))

    pertanyaan_pilih = [
        inquirer.List(
            "request_id",
            message="=== Pilih request yang ingin diproses ===",
            choices=choices_request,
        )
    ]
    jawaban_pilih = inquirer.prompt(pertanyaan_pilih)

    if not jawaban_pilih or jawaban_pilih["request_id"] is None:
        print("Dibatalkan")
        enter()
        return

    req_id = jawaban_pilih["request_id"]

    pertanyaan_status = [
        inquirer.List(
            "status",
            message=f"Pilih status baru untuk request #{req_id}",
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
        input("Tekan Enter untuk kembali...")
        return
    
    tanggal_jemput = None    
    berat = None
    catatan = None

    if status_baru == "selesai":
        while True:
            try:
                berat_input = (
                    input("Masukkan berat sampah (kg): ").strip().replace(",", ".")
                )
                berat = float(berat_input)
                if not math.isfinite(berat) or not (0 < berat <= 200):
                    print("Berat sampah harus diatas 0 hingga 200")
                    continue
                break
            except ValueError:
                print("Input tidak valid, harap masukkan angka.")
                
        catatan = input("Masukkan catatan dari penjemputan (kosongkan untuk default): ").strip()
        if not catatan:
            catatan = "Sampah telah dijemput dan ditimbang"
            
        tanggal_jemput = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    elif status_baru == "ditolak":
        while True:
            catatan = input("Masukkan alasan penolakan: ").strip()
            if not catatan:
                print("Input tidak boleh kosong")
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
    
            print(f"\n[SUKSES] request #{req_id} berhasil diupdate menjadi '{status_baru}'")
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
            input("\nTekan Enter untuk kembali...")
        elif pilihan == "2":
            edit_requests_petugas()
        elif pilihan == "3":
            print("\nLogout berhasil.")
            logout()
            break


if __name__ == "__main__":
    jalankan_menu_petugas()
