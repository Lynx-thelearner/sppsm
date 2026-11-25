import sys

from .admin import run_admin
from .auth import auth_menu, login, register, session
from .database import init_db
from .petugas import jalankan_menu_petugas
from .utils import clear, enter
from .warga import jalankan_menu_warga


def main() -> None:
    try:
        init_db()

        while True:
            clear()
            print("=== Sistem Pengelolaan Penjemputan Sampah Mandiri ===")

            if session["is_login"]:
                role = session["role"]
                if role == "admin":
                    run_admin(session["user_id"])
                elif role == "petugas":
                    jalankan_menu_petugas()
                elif role == "warga":
                    jalankan_menu_warga()
                else:
                    print(f"\n[!] Role '{role}' tidak dikenali. Sesi akan direset.")
                    session["user_id"] = None
                    session["username"] = None
                    session["nama"] = None
                    session["role"] = None
                    session["alamat"] = None
                    session["no_telepon"] = None
                    session["is_login"] = False
                    enter()
            else:
                pilihan = auth_menu()
                if pilihan == "1":
                    login()
                elif pilihan == "2":
                    register()
                elif pilihan == "3":
                    print("\nSistem keluar, byee")
                    enter()
                    sys.exit()
    except KeyboardInterrupt:
        print("\n\n[!] Program dihentikan. See ya!")


if __name__ == "__main__":
    main()
