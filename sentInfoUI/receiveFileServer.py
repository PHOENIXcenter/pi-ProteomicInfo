# # -*- coding:utf-8 -*-
'''
用于多线程接收文件的。通过监听端口，将接收到的文件写入到指定的文件夹。

'''
import os
import struct
import socket
import threading

class ReceiveFile:
    def __init__(self, received_Dir, port):
        self.Received_Dir = received_Dir
        self.Port = port
        self.newFiles = []
        self.running = True
        self.CHUNKSIZE = 100000000
        self.server_sock = None

    def message_handle(self, tcp_client, tcp_client_ip):
        try:
            with tcp_client:
                while True:
                    fileinfo_size = struct.calcsize('1024sd')
                    buf = tcp_client.recv(fileinfo_size)
                    if not buf:
                        break
                    filename, length = struct.unpack('1024sd', buf)
                    filename = filename.strip(b'\00').decode()
                    if type(length) == int:
                        length = int(length)
                    # print(f'Downloading {filename}...\n  Expecting {length:} bytes...', end='\n', flush=True)
                    path = os.path.join(self.Received_Dir, filename)
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    with open(path, 'wb') as f:
                        while length > 0:
                            chunk = min(length, self.CHUNKSIZE)
                            data = tcp_client.recv(int(chunk))
                            if not data:
                                break
                            f.write(data)
                            length -= len(data)
                        else:
                            # print('Complete')
                            self.newFiles.append(path)
                            continue
                    # print('Incomplete')
                    break
        except Exception as e:
            print(str(tcp_client_ip) + str(e))

    def run(self):
        self.server_sock = socket.socket()
        self.server_sock.bind(('', self.Port))
        self.server_sock.listen(10)

        print(f'Waiting for a client on port {self.Port}...')
        while self.running:
            try:
                client, client_ip = self.server_sock.accept()
                client.settimeout(10)
                print(f"New client joined from {client_ip}")
                thd = threading.Thread(target=self.message_handle, args=(client, client_ip))
                thd.setDaemon(True)
                thd.start()
                print('Running -- Receiving files --')
            except socket.timeout:
                pass
            except OSError as e:
                if self.running:
                    print(f"Error accepting client: {e}")

    def stop(self):
        self.running = False
        if self.server_sock:
            self.server_sock.close()
            


# if __name__ == '__main__':
#     received_dir = r'D:\test\wechatMessage3\data\temp'  # Change to your desired directory
#     port = 12345  # Change to your desired port
#     receiver = ReceiveFile(received_dir, port)
#     receiver.run()
