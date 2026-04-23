# -*- coding: utf-8 -*-
# Утилита для загрузки Kayhon.xlsx на сервер через SFTP.
# Заполните SERVER_* значениями вашего сервера перед запуском.

import os
from pathlib import Path

import paramiko

SERVER_HOST = "your_server_ip"
SERVER_PORT = 22
SERVER_USERNAME = "your_username"
SERVER_PASSWORD = "your_password"
# SSH_KEY_PATH = "/path/to/your/private/key"

BASE_DIR = Path(__file__).resolve().parent
LOCAL_FILE_PATH = str(BASE_DIR / "Kayhon.xlsx")
REMOTE_FILE_PATH = "/path/to/your/server/directory/Kayhon.xlsx"


def upload_file() -> None:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(
            SERVER_HOST,
            port=SERVER_PORT,
            username=SERVER_USERNAME,
            password=SERVER_PASSWORD,
        )
        # Вариант с ключом вместо пароля:
        # ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USERNAME, key_filename=SSH_KEY_PATH)

        with ssh.open_sftp() as sftp:
            print(f"Uploading {LOCAL_FILE_PATH} to {REMOTE_FILE_PATH}...")
            sftp.put(LOCAL_FILE_PATH, REMOTE_FILE_PATH)
            print("File uploaded successfully!")
    except Exception as e:
        print(f"Error uploading file: {e}")
    finally:
        ssh.close()


if __name__ == "__main__":
    if not os.path.exists(LOCAL_FILE_PATH):
        print(f"Local file {LOCAL_FILE_PATH} not found!")
    else:
        upload_file()
