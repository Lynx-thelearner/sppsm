import pwinput
from .database import users, session

def login():
    print("\n" + "=" * 30)
    print("LOGIN MENU")
    print("=" * 30) 

    username = input("Enter your username: ")

    if username not in users:
        print("User does not exist. Please register first.")
        return False

    password = pwinput.pwinput(prompt="Enter your password: ", mask="*")

    if users[username]["password"] == password:
        session["username"] = username
        session["role"] = users[username]["role"]
        session["is_login"] = True  

        print(f"\nLogin successful! Welcome, {username}.")
        print(f"Your role is: {session['role'].capitalize()}")
        return True
    else:
        print("Incorrect password. Please try again.")
        return False


def register():
    print("\n" + "=" * 30)
    print("REGISTRATION MENU")
    print("=" * 30) 

    username = input("Enter a username: ")

    if username in users:
        print("Username already exists. Please choose a different username.")
        return False

    password = pwinput.pwinput(prompt="Enter a password: ", mask="*")
    confirm_password = pwinput.pwinput(prompt="Confirm your password: ", mask="*")

    if password != confirm_password:
        print("Passwords do not match. Please try again.")
        return False

    print("\n--- Data Lokasi ---")
    blok = input("Enter your Block (e.g., A): ").upper()
    no_rumah = input("Enter your House Number (e.g., 12): ")

    lokasi_lengkap = f"Blok {blok} No. {no_rumah}"

    users[username] = {
        "password": password,
        "role": "warga",
        "lokasi": lokasi_lengkap
    }
    
    print(f"\nRegistration successful! You can now log in as {username}.")
    print(f"📍 Your registered location: {lokasi_lengkap}")
    return True