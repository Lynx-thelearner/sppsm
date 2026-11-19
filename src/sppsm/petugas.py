import math
from contextlib import closing

import inquirer
from prettytable import PrettyTable

from .auth import logout
from .database import get_connection
from .utils import clear


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
        input("\n Tekan untuk melanjutkan")
        return

    choices_request = [
        (
            f"[#{row['request_id']}] {row['nama_warga']} - {row['alamat']} ({row['tanggal_pengajuan']})",
            row["request_id"],
        )
        for row in data
    ]

    choices_request.append(("<< Batal >>", None))

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
        input("\nTekan untuk melanjutkan.")
        return

    req_id = jawaban_pilih["request_id"]

    pertanyaan_status = [
        inquirer.List(
            "status",
            message=f"Pilih status baru untuk request #{req_id}",
            choices=["selesai", "ditolak", "Batalkan"],
        )
    ]
    jawaban_status = inquirer.prompt(pertanyaan_status)
    status_baru = jawaban_status["status"] if jawaban_status else "Batalkan"

    if status_baru == "Batalkan":
        print("Proses dibatalkan.")
        input("Tekan Enter untuk kembali...")
        return

    berat = None
    catatan = None

    if status_baru == "selesai":
        while True:
            try:
                berat_input = (
                    input("Masukkan berat sampah (kg): ").strip().replace(",", ".")
                )
                berat = float(berat_input)
                if not math.isfinite(berat) or berat <= 0:
                    print("Berat sampah harus diatas 0")
                    continue
                break
            except ValueError:
                print("Input tidak valid, harap masukkan angka.")
        catatan = "Sampah telah dijemput dan ditimbang"

    elif status_baru == "ditolak":
        while True:
            catatan = input("Masukkan alasan penolakan: ").strip()
            if not catatan:
                print("Input tidak boleh kosong")
                continue
            break

    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE requests
            SET status = ?, berat_sampah = ?, catatan = ?
            WHERE request_id = ? AND status = 'menunggu'
            """,
            (status_baru, berat, catatan, req_id),
        )

        if cursor.rowcount == 0:
            print("Request tidak ditemukan atau sudah diproses")
            input("\nTekan Enter untuk kembali...")
            return

        conn.commit()

    print(f"\n[SUKSES] request #{req_id} berhasil diupdate menjadi '{status_baru}'")
    if berat is not None:
        print(f"Total berat: {berat} kg")
    input("\nTekan Enter untuk kembali menu...")


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
