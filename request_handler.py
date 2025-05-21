import asyncio
from collections import deque

from file_manager import *
from utils import *

async def create(data, client_socket): 
    global FM

    name = data["fileName"]
    sectionNum = data["sectionNum"]
    sectionNames = data["sectionNames"]

    if len(sectionNames) != sectionNum:
        return # 이름의 개수와 설정한 섹션 개수의 불일치

    if FM.duplicated(name):
        return # 이름 중복
    
    FM.fileAdd(file(name, sectionNum, sectionNames))

    with open(directory+name+".txt", 'w', encoding="utf-8") as f:
        for i in range(1, sectionNum+1):
            f.write(f"{separator} {i} {sectionNames[i]} {separator}\n\n")
            
    client_socket.sendall(endMessage.encode())  # 끝을 알리는 메시지, 잘 처리했다는 의미

async def read(data, client_socket):    # 실제로 파일을 읽을 필요는 없을듯? 수정합시다.
    def Error(): return 0

    global FM

    name = data["fileName"]

    # case 1, read
    if name == None:
        files = FM.getFileInfo()
        for f in files:
            fileName = f.getname()
            client_socket.sendall(fileName.encode())
            for idx, SecName in enumerate(f.getSections()):
                client_socket.sendall(f"\t{idx + 1}. {SecName}".encode())

        client_socket.sendall(endMessage.encode())  # 끝을 알리는 메시지

    # case 2, read <fileName> <sectionName>
    elif FM.duplicated(name):   # 중복된 파일 제목이 있으면
        sectionName = data["sectionNames"][0]
        fileclass = FM.getFile(name)

        if not fileclass.sectionCheck(sectionName): Error()

        # 제목 및 섹션 이름
        client_socket.sendall(name.encode())
        sectionIdx = fileclass.getSections().index(sectionName) + 1
        client_socket.sendall(f"\t{sectionIdx}. {sectionName}".encode())

        # 파일 내용 보내기
        with open(directory+name+".txt", 'r', encoding="utf-8") as f:
            start, end = fileclass.getLines(sectionName)
            for idx, line in enumerate(f):
                if idx >= end : break
                elif start <= idx :
                    client_socket.sendall(f"\t\t{line}".encode())
            client_socket.sendall(endMessage.encode())

    else: Error()

async def write(data, client_socket):
    global FM

    fileName = data["fileName"]
    sectionName = data["sectionNames"]
    fileclass = FM.getFile(fileName)

    if not (FM.duplicated(fileName) and\
             fileclass.sectionCheck(sectionName)): Error()

    fileclass.waitingQueue.append(client_socket)


async def handle_client(client_socket, addr):
    while True:
        data = json.loads(client_socket.recv().decode())       # 클라이언트로부터 데이터 받기
        request = data["request"]
        match request:
            case "create":
                task = asyncio.create_task(create(data, client_socket))
            case "read":
                task = asyncio.create_task(read(data, client_socket))
            case "write":
                task = asyncio.create_task(write(data, client_socket))
            case "bye":
                break 
            case default:
                print("잘못된 요청입니다.")

def Error():
    pass