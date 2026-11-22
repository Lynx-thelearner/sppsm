import os
import sqlite3

from .utils import hash_password

db_name = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "sppsm.db"
)


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
                tanggal_penjemputan TEXT,
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
            (
                "Fysortheguy",
                hash_password("hafizh123"),
                "Hafizh",
                "Kantor",
                "081223548632",
                "admin",
            ),
            (
                "Tomgun",
                hash_password("tom123"),
                "Tommy",
                "Kantor",
                "0838557891012",
                "petugas",
            ),
            (
                "BennyAdventureTeam",
                hash_password("ben123"),
                "Bennet",
                "Blok A",
                "083855754782",
                "warga",
            ),
            (
                "lynxstilllearning",
                hash_password("lynxlynxy"),
                "Lynx",
                "Blok CX",
                "081235754782",
                "warga",
            ),
            (
                "kikirakira",
                hash_password("kiki123"),
                "Kiki",
                "Blok B",
                "083985754782",
                "warga",
            ),
        ]
        cursor.executemany(
            "INSERT INTO users (username, password, nama, alamat, no_telepon, role) VALUES (?, ?, ?, ?, ?, ?)",
            initial_users,
        )

    
# Seeding table requests
    cursor.execute("SELECT COUNT(*) FROM requests")
    
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            SELECT user_id, alamat
            FROM users
            WHERE role = 'warga'
            ORDER BY
                CASE
                    WHEN username = 'BennyAdventureTeam' THEN 0
                    ELSE 1
                END,
                user_id ASC
            LIMIT 3
        """)
    
        user_warga = cursor.fetchall()
    
        if user_warga:
            initial_requests = []
    
            data_requests = [
                (
                    "2026-11-20 08:30:00",
                    None,
                    None,
                    "menunggu",
                    "Sampah daun dan ranting di depan pagar",
                ),
                (
                    "2026-11-21 09:15:00",
                    None,
                    None,
                    "menunggu",
                    "Sampah kardus dan plastik",
                ),
                (
                    "2026-11-18 10:00:00",
                    "2026-11-18 11:30:00",
                    6.5,
                    "selesai",
                    "Sampah telah dijemput dan ditimbang",
                ),
                (
                    "2026-11-17 14:00:00",
                    None,
                    None,
                    "ditolak",
                    "Lokasi tidak dapat diakses kendaraan",
                ),
            ]
    
            for i, request in enumerate(data_requests):
                user = user_warga[i % len(user_warga)]
    
                initial_requests.append((
                    user["user_id"],
                    request[0],
                    request[1],
                    request[2],
                    user["alamat"],
                    request[3],
                    request[4],
                ))
    
            cursor.executemany("""
                INSERT INTO requests (
                    user_id,
                    tanggal_pengajuan,
                    tanggal_penjemputan,
                    berat_sampah,
                    alamat,
                    status,
                    catatan
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, initial_requests)

    conn.commit()
    conn.close()
