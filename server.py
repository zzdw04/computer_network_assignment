import asyncio
import os
import utils

from file_manager import *
from request_handler import *


# 각종 예외상황 에러 등 생각해서 구현 해야 함!!

# 서버 설정
host = '127.0.0.1'  # local
port = 12345

# 폴더 관련 코드들
os.makedirs("files", exist_ok=True)
utils.FM = None
utils.FM = fileManager()

async def handle_connection(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"{addr}에서 연결됨")

    try:
        await handle_client(reader, writer)  # 비동기 client 핸들링
    except Exception as e:
        print(f"에러 발생: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_connection, host, port)
    print("서버 대기중....")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())