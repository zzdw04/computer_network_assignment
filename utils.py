import socket
import json
from tkinter import * # write 인터페이스 구현

endMessage = "END!"
directory = "./files/"  
waitMessage = "Waiting..."
proceedMessage = "PROCEED"
committedMessage = "COMMITTED"
startEndSymbol = "------------------------------"
FM = None

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

def makedata(request, query, content = None):
    while True:
        try:
            if request == "create":
                fileName = query[1]
                sectionNum = int(query[2])
                sectionNames = query[3:]

            elif request == "read":
                mode = 0 if len(query) == 1 else 1
                fileName = None if mode == 0 else query[1]
                sectionNames = None if mode == 0 else query[2]
                sectionNum = None
            elif request == "write" or request == "content":
                fileName = query[1]
                sectionNames = query[2]
                sectionNum = None
            elif request == "bye" or request == "alert":
                fileName, sectionNum, sectionNames = None, None, None
            data = {
                "request" : request,
                "fileName" : fileName,
                "sectionNum" : sectionNum,
                "sectionNames" : sectionNames,
                "content" : content
            }

            return (json.dumps(data) + "\n").encode()
            # 서버에서 readline으로 메시지를 받기 때문에 개행문자 필요.
        except:
            print("잘못된 입력!")
            query = input().split()
            request = query[0]

def checkByte(string):
     maxbyte = 64
     return len(string('utf-8')) > 64