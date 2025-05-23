# 각종 예외 처리는 서버에서 구현 할듯..?
import socket   # 데이터 통신을 위함
import json     # 데이터를 넘길 때 사용
from utils import *
ip, port = input("ip:port 입력 : \n").split(":")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = '127.0.0.1'
port = 12345
client_socket.connect((ip, port))   # tcp 연결

while True:
    query = input().split()
    request = query[0]

    if request == "bye": 
        client_socket.close()
        print("client 종료")
        break

    # create <d_title> <s_#> <s1_title> ... <sk_title>
    elif request == "create":
        # data를 딕셔너리로 만들고 json으로 바꾸고고 전달
        data = makedata(request, query)

        # 인코딩 후 전송 
        client_socket.sendall(data.encode())

    # read 또는 read <d_title> <s_title>
    elif request == "read":
        mode = 0 if len(query) == 1 else 1  # 0이면 파일 목록, 1이면 섹션
        data = makedata(request, query)
        client_socket.sendall(data.encode())

        while True: 
            recv_data = client_socket.recv(1024).decode()    # 데이터 받음
            if recv_data == endMessage:
                break
            print(recv_data)

        # 잘 받았다는 요청 전송? 해야하나?

    # write <d_title> <s_title> 이후 인터페이스 제공
    elif request == "write":
        data = makedata(request, query)
        client_socket.sendall(data.encode())

        # 권한을 받는 코드 필요
        authorized = False
        data = client_socket.recv(1024).decode()
        if data == "waiting":
            while client_socket.recv(1024).decode() != "okay":
                continue

        # 권한 okay면
        text = WriteContents()

        # 총 문장의 개수
        num = len(text)
        client_socket.sendall(num.encode())

        for sentence in text:
            client_socket.sendall(json.dumps(sentence).encode())
        client_socket.sendall(endMessage.encode())

        # 메시지를 못 받으면 timeout?

    else:
        print("잘못된 입력입니다.")