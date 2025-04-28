# -*- coding:utf-8 -*-

import threading
from socket import *
import os
import sys
import struct
import re
import shutil
from datetime import datetime

def talk(tcp_client, tcp_client_ip):
    Param_Info = ''
    with tcp_client:
        while True:
            #client.setblocking(False)
            fileinfo_size = struct.calcsize('1024sd')
            buf = tcp_client.recv(fileinfo_size)
            if not buf:
                break
            filename,length = struct.unpack('1024sd', buf)
            filename = filename.strip(b'\00').decode()
            if type(length) == int:
                length = int(length)
            print(f'Downloading {filename}...\n Expecting {length:} bytes...',end='\n',flush=True)
            path = os.path.join(Received_Dir,filename)
            os.makedirs(os.path.dirname(path),exist_ok=True)
            if regex.match(filename):
                Param_Info = path
            # Read the data in chunks so it can handle large files.
            try :
                with open(path,'wb') as f:
                    while length > 0:
                        chunk = min(length,CHUNKSIZE)
                        data = tcp_client.recv(int(chunk))
                        if not data: break
                        f.write(data)
                        length -= len(data)
                    else: # only runs if while doesn't break and length==0
                        print(str(filename) + '... Data reception completed')
                        continue
            # socket was closed early.
            except:
                print('Incomplete')
                break
    #print(str(Exe_Script) + ' -command ')
    if Param_Info != '':
        FilePath = os.getcwd()
        LogRecord = open(FilePath + r'\Log\AutoSearch_Log_Record.txt','a')
        LogRecord.write('-----------------------------------------------------------------------------------------' + '\n')
        LogRecord.write(str(Param_Info).split('.')[0] + '\n')
        LogRecord.write(str(datetime.now()) + ': Start Auto Search' + '\n')
        LogRecord.write('-----------------------------------------------------------------------------------------' + '\n')
        LogRecord.close()
        if Software == 'MQ':
            NewMqpar = '\\'.join(Param_Info.split('\\')[0:-1])
            NewMqpar = NewMqpar + r'\mqpar.xml'
            shutil.copy(Param_Info,NewMqpar)
            #print('Run')
            os.system(r'mono '+ str(Exe_Script) + ' ' + NewMqpar )
        if Software == 'SP':
            #print('Run')
            os.system(str(Exe_Script) + ' -command ' + Param_Info)
        if Software == 'PD':
            Dir = '\\'.join(Param_Info.split('\\')[0:-1])
            File = Param_Info.split('\\')[-2]
            File = File + '.raw'
            File = os.path.join(Dir,File)
            Raw = Dir + 'r'
            os.system(str(Exe_Script) + ' -p ' + str(Param_Info) + ' ' + str(File))
    #print(str(Param_Info))

def RunService(Param_1,Param_2,Param_3,Param_4):
    global Port,Exe_Script,Received_Dir,Software,regex,CHUNKSIZE
    Port = int(Param_1)
    Exe_Script = Param_3
    Received_Dir = Param_2
    Software = Param_4
    CHUNKSIZE = 10000000
    sock = socket()
    sock.bind(('',Port))
    sock.listen(5)
    print(str(Port) + '\t' + str(Exe_Script) + '\t' + str(Received_Dir) + '\t' + str(Software))
    print('Waiting for a client...')
    if Software == 'MQ':
        regex = re.compile('.*_mqpar.xml$')
    if Software == 'SP':
        regex = re.compile('.*_argument.txt$')
    if Software == 'PD':
        regex = re.compile('.*.param$')
    #if __name__ == '__main__':
    while True:
        client, client_ip = sock.accept()
        client.settimeout(60)  # Waiting Time
        print(f"New client joined from {client_ip}")
        # Multi Thread -- talk
        thd = threading.Thread(target=talk, args=(client, client_ip))
        thd.setDaemon(True)  # 设置守护主线程 应对多个客户端同时传输
        thd.start()
            
##RunService(13579,r'D:\Huanan\Spectronaut_Result\Pic',r'D:\Software\MaxQuant_2.0.3.0\MaxQuant\bin\MaxQuantCmd.exe','MQ')

