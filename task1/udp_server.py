import socket
import json
from pathlib import Path
from datetime import datetime

STORAGE = Path("storage")
STORAGE.mkdir(exist_ok=True)
DATA_FILE = STORAGE / "data.json"

def run_udp_server(host="127.0.0.1", port=5000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    print(f"UDP сервер запущений {host}:{port}")

    while True:
        data, addr = sock.recvfrom(1024)
        message = data.decode("utf-8")
        print(f"Отримано від {addr}: {message}")

        try:
            data_dict = json.loads(message)
        except json.JSONDecodeError:
            continue

        # Читаємо старі дані
        if DATA_FILE.exists():
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                old_data = json.load(f)
        else:
            old_data = {}

        # Додаємо нові
        date_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        old_data[date_stamp] = data_dict

        # Записуємо назад
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(old_data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    run_udp_server()
