from .database import init_db


def main() -> None:
    init_db()
    
    print("=== SPPSM ===")
    print("Database berhasil disiapkan!")
    
if __name__ == "__main__":
    main()
