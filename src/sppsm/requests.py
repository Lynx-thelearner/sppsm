from .utils import clear
import inquirer, os
from .database import request, request_counter
from prettytable import PrettyTable

def menu_request():
    os.system(clear)

    pertanyaan = [
        inquirer.List(
            'pilihan',
            message="=== Pilih Menu Request ===",
            choices=[
                '1. Buat request pengambilan',
                '2. Batalkan request pengambilan',
                '3. Lihat history pengambilan',
                '4. Kembali'
            ]
        )
    ]

    jawaban = inquirer.prompt(pertanyaan)
    return jawaban['pilihan'][0] if jawaban else '4'

def get_all_requests():
    os.system(clear)

    if not request:
        print("Tidak ada requests")
        return

    table = PrettyTable([
        "ID",
        "Username",
        "Jadwal Pengajuan",
        "Jadwal Pengambilan",
        "Status",
        "Catatan",
        "Berat (kg)"
    ])

    for rid, rdata in request.items():

        pengajuan = rdata["jadwal_pengajuan"]
        pengambilan = rdata["jadwal_pengambilan"]

        jadwal_pengajuan = (
            f"{pengajuan['tanggal']} "
            f"{pengajuan['waktu'][:5]}"
        )

        if pengambilan["tanggal"] is not None:
            jadwal_pengambilan = (
                f"{pengambilan['tanggal']} "
                f"{pengambilan['waktu'][:5]}"
            )
        else:
            jadwal_pengambilan = "Belum dijadwalkan"

        table.add_row([
            rid,
            rdata["username"],
            jadwal_pengajuan,
            jadwal_pengambilan,
            rdata["status"],
            rdata["catatan"] or "-",
            rdata["berat_sampah"]
        ])

    print(table)

def create_request(username):
    os.system(clear)
    print("="*20)


if __name__ == "__main__":
        hasil = get_all_requests()
        print(hasil)
    