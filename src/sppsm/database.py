users = {
    "Hafizh": {"password": "hafizh123", "role": "admin", "lokasi": "Kantor"},
    "Tom": {
        "password": "tom123",
        "role": "petugas",  # role/peran user
        "lokasi": "Kantor",  # lokasi user
    },
    "Ben": {"password": "ben123", "role": "warga", "lokasi": "Blok A"},
}

request = {
    1: {
        "username": "Ben",
        "jadwal": {
            "tanggal": "2026-11-06",
            "waktu": "22:53:13.657630",
        },
        "status": "selesai",  # status request dari warga, selesai = sudah selesai, dll
        "catatan": "",
        "berat_sampah": 5,  # satuan berat kg secara default
    }
}

request_counter = 2

session = {"username": None, "role": None, "is_login": False}
# Buat bersama
