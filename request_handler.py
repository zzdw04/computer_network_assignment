import asyncio
import os

from file_manager import *
from utils import *

async def create(data, writer: asyncio.StreamWriter): 
    global FM

    name = data["fileName"]
    os.makedirs("./files/"+name, exist_ok=True)

    sectionNum = data["sectionNum"]
    sectionNames = data["sectionNames"]

    if len(sectionNames) != sectionNum:
        return # 이름의 개수와 설정한 섹션 개수의 불일치

    if FM.duplicated(name):
        return # 이름 중복
    
    FM.fileAdd(file(name, sectionNum, sectionNames))
    FM.getFile(name).startProcessing()
    for idx, secName in enumerate(sectionNames):
        with open(f"{directory}{name}/{secName}.txt", 'w', encoding="utf-8") as f:
            f.write("")
            
    writer.write(endMessage.encode())  # 끝을 알리는 메시지, 잘 처리했다는 의미
    await writer.drain()

async def read(data, writer: asyncio.StreamWriter):    # 딕셔너리에 있는 콘텐츠를 읽어옴
    # 실제로 읽어오면 애로사항이 많음
    # 너무 느림
    # 읽는 중에 파일 변경 요청이 오면 처리하기 까다로움
    # 메모리 관점에선 좋긴 한데, 다양한 문제가 생기고 구조가 복잡해질듯
    # 그냥 시간과 메모리를 trade off, 서버는 고성능이라 메모리가 충분하다고 생각합니다
    def Error(): return 0

    global FM

    name = data["fileName"]

    # case 1, read
    if name == None:
        files = FM.getFileInfo()    # 파일 객체들을 가져와서
        # 파일별로 이름과 섹션들을 받아서 보내준다. 어차피 write가 되어도 여긴 안바뀜 
        for f in files:
            fileName = f.getName()

            writer.write(fileName.encode())
            await writer.drain()

            for idx, SecName in enumerate(f.getSections()):
                writer.write(f"\t{idx + 1}. {SecName}".encode())
                await writer.drain()

        writer.write(endMessage.encode())  # 끝을 알리는 메시지
        await writer.drain()

    # case 2, read <fileName> <sectionName>
    elif FM.duplicated(name):   # 중복된 파일 제목이 있으면 실행
        sectionName = data["sectionNames"][0]
        fileclass = FM.getFile(name)

        if not fileclass.sectionCheck(sectionName): Error()

        # 제목 및 섹션 이름
        writer.write(name.encode())
        await writer.drain()
        sectionIdx = fileclass.getSections().index(sectionName) + 1

        writer.write(f"\t{sectionIdx}. {sectionName}".encode())
        await writer.drain()

        # 파일 내용 보내기
        lines = fileclass.getContents(sectionName) # 확정된 내용을 받아서 보냄

        for line in lines:
            writer.write("\t" + line.encode())
            await writer.drain()

        writer.write(endMessage.encode())  # 끝을 알리는 메시지
        await writer.drain()

    else: Error()

async def write(data, writer: asyncio.StreamWriter, reader: asyncio.StreamReader):
    global FM

    fileName = data["fileName"]
    sectionName = data["sectionNames"]
    fileclass = FM.getFile(fileName)

    if not (FM.duplicated(fileName) and\
             fileclass.sectionCheck(sectionName)): await Error()

    await fileclass.waitingQueue[sectionName].put((writer, reader))


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info('peername')
    print(f"{addr}에서 연결됨")

    # # Nagle 알고리즘이 TCP 전송 단위를 합치지 않게 하도록
    # sock = writer.get_extra_info('socket')
    # sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    while True:
        data = await reader.readline()
        message = data.decode().strip()
        request_data = json.loads(message)
        request = request_data["request"]

        match request:
            case "create":
                task = asyncio.create_task(create(data, writer))
            case "read":
                task = asyncio.create_task(read(data, writer))
            case "write":
                task = asyncio.create_task(write(data, writer, reader))
            case "bye":
                writer.close()    
                await writer.wait_closed()
                break 
            case default:
                Error()

async def Error():    # 에러 타입을 구분할까 ... 잘못된 요청이라고 퉁칠까까.
    pass    
    #await send_error(writer, "Unknown request")