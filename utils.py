import socket
import json
from tkinter import * # write 인터페이스 구현

endMessage = "##**##"
separator = "#&#&#"   # 섹션 구분자로 사용
directory = "./files/"

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

def makedata(request, query):
     # 예외처리 할 것들
    
     if request == "create":
         fileName = query[1]
         sectionNum = int(query[2])
         sectionNames = query[3:]
     elif request == "read":
         mode = 0 if len(query) == 1 else 1
         fileName = [None, query[1]][mode]
         sectionNum = None
         sectionNames = [None, query[2]][mode]
     elif request == "write":
         fileName = query[1]
         sectionNum = None
         sectionNames = query[2]

     data = {
            "request" : request,
            "fileName" : fileName,
            "sectionNum" : sectionNum,
            "sectionNames" : sectionNames
     }

     return data