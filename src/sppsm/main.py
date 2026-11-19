import sys

from .admin import run_admin
from .auth import auth_menu, login, register, session
from .database import init_db
from .petugas import jalankan_menu_petugas
from .users import menu_crud_user
from .utils import clear


def main() -> None:
    init_db()

    while True:
        clear()
        print("=== Sistem Pengelolaan Penjemputan Sampah Mandiri ===")

        if session["is_login"]:
            role = session["role"]
            if role == "admin":
                run_admin()
            elif role == "petugas":
                jalankan_menu_petugas()
            elif role == "warga":
                pass
        else:
            pilihan = auth_menu()
            if pilihan == "1":
                login()
            elif pilihan == "2":
                register()
            elif pilihan == "3":
                sys.exit()
