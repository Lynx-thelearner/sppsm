import sqlite3
from .utils import hash_password

db_name = "sppsm.db"


def get_connection():
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                nama TEXT NOT NULL,
                alamat TEXT NOT NULL,
                no_telepon TEXT,
                role TEXT NOT NULL
                CHECK (
                    role IN (
                        'admin',
                        'petugas',
                        'warga'
                    )
                )
            )
        """)

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                tanggal_pengajuan TEXT NOT NULL,
                jadwal_penjemputan TEXT,
                berat_sampah REAL CHECK ( berat_sampah >= 0),
                alamat TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'menunggu'
                CHECK (
                    status IN (
                        'menunggu',
                        'selesai',
                        'ditolak',
                        'dibatalkan'
                    )
                ),
                catatan TEXT,
    
                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
        """)

    # seeding table users
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        initial_users = [
            ("Fysortheguy", hash_password("hafizh123"), "Hafizh", "Kantor", "081223548632", "admin"),
            ("Tomgun", hash_password("tom123"), "Tommy", "Kantor", "0838557891012", "petugas"),
            ("BennyAdventureTeam", hash_password("ben123"), "Bennet", "Blok A", "083855754782", "warga"),
        ]
        cursor.executemany(
            "INSERT INTO users (username, password, nama, alamat, no_telepon, role) VALUES (?, ?, ?, ?, ?, ?)",
            initial_users,
        )

    # seeding table requests
    cursor.execute("SELECT COUNT(*) FROM requests")
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT user_id, alamat FROM users WHERE username = ?", ("BennyAdventureTeam",))
        user = cursor.fetchone()

        if user:
            cursor.execute(
                """
                INSERT INTO requests (user_id, tanggal_pengajuan, jadwal_penjemputan, berat_sampah, alamat, status, catatan)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user["user_id"],
                    "2026-11-06 22:53:13",
                    "2026-11-06 23:10:15",
                    5.0,
                    user["alamat"],
                    "selesai",
                    "",
                ),
            )

    conn.commit()
    conn.close()