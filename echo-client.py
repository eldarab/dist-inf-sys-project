import socket

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        msg = input('Enter a message ')
        s.sendall(str.encode(msg))
        data = s.recv(1024)
        print('Received', repr(data))
        print(type(data), type(repr(data)), type(b'q'))
        if data == b'q':
            break
