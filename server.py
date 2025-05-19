import asyncio
import os

from file_manager import *
from request_handler import *
from utils import *

# 각종 예외상황 에러 등 생각해서 구현 해야 함!!

# 서버 설정
host = '127.0.0.1'  # local
port = 12345

# 폴더 관련 코드들
directory = "./files/"
os.makedirs("files", exist_ok=True)
FM = fileManager()


async def main():
    # 소켓 만들기 AF_INET : ipv4, SOCK_STREAM : TCP 통신
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    print("서버 대기중....")


    # 이거 비동기로 만들어야 함...
    while True:
        client_socket, addr = server_socket.accept()
        print(f"{addr}에서 연결됨")

        handle_client(client_socket, addr)
        client_socket.close()
