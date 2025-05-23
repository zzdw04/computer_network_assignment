import asyncio
from utils import *

class fileManager: # 파일 최대 10개, 제목 및 섹션의 제목 최대 64바이트 섹션 내용 최대 10줄, 각 줄은 최대 64바이트 
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
    def getFile(self, name):    # 최대 파일 10개라서 선형탐색 okay 
        for file in self.__files:
            if file.getName() == name: return file
    
class file:
    # 섹션 구분 : #&#&# section #&#&#
    # 사실 두 섹션 이름이 같아도 안됨
    def __init__(self, name,sectionNum, sectionNames):  # 초기화
        self.__name = name   
        self.__sectionNum = sectionNum
        self.__sectionNames = sectionNames
        self.waitingQueue = dict()
        self.locks = dict() 
        self.__content = dict()
        self.__commited_content = dict()    # read는 오직 여기서만 데이터를 받음
        # 섹션 인덱스가 필요할까...? 진짜모름
        for name in self.__sectionNames:
            self.waitingQueue[name] = asyncio.Queue()
            self.locks[name] = asyncio.Lock()
            self.__content[name] = []
            self.__commited_content[name] = []

        self.__sectionStarts = [i*2 for i in range(sectionNum+1)] # 처음은 구분자 + Null, endline

    def getName(self):  # 파일 이름 리턴
        return self.__name
    def getSections(self): # 섹션 이름들 리스트로 리턴
        return self.__sectionNames
    def getSectionNum(self):    # 총 섹션의 개수 리턴
        return self.__sectionNum
    def sectionCheck(self, name):   # 이 이름의 섹션이 존재하는지 확인
        if name in self.__sectionNames: 
            return True
        return False
    
    def __fixContent(self, section, newContent): # content 내용을 수정
        self.__content[section] = []
        for line in newContent:
            self.__content[section].append(line)

    def __confirmContent(self, section): # 내용을 확정하는 함수
        self.__commited_content[section] = []
        for line in self.__content[section]:
            self.__commited_content[section].append(line)

    def getContents(self, section):  # 확정된 내용을 보냄
        return self.__commited_content[section] + [] # 이러면 새로운 객체가 복사되어 리턴

    def startProcessing(self): # 파일 객체를 만들 때 같이 돌릴듯 한데... 생성자로 넣는게 맞으려나. 
        for section in self.getSections():
            asyncio.create_task(self.write_loop(section))

    async def writeLoop(self, section):    # 큐에 들어오면 작업을 실행할 곳
        while True:

            if self.waitingQueue[section]:
                nowTask = self.waitingQueue[section].popleft()

            async with self.locks[section]:
                if self.waitingQueue[section]:
                    new_contents = []
                    while True:
                        break
                        # endmessage가 올 때까지
                        # new_contents에 append 탭 한 번 해서!!
                    
                    self.__fixContent(section, new_contents)
                    self.__confirmContent(section)
                    
                    # 실제 파일에 작성
                    with open(f"{directory}{self.__name}/{section}.txt", 'w', encoding="utf-8") as f:
                        f.writelines(self.__commited_content)


                    # 락을 풀기

            # 잘 처리했다는 내용 전송