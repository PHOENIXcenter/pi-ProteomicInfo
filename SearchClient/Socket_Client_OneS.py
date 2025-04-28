from socket import *
import os
import sys
import time
import struct

#Work_Dir = sys.argv[1]

def TransferFile(Work_Dir,Port,IP):
    CHUNKSIZE = 100000000
    sock = socket()
    print('Socket:' + str(Port) + ' ' + str(IP))
    #sock.connect(('localhost',13579))
    try:
        sock.connect((IP,Port))
    except Exception as e:
        print(e)

    Start_Time = time.time()

    for path,dirs,files in os.walk(Work_Dir):
        for file in files:
            filename = os.path.join(path,file)
            relpath = os.path.relpath(filename,Work_Dir)
            filesize = os.path.getsize(filename)
    # 文件夹下的相对路径
            print(f'Sending {relpath}')
            print(filesize)
            #print(filename)
            
            with open(filename,'rb') as f:
                #sock.sendall(relpath.encode() + b'\t')
    #            time.sleep(0.01)
                #sock.sendall(str(filesize).encode() + b'\t')
    #            time.sleep(0.01)
                fileinfo_size = struct.calcsize('1024sd')
                fhead = struct.pack('1024sd', str(relpath).encode(),filesize)
                sock.sendall(fhead)
                
                while True:
                    data = f.read(CHUNKSIZE)
                    if not data: break
                    sock.sendall(data)
                    #time.sleep(0.01)
                
    print('Done ')
    #time.sleep(3)
    #sock.close()
    print('Sever Disconnected')

    End_Time = time.time()
    Gap = float(End_Time) - float(Start_Time)
    print("Usage: " + str(Gap))

#TransferFile('D:\Huanan\Spectronaut_Result\Pic',18888,'10.16.4.101')