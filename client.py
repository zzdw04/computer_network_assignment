# 각종 예외 처리는 서버에서 구현 할듯..?
import socket   # 데이터 통신을 위함
import json     # 데이터를 넘길 때 사용
from utils import *
endMessage = "##**##"

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
        # data를 딕셔너리로 만들고 json으로 전달
        data = makedata(request, query)

        # 데이터를 json형식으로 바꾸고, 인코딩 후 전송 
        client_socket.sendall(json.dumps(data).encode())

    # read 또는 read <d_title> <s_title>
    elif request == "read":
        mode = 0 if len(query) == 1 else 1
        data = makedata(request, query)
        client_socket.sendall(json.dumps(data).encode())

        recv_data = client_socket.recv(1024)    # 데이터 받음
        json_str = recv_data.decode()           # 디코딩
        data = json.loads(json_str)             # 파싱

        # 이후 적절히 문장을 출력하는 코드 필요.

    # write <d_title> <s_title> 이후 인터페이스 제공
    elif request == "write":
        data = makedata(request, query)

        json_str = json.dumps(data)
        client_socket.sendall(json_str.encode())

        # 권한을 받는 코드 필요

        # 권한 ok!면
        text = WriteContents()

        # 총 문장의 개수
        num = len(text)
        client_socket.sendall(num.encode())

        for sentence in text:
            client_socket.sendall(json.dumps(sentence).encode())

    else:
        print("잘못된 입력입니다.")