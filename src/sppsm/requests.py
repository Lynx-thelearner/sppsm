<<<<<<< HEAD
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


# Ini untuk menampilkan daftar user yang bisa dipilih sebagai pengaju
def _tampilkan_daftar_user():
    conn = get_connection()
    try:
        users = conn.execute(
            "SELECT user_id, username, nama, alamat, role FROM users"
        ).fetchall()
    finally:
        conn.close()

    if not users:
        return []

    print("\n--- Daftar User Tersedia ---")
    for u in users:
        print(
            f"ID: {u['user_id']} | Username: {u['username']} | Nama: {u['nama']} | Role: {u['role']}"
        )
    return users


# Tampilkan Requests (Read)
def read_requests():
    clear()
    data = get_requests()
    if not data:
        print("\nBelum ada data request penjemputan sampah di database.")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    tabel = PrettyTable()
    tabel.field_names = [
        "ID",
        "Pengaju",
        "Tgl Pengajuan",
        "Jadwal Jemput",
        "Berat (kg)",
        "Alamat",
        "Status",
        "Catatan",
    ]
    tabel.align["Pengaju"] = "l"
    tabel.align["Tgl Pengajuan"] = "l"
    tabel.align["Jadwal Jemput"] = "l"
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
                r["jadwal_penjemputan"] or "-",
                berat,
                r["alamat"],
                r["status"],
                r["catatan"] or "-",
            ]
        )

    print("\n=== DAFTAR REQUEST PENJEMPUTAN SAMPAH ===")
    print(tabel)
    input("\nTekan Enter untuk kembali ke menu...")


# Buat Request Baru (Create)
def create_request():
    clear()
    print("\n=== BUAT REQUEST PENJEMPUTAN BARU ===")
    print("(Ketik '0' pada user_id untuk kembali ke menu)\n")

    users = _tampilkan_daftar_user()
    if not users:
        print("Belum ada user di database. Buat user terlebih dahulu!")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    # Pilih user_id pengaju
    while True:
        try:
            user_id = int(input("\nMasukkan user_id pengaju (0 untuk batal): ").strip())
            if user_id == 0:
                return
            if user_id < 0 or user_id > 9223372036854775807:
                print("user_id tidak valid atau terlalu besar!")
                continue
        except ValueError:
            print("user_id harus berupa angka!")
            continue

        conn = get_connection()
        user_target = conn.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        conn.close()

        if not user_target:
            print(f"User dengan ID {user_id} tidak ditemukan!")
        else:
            break

    # Tanggal pengajuan (otomatis waktu sekarang atau custom)
    waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tgl_input = input(f"Tanggal pengajuan [Enter untuk '{waktu_sekarang}']: ").strip()
    tanggal_pengajuan = tgl_input if tgl_input else waktu_sekarang

    # Jadwal penjemputan (opsional)
    jadwal_input = input(
        "Jadwal penjemputan (Contoh: 2026-11-20 09:00:00, Enter jika belum ada): "
    ).strip()
    jadwal_penjemputan = jadwal_input if jadwal_input else None

    # Berat sampah (opsional, >= 0)
    while True:
        berat_input = input(
            "Perkiraan berat sampah dalam kg (Opsional, Enter jika kosong): "
        ).strip()
        if not berat_input:
            berat_sampah = None
            break
        try:
            berat_sampah = float(berat_input)
            if berat_sampah < 0:
                print("Berat sampah tidak boleh negatif!")
                continue
            break
        except ValueError:
            print("Berat sampah harus berupa angka (contoh: 2.5)!")

    # Alamat penjemputan (default ambil dari alamat user)
    alamat_input = input(
        f"Alamat penjemputan [Enter untuk '{user_target['alamat']}']: "
    ).strip()
    alamat = alamat_input if alamat_input else user_target["alamat"]

    # Status request
    pertanyaan_status = [
        inquirer.List(
            "status",
            message="Pilih status awal request:",
            choices=["menunggu", "selesai", "ditolak", "dibatalkan"],
        )
    ]
    jawaban_status = inquirer.prompt(pertanyaan_status)
    status = jawaban_status["status"] if jawaban_status else "menunggu"

    # Catatan (opsional)
    catatan = input("Catatan tambahan (Opsional, Enter jika kosong): ").strip()

    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO requests (
                user_id, tanggal_pengajuan, jadwal_penjemputan,
                berat_sampah, alamat, status, catatan
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                tanggal_pengajuan,
                jadwal_penjemputan,
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
    clear()
    print("\n=== UPDATE DATA REQUEST ===")
    data = get_requests()
    if not data:
        print("Belum ada data request di database.")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    for r in data:
        nama_user = r["username"] or f"ID:{r['user_id']}"
        print(
            f"ID: {r['request_id']} | Pengaju: {nama_user} | Tgl: {r['tanggal_pengajuan']} | Status: {r['status']}"
        )

    while True:
        try:
            target_id = int(
                input(
                    "\nMasukkan request_id yang ingin diupdate (Tekan 0 untuk kembali ke menu): "
                ).strip()
            )
            if target_id == 0:
                return
            if target_id < 0 or target_id > 9223372036854775807:
                print("request_id tidak valid atau terlalu besar!")
                continue
            break
        except ValueError:
            print("request_id harus berupa angka!")

    conn = get_connection()
    req_lama = conn.execute(
        "SELECT * FROM requests WHERE request_id = ?", (target_id,)
    ).fetchone()
    conn.close()

    if not req_lama:
        print(f"Request dengan ID {target_id} tidak ditemukan!")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    # Simpan nilai sementara sebelum disimpan permanen
    user_id_baru = req_lama["user_id"]
    tgl_pengajuan_baru = req_lama["tanggal_pengajuan"]
    jadwal_baru = req_lama["jadwal_penjemputan"]
    berat_baru = req_lama["berat_sampah"]
    alamat_baru = req_lama["alamat"]
    status_baru = req_lama["status"]
    catatan_baru = req_lama["catatan"]

    while True:
        clear()
        # Ambil username terbaru sesuai user_id_baru
        conn = get_connection()
        u_info = conn.execute(
            "SELECT username, nama FROM users WHERE user_id = ?", (user_id_baru,)
        ).fetchone()
        conn.close()
        label_pengaju = (
            f"{u_info['nama']} ({u_info['username']}) [ID: {user_id_baru}]"
            if u_info
            else f"ID: {user_id_baru}"
        )

        print("=== UPDATE DATA REQUEST ===")
        print(f"Request ID         : {target_id}")
        print(f"Pengaju            : {label_pengaju}")
        print(f"Tanggal Pengajuan  : {tgl_pengajuan_baru}")
        print(f"Jadwal Penjemputan : {jadwal_baru or '-'}")
        print(f"Berat Sampah (kg)  : {berat_baru if berat_baru is not None else '-'}")
        print(f"Alamat             : {alamat_baru}")
        print(f"Status             : {status_baru}")
        print(f"Catatan            : {catatan_baru or '-'}")
        print("-" * 45)

        pertanyaan = [
            inquirer.List(
                "kolom",
                message="Pilih data yang ingin diubah:",
                choices=[
                    "1. Pengaju (user_id)",
                    "2. Tanggal Pengajuan",
                    "3. Jadwal Penjemputan",
                    "4. Berat Sampah (kg)",
                    "5. Alamat Penjemputan",
                    "6. Status Request",
                    "7. Catatan",
                    "8. Simpan perubahan dan selesai",
                    "9. Batal (buang perubahan)",
                ],
            )
        ]

        jawaban = inquirer.prompt(pertanyaan)
        pilihan = jawaban["kolom"][0] if jawaban else "9"

        if pilihan == "1":
            _tampilkan_daftar_user()
            while True:
                try:
                    uid_input = int(
                        input("\nMasukkan user_id pengaju yang baru: ").strip()
                    )
                    if uid_input <= 0 or uid_input > 9223372036854775807:
                        print("user_id tidak valid!")
                        continue
                except ValueError:
                    print("user_id harus berupa angka!")
                    continue

                conn = get_connection()
                cek_user = conn.execute(
                    "SELECT 1 FROM users WHERE user_id = ?", (uid_input,)
                ).fetchone()
                conn.close()

                if not cek_user:
                    print(f"User dengan ID {uid_input} tidak ditemukan!")
                else:
                    user_id_baru = uid_input
                    print("Pengaju berhasil diubah sementara.")
                    break

        elif pilihan == "2":
            while True:
                input_tgl = input(
                    "\nMasukkan tanggal pengajuan baru (YYYY-MM-DD HH:MM:SS): "
                ).strip()
                if not input_tgl:
                    print("Tanggal pengajuan tidak boleh kosong!")
                else:
                    tgl_pengajuan_baru = input_tgl
                    print("Tanggal pengajuan berhasil diubah sementara.")
                    break

        elif pilihan == "3":
            input_jadwal = input(
                "\nMasukkan jadwal penjemputan baru (Kosongkan/Enter untuk menghapus jadwal): "
            ).strip()
            jadwal_baru = input_jadwal if input_jadwal else None
            print("Jadwal penjemputan berhasil diubah sementara.")

        elif pilihan == "4":
            while True:
                input_berat = input(
                    "\nMasukkan berat sampah baru dalam kg (Enter untuk mengosongkan): "
                ).strip()
                if not input_berat:
                    berat_baru = None
                    print("Berat sampah dikosongkan sementara.")
                    break
                try:
                    nilai_berat = float(input_berat)
                    if nilai_berat < 0:
                        print("Berat sampah tidak boleh negatif!")
                        continue
                    berat_baru = nilai_berat
                    print("Berat sampah berhasil diubah sementara.")
                    break
                except ValueError:
                    print("Berat sampah harus berupa angka!")

        elif pilihan == "5":
            while True:
                input_alamat = input("\nMasukkan alamat penjemputan baru: ").strip()
                if not input_alamat:
                    print("Alamat tidak boleh kosong!")
                else:
                    alamat_baru = input_alamat
                    print("Alamat berhasil diubah sementara.")
                    break

        elif pilihan == "6":
            tanya_status = [
                inquirer.List(
                    "status_baru",
                    message="Pilih status baru:",
                    choices=["menunggu", "selesai", "ditolak", "dibatalkan"],
                )
            ]
            jwb_status = inquirer.prompt(tanya_status)
            if jwb_status:
                status_baru = jwb_status["status_baru"]
                print(f"Status berhasil diubah sementara menjadi '{status_baru}'.")

        elif pilihan == "7":
            catatan_baru = input(
                "\nMasukkan catatan baru (Enter untuk mengosongkan): "
            ).strip()
            print("Catatan berhasil diubah sementara.")

        elif pilihan == "8":
            break

        elif pilihan == "9":
            print("\nPerubahan dibatalkan. Data tidak disimpan.")
            input("\nTekan Enter untuk kembali ke menu...")
            return

        lanjut = (
            input("\nMasih ingin mengupdate data lainnya pada request ini? [y/n]: ")
            .strip()
            .lower()
        )
        if lanjut != "y":
            break

    # Cek apakah ada data yang benar-benar berubah sebelum menulis ke database
    if (
        user_id_baru == req_lama["user_id"]
        and tgl_pengajuan_baru == req_lama["tanggal_pengajuan"]
        and jadwal_baru == req_lama["jadwal_penjemputan"]
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
            SET user_id = ?,
                tanggal_pengajuan = ?,
                jadwal_penjemputan = ?,
                berat_sampah = ?,
                alamat = ?,
                status = ?,
                catatan = ?
            WHERE request_id = ?
            """,
            (
                user_id_baru,
                tgl_pengajuan_baru,
                jadwal_baru,
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
    clear()
    print("\n=== HAPUS DATA REQUEST ===")
    data = get_requests()
    if not data:
        print("Belum ada data request di database.")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    for r in data:
        nama_user = r["username"] or f"ID:{r['user_id']}"
        print(
            f"ID: {r['request_id']} | Pengaju: {nama_user} | Tgl: {r['tanggal_pengajuan']} | Status: {r['status']}"
        )

    while True:
        try:
            target_id = int(
                input(
                    "\nMasukkan request_id yang ingin dihapus (Tekan 0 untuk kembali ke menu): "
                ).strip()
            )
            if target_id == 0:
                return
            if target_id < 0 or target_id > 9223372036854775807:
                print("request_id tidak valid atau terlalu besar!")
                continue
            break
        except ValueError:
            print("request_id harus berupa angka!")

    conn = get_connection()
    req_target = conn.execute(
        """
        SELECT r.request_id, r.status, r.tanggal_pengajuan, u.username
        FROM requests r
        LEFT JOIN users u ON r.user_id = u.user_id
        WHERE r.request_id = ?
        """,
        (target_id,),
    ).fetchone()
    conn.close()

    if not req_target:
        print(f"Request dengan ID {target_id} tidak ditemukan!")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    pengaju = req_target["username"] or "User tidak diketahui"
    konfirmasi = (
        input(
            f"Yakin ingin menghapus request ID {target_id} milik '{pengaju}' (Status: {req_target['status']})? [y/n]: "
        )
        .strip()
        .lower()
    )
    if konfirmasi != "y":
        print("Penghapusan dibatalkan.")
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
                    "5. Kembali / Keluar",
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
=======
>>>>>>> 14b5a5a (feat: adding functions and detailling on every entities)
