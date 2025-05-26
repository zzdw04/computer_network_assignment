import asyncio
import os
import utils
import sys

from file_manager import *
from request_handler import *

async def handle_connection(reader, writer):
    global connectedClients, connected, closeEvent
    addr = writer.get_extra_info('peername')
    print(f"{addr}에서 연결됨")

    connectedClients += 1
    connected = True

    print(f"현재 연결된 클라이언트 수 : {connectedClients}")
    try:
        await handle_client(reader, writer)  # 비동기 client 핸들링
    except Exception as e:
        print(f"에러 발생: {e}")
    finally:
        connectedClients -= 1
        try:
            writer.close()
            print(f"현재 연결된 클라이언트 수 : {connectedClients}")
            await writer.wait_closed()
        except Exception as e:
            pass

    if connectedClients == 0 and connected:
            closeEvent.set()

async def main():
    server = await asyncio.start_server(handle_connection, host, port)
    print("서버 대기중....")

    async with server:
        await closeEvent.wait()
        print("서버 종료")

if __name__ == "__main__":
    # 서버 설정
    utils.directory = utils.readConfig("docs_directory")
    host = sys.argv[1]
    port = int(sys.argv[2])

    connectedClients = 0
    connected = False
    closeEvent = asyncio.Event()

    # 폴더 관련 코드들
    os.makedirs("files", exist_ok=True)
    utils.FM = None
    utils.FM = fileManager()

    asyncio.run(main())