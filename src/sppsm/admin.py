import inquirer

from .auth import logout
from .users import menu_crud_user
from .utils import clear, enter


def menu_admin():
    pertanyaan = [
        inquirer.List(
            "pilihan",
            message="=== Pilih Menu Admin",
            choices=[
                ("Users", "1"),
                ("Requests", "2"),
                ("Logout", "3"),
            ],
        )
    ]

    jawaban = inquirer.prompt(pertanyaan)
    return jawaban["pilihan"] if jawaban else "3"


def run_admin():
    clear()

    jawaban = menu_admin()
    if jawaban == "1":
        menu_crud_user()
    elif jawaban == "2":
        enter()
    elif jawaban == "3":
        logout()
