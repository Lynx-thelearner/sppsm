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
            SELECT request_id, tanggal_pengajuan, jadwal_penjemputan, berat_sampah, status, catatan
            FROM requests
            WHERE user_id = ?
            ORDER BY request_id DESCEND
            """,
            (session["user_id"])
        ).fetchall()

    if not requests:
        print("\nBelum ada pengajuan requests")
        enter()