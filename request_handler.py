import sys
sys.dont_write_bytecode = True

import asyncio
import os

from file_manager import *
import utils
from utils import debug

async def create(data, writer: asyncio.StreamWriter): 
    name = data["fileName"]
    sectionNum = data["sectionNum"]
    sectionNames = data["sectionNames"]

    if len(sectionNames) != sectionNum:
        return await Error(writer, "섹션 개수와 이름 수가 맞지 않음!") # 이름의 개수와 설정한 섹션 개수의 불일치

    if utils.FM.duplicated(name):
        print("이름 중복!")
        return await Error(writer, "이름 중복!") # 이름 중복

    os.makedirs("./files/"+name, exist_ok=True)
    utils.FM.fileAdd(file(name, sectionNum, sectionNames))
    utils.FM.getFile(name).startProcessing()

    for idx, secName in enumerate(sectionNames):
        with open(f"{directory}{name}/{secName}.txt", 'w', encoding="utf-8") as f:
            f.write("")
    
    print(f"{writer.get_extra_info('peername')}의 create 명령 완료.")
    writer.write(utils.committedMessage.encode())  # 잘 처리했다는 의미
    await writer.drain()

async def read(data, writer: asyncio.StreamWriter):    # 딕셔너리에 있는 콘텐츠를 읽어옴
    # 실제로 읽어오면 애로사항이 많음
    # 너무 느림
    # 읽는 중에 파일 변경 요청이 오면 처리하기 까다로움
    # 메모리 관점에선 좋긴 한데, 다양한 문제가 생기고 구조가 복잡해질듯
    # 그냥 시간과 메모리를 trade off, 서버는 고성능이라 메모리가 충분하다고 생각합니다
    print("read 들어왔다!")

    name = data["fileName"]

    # case 1, read
    if name == None:
        files = utils.FM.getFileInfo()    # 파일 객체들을 가져와서
        # 파일별로 이름과 섹션들을 받아서 보내준다. 어차피 write가 되어도 여긴 안바뀜
        writer.write(f"{utils.startEndSymbol}\n".encode())
        await writer.drain()

        for f in files:
            fileName = f.getName()

            writer.write(f"{fileName}\n".encode())
            await writer.drain()

            for idx, SecName in enumerate(f.getSections()):
                writer.write(f"\t{idx + 1}. {SecName}\n".encode())
                await writer.drain()

        writer.write(f"{utils.startEndSymbol}\n".encode())
        await writer.drain()

        writer.write(f"{utils.endMessage}\n".encode())  # 끝을 알리는 메시지
        await writer.drain()

    # case 2, read <fileName> <sectionName>
    elif utils.FM.duplicated(name):   # 중복된 파일 제목이 있으면 실행
        sectionName = data["sectionNames"]
        fileclass = utils.FM.getFile(name)

        if not fileclass.sectionCheck(sectionName): await Error(writer, "존재하지 않는 섹션 이름")

        # 제목 및 섹션 이름
        writer.write(f"{utils.startEndSymbol}\n".encode())
        await writer.drain()

        writer.write(f"{name}\n".encode())
        await writer.drain()
        sectionIdx = fileclass.getSections().index(sectionName) + 1

        writer.write(f"\t{sectionIdx}. {sectionName}\n".encode())
        await writer.drain()

        # 파일 내용 보내기
        lines = fileclass.getContents(sectionName) # 확정된 내용을 받아서 보냄

        for line in lines:
            writer.write(f"\t\t{line}".encode())
            await writer.drain()

        writer.write(f"{utils.startEndSymbol}\n".encode())
        await writer.drain()

        writer.write(f"{utils.endMessage}\n".encode())  # 끝을 알리는 메시지
        await writer.drain()

    else: await Error(writer, "잘못된 요청")

async def write(data, writer: asyncio.StreamWriter, reader: asyncio.StreamReader):
    print("write 들어왔다!")
    fileName = data["fileName"]
    sectionName = data["sectionNames"]
    fileclass = utils.FM.getFile(fileName)

    if not (utils.FM.duplicated(fileName) and\
             fileclass.sectionCheck(sectionName)): await Error(writer, "잘못된 요청")
    
    if fileclass.locks[sectionName].locked():   # 잠겨있을 경우 (누가 사용중인 경우)
        writer.write(waitMessage.encode())
        await writer.drain()
    await fileclass.waitingClientQueue[sectionName].put((writer, reader))

async def pushContent(data):
    fileName = data["fileName"]
    sectionName = data["sectionNames"]
    fileclass = utils.FM.getFile(fileName)
    print(data["content"])
    await fileclass.writeMessageQueue[sectionName].put(data["content"])
    print("잘 들어갔음!")

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    # # Nagle 알고리즘이 TCP 전송 단위를 합치지 않게 하도록
    # sock = writer.get_extra_info('socket')
    # sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    while True:
        request_data = json.loads((await reader.readline()).decode().strip())
        request = request_data["request"]
        print("데이터 수신!")
        print(request_data)
        match request:
            case "create":
                task = asyncio.create_task(create(request_data, writer))
            case "read":
                task = asyncio.create_task(read(request_data, writer))
            case "write":
                task = asyncio.create_task(write(request_data, writer, reader))
            case "content":
                task = asyncio.create_task(pushContent(request_data))
            case "alert":
                pass
            case "bye":
                addr = writer.get_extra_info('peername')
                writer.write("CloseACK".encode())
                await writer.drain()
                writer.close()
                print(f"{addr}에서 연결 종료 됨")
                await writer.wait_closed()
                break 
            case default:
                await Error(writer, "잘못된 요청")

async def Error(writer: asyncio.StreamWriter, message):
    print(f"에러! : {message}")
    writer.write(f"에러! : {message}".encode())
    await writer.drain()
