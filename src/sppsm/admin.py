import inquirer

from .auth import logout
from .requests import menu_crud_requests
from .users import menu_crud_user
from .utils import clear


def menu_admin():
    pertanyaan = [
        inquirer.List(
            "pilihan",
            message="=== Pilih Menu Admin ===",
            choices=[
                ("Users", "1"),
                ("Requests", "2"),
                ("Logout", "3"),
            ],
        )
    ]

    jawaban = inquirer.prompt(pertanyaan)
    return jawaban["pilihan"] if jawaban else "3"


def run_admin(current_user_id=None):
    while True:
        clear()

        jawaban = menu_admin()
        if jawaban == "1":
            menu_crud_user(current_user_id)
        elif jawaban == "2":
            menu_crud_requests()
        elif jawaban == "3":
            logout()
            break


if __name__ == "__main__":
    run_admin()
