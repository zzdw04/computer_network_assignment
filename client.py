import time
import socket   # 데이터 통신을 위함
import json     # 데이터를 넘길 때 사용
from utils import *
# ip, port = input("ip:port 입력 : \n").split(":")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = '127.0.0.1'
port = 12345
client_socket.connect((ip, port))   # tcp 연결

while True:
    query = input().split()
    request = query[0]

    if request == "bye": 
        client_socket.sendall(makedata(request, query))
        
        response = client_socket.recv(1024).decode()
        if response == "CloseACK":
            client_socket.close()
            print("client 종료")
            break

    # create <d_title> <s_#> <s1_title> ... <sk_title>
    elif request == "create":
        # data를 딕셔너리로 만들고 json으로 바꾸고 전달
        # 인코딩 후 전송 
        client_socket.sendall(makedata(request, query))

        message = client_socket.recv(1024).decode()
        if message == committedMessage:
            print("요청이 잘 처리 되었습니다.")
        else: print(message)

    # read 또는 read <d_title> <s_title>
    elif request == "read":
        mode = 0 if len(query) == 1 else 1  # 0이면 파일 목록, 1이면 섹션
        client_socket.sendall(makedata(request, query))

        while True: 
            recv_data = client_socket.recv(1024).decode()    # 데이터 받음
            if recv_data == endMessage:
                break
            print(recv_data)

        # 잘 받았다는 요청 전송? 해야하나?

    # write <d_title> <s_title> 이후 인터페이스 제공
    elif request == "write":
        client_socket.sendall(makedata(request, query))

        # 권한을 받는 코드

        data = client_socket.recv(1024).decode().strip()
        if data == waitMessage:
            while client_socket.recv(1024).decode().strip() != proceedMessage:
                time.sleep(0.01)

        # 권한 okay면
        text = WriteContents()

        for sentence in text:
            client_socket.sendall(makedata("content", query, sentence))
        client_socket.sendall(makedata("content", query, endMessage))

        print("모든 데이터를 보냈다!")
        message = client_socket.recv(1024).decode()
        if message == committedMessage:
            print("요청이 잘 처리 되었습니다.")
        else: print(message)

    else:
        print("잘못된 입력입니다.")