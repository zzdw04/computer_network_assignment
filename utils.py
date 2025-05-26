import socket
import json
from tkinter import * # write 인터페이스 구현

endMessage = "END!" 
waitMessage = "Waiting..."
proceedMessage = "PROCEED"
committedMessage = "COMMITTED"
startEndSymbol = "------------------------------"
lineLimit = 10
byteLimit = 64
directory = None
FM = None

class valueError(Exception):
    def __str__(self): return "한 개 이상의 섹션을 입력하여야 합니다."

class ByteExceedError(Exception):
    def __str__(self): return "64바이트 초과"

def debug():
     print("여기까지 실행")

def WriteContents():
    texts = []
    def confirm():
            content = text_box.get("1.0", "end-1c")
            texts.append(content.split("\n"))
            window.destroy()
    
    window = Tk()
    window.title("write")
    window.geometry('640x480')  # VGA 해상도

    # 인터페이스, 레이아웃 구성
    frame = Frame(window, width=560, height=420)
    frame.place(x=40, y=30)

    # 여러 줄의 텍스트 입력 창 제공
    text_box = Text(frame, wrap='word')
    text_box.pack(fill='both', expand=True)

    button = Button(window, text="확인", command=confirm)
    button.place(x=610, y=30)

    window.mainloop()
    return texts[0]

def makedata(requestType, request, content = None):
    try:
        if requestType == "create":
            fileName = request[1]
            sectionNum = int(request[2])
            sectionNames = request[3:]
    
            if sectionNum == 0 or sectionNames == []:
                raise valueError()
            if not (checkByte(fileName) and checkByte(sectionNames)):
                raise ByteExceedError()


        elif requestType == "read":
            mode = 0 if len(request) == 1 else 1
            fileName = None if mode == 0 else request[1]
            sectionNames = None if mode == 0 else request[2]
            sectionNum = None

        elif requestType == "write" or requestType == "content":
            fileName = request[1]
            sectionNames = request[2]
            sectionNum = None

        elif requestType == "bye" or requestType == "alert":
            fileName, sectionNum, sectionNames = None, None, None

        data = {
            "requestType" : requestType,
            "fileName" : fileName,
            "sectionNum" : sectionNum,
            "sectionNames" : sectionNames,
            "content" : content
        }
        return (json.dumps(data) + "\n").encode()
        # 서버에서 readline으로 메시지를 받기 때문에 개행문자 필요.
    except Exception as e:
        print(f"잘못된 입력! : {e}")
        return None
    
def checkByte(string):
    if isinstance(string, str):
        return len(string) < byteLimit
    elif isinstance(string, list):
        return all( len(x) < byteLimit for x in string)
    
def readConfig(data, path = "./files/config.txt"):
    with open(path, 'r', encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"): continue
            line = line.strip()
            key, value = line.split('=')
            if key.strip() == data:
                return value.strip()