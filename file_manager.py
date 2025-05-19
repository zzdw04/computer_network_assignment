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
    def getSectionNum(self):
        return self.__sectionNum
    def sectionCheck(self, name):   # 이 이름의 섹션이 존재하는지 확인인
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