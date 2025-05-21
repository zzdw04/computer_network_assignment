from collections import deque
import asyncio

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
        self.waitingQueue = dict()
        self.locks = dict()
        self.__content = dict()
        self.__commited_content = dict()

        for name in self.__sectionNames:
            self.waitingQueue[name] = deque()
            self.locks[name] = asyncio.Lock()
            self.__content[name] = []
            self.__commited_content[name] = []

        self.__sectionStarts = [i*2 for i in range(sectionNum+1)] # 처음은 구분자 + Null, endline

    def getName(self): 
        return self.__name
    def getSections(self): 
        return self.__sectionNames
    def getSectionNum(self):
        return self.__sectionNum
    def sectionCheck(self, name):   # 이 이름의 섹션이 존재하는지 확인
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
    
    def fix_content(self, section, newContent):
        self.__content[section] = []
        for line in newContent:
            self.__content[section].append(line)
    def content_confirm(self, section):
        self.__commited_content[section] = []
        for line in self.__content:
            self.__commited_content[section].append(line)

    def start_processing(self):
        for section in self.getSections():
            asyncio.create_task(self.write_loop(section))

    async def write_loop(self, section):
        while True:
            if self.waitingQueue[section] and self.locks[section]:
                pass

    def apply_write(self, section_name, request):
        pass