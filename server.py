import socket
import json
import asyncio
import os
from collections import deque

class fileManager:
    def __init__(self):
        self.__fileNum = 0
        self.__fileNames = set()
        self.__files = list()

    def fileAdd(self, file):    
        self.__files.append(file)
        self.__fileNames.add(file.getName())
    def duplicated(self, name):
        if name in self.__fileNames: 
            return True
        return False
    def getFileInfo(self):
        return self.__files    
    def getFile(self, name):
        for file in self.__files:
            if file.getName() == name: return file
    
class file:
    # 섹션 구분 : #&#&# section #&#&#
    # 사실 두 섹션 이름이 같아도 안됨
    def __init__(self, name,sectionNum, sectionNames):
        self.__name = name   
        self.__sectionNum = sectionNum
        self.__sectionNames = sectionNames
        self.__waitingQueue = deque()
        self.__locked = False
        self.__sectionStarts = [i*2 for i in range(sectionNum+1)] # 처음은 구분자 + Null, endline

    def getName(self): 
        return self.__name
    def getSection(self): 
        return self.__sectionNames
    def sectionCheck(self, name):
        if name in self.__sectionNames: 
            return True
        return False
    def fixOffset(self, section, lines):
        pass
        # if section3을 수정했으면... 
        # sec[3] - sec[2] 이게 원래 섹션 길이 + 1 (구분자)
        # lines - 저 값 -> dline 만큼 그 뒤의 offset만큼 더하면 될듯
    def getLines(self, section):
        idx = self.__sectionNames.idx(section)  # (시작 줄, 다음 섹션 시작 줄)을 리턴
        return (self.__sectionStarts[idx] + 1, self.__sectionStarts[idx+1])

async def create(data): 
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
            
async def read(data, addr):
    def Error(): return 0

    global FM

    name = data["fileName"]

    # case 1, read

    # 줄 단위로 보내야 함. 수정 필요.
    if name == None:
        files = FM.getFileInfo()
        files_dict = dict() # 파일이름 : 섹션 이름들
        for f in files:
            files_dict[f.getName()] = f.getSection()

        server_socket.sendall(json.dumps(files_dict).encode())

    # case 2, read <fileName> <sectionName>
    elif FM.duplicated(name):
        sectionName = data["sectionNames"][0]
        fileclass = FM.getFile(data["fileName"])

        if not fileclass.sectionCheck(sectionName): Error()

        with open(directory+name+".txt", 'r', encoding="utf-8") as f:
            start, end = fileclass.getLines(sectionName)
            for idx, line in enumerate(f):
                if idx >= end : break
                elif start <= idx :
                    server_socket.sendall(json.dumps(line).encode())

    else: Error()

async def write(data, addr):
    pass
    # 구현 목록
    # lock, unlock
    # 
    # 됐다 안됐다 그거랑
    # 입력 받은거 수정, 마지막에 입력의 끝을 알리는 무언가 필요
    # offset 수정

async def handle_client(client_socket, addr):
    while True:
        data = json.loads(client_socket.recv().decode())       # 클라이언트로부터 데이터 받기
        request = data["request"]
        match request:
            case "create":
                task = asyncio.create_task(create(data))
            case "read":
                task = asyncio.create_task(read(data, addr))
            case "write":
                task = asyncio.create_task(write(data, addr))
            case "bye":
                break 
            case default:
                print("잘못된 요청입니다.")


# 서버 설정
host = '127.0.0.1'  # local
port = 12345

# 폴더 관련 코드들
directory = "./files/"
os.makedirs("files", exist_ok=True)
separator = "#&#&#"   # 섹션 구분자로 사용
FM = fileManager()

# 소켓 만들기 AF_INET : ipv4, SOCK_STREAM : TCP 통신
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen()
print("서버 대기중....")

while True:
    client_socket, addr = server_socket.accept()
    print(f"{addr}에서 연결됨")

    handle_client(client_socket, addr)
    client_socket.close()