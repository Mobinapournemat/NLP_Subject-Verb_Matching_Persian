import socket
import threading


host = '127.0.0.1'
port = 8550
username = input("Choose a username: ") 

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))


def receive():
    while True:
        try:
            messages = client.recv(1024).decode('ascii').split('\0')
            for message in messages:
                if message == 'Type':
                    client.send('Client'.encode('ascii'))
                elif message == 'Username':
                    client.send(str(username).encode('ascii'))
                elif message[:5] == 'board':
                    board = message[5:]
                    print(board)
                else:
                    print(message)
        except:
            print('An Error occurred!')
            client.close()
            exit()


def write():
    while True:
        try:
            message = input()
            client.send(message.encode('ascii'))
            if message == '/exit':
                client.close()
                exit()
        except:
            print('An Error occurred!')
            client.close()
            break


receive_thred = threading.Thread(target=receive)
receive_thred.start()

write_thred = threading.Thread(target=write)
write_thred.start()