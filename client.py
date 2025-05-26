import time
import socket   # 데이터 통신을 위함
import json     # 데이터를 넘길 때 사용
import sys
from utils import *

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

clientIp = sys.argv[1]
# clientPort = int(sys.argv[2])

while True:
    try:
        clientPort = int(input("포트 번호 입력 : "))
        client_socket.bind((clientIp, clientPort))
        break
    except:
        print("잘못된 포트 번호")

ip, port = readConfig("docs_server").split()
client_socket.connect((ip, int(port)))   # tcp 연결
while True:
    try:
        request = input().split()
        requestType = request[0]
        if requestType == "bye":

            sendData = makedata(requestType, request)
            if sendData != None:
                client_socket.sendall(sendData)
            else: raise Exception
            
            response = client_socket.recv(1024).decode()
            if response == "CloseACK":
                client_socket.close()
                print("client 종료")
                break

        # create <d_title> <s_#> <s1_title> ... <sk_title>
        elif requestType == "create":
            # data를 딕셔너리로 만들고 json으로 바꾸고 전달
            # 인코딩 후 전송 
            sendData = makedata(requestType, request)
            if sendData != None:
                client_socket.sendall(sendData)
            else: raise Exception

            message = client_socket.recv(1024).decode()

            if message == committedMessage:
                print("요청이 잘 처리 되었습니다.")
            else: print(message)

        # read 또는 read <d_title> <s_title>
        elif requestType == "read":
            sendData = makedata(requestType, request)
            if sendData != None:
                client_socket.sendall(sendData)
            else: raise Exception
            sock_file = client_socket.makefile("r", encoding="utf-8") # 줄 단위로 읽기 위해, 소켓을 파일처럼 읽을 수 있도록 하는 것

            while True: 
                recv_data = sock_file.readline().rstrip()   # 데이터 받음
                if recv_data.split()[0] == "에러!":
                    print(recv_data)
                    break
                if recv_data == endMessage:
                    break
                print(recv_data)

        # write <d_title> <s_title> 이후 인터페이스 제공
        elif requestType == "write":
            sendData = makedata(requestType, request)
            if sendData != None:
                client_socket.sendall(sendData)
            else: raise Exception

            # 권한을 받는 코드
            data = client_socket.recv(1024).decode().strip()
            if data == waitMessage:
                print("누군가가 해당 섹션에 작성중...")
                while client_socket.recv(1024).decode().strip() != proceedMessage:
                    time.sleep(0.01)
            elif data == proceedMessage:
                pass
            else:
                print("잘못된 요청입니다.")
                continue
                
            # 권한 okay면
            while True:
                texts = WriteContents()

                if len(texts) > lineLimit:  # 줄 제한. default = 10
                    print(f"입력 제한{lineLimit}줄을 초과하였습니다. 내용을 다시 입력 해주세요.")
                    continue
                
                if not checkByte(texts):    # byte 제한. default = 64
                    print(f"입력 제한{byteLimit}byte를 초과한 줄이 있습니다. 내용을 다시 입력 해주세요.")
                    continue
                
                break

            for sentence in texts:
                client_socket.sendall(makedata("content", request, sentence))
            client_socket.sendall(makedata("content", request, endMessage))



            print("모든 데이터를 보냈다!")
            message = client_socket.recv(1024).decode()
            if message == committedMessage:
                print("요청이 잘 처리 되었습니다.")
            else: print(message)

        else:
            print("잘못된 입력입니다.")

    except: continue