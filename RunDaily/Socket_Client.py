from socket import *
import os
import sys
import time
import struct

def TransferFile(filename,IP,Port):
    CHUNKSIZE = 1000000
    sock = socket()
    #sock.connect(('localhost',13579))
    try:
        sock.connect((IP,int(Port)))
    except Exception as e:
        print(e)
    Start_Time = time.time()
    relpath = filename.split('\\')[-1]
    filesize = os.path.getsize(filename)
# 文件夹下的相对路径
    print(f'Sending {filename}')
    with open(filename,'rb') as f:
        fileinfo_size = struct.calcsize('1024sd')
        fhead = struct.pack('1024sd', str(relpath).encode(),filesize)
        sock.sendall(fhead)
        while True:
            data = f.read(CHUNKSIZE)
            if not data: break
            sock.sendall(data)
            #time.sleep(0.01)
                
    End_Time = time.time()
    Gap = float(End_Time) - float(Start_Time)
    #print("Usage: " + str(Gap))
    print('Transfer File Done ')

#TransferFile(r'I:\Huangcx\Monitor\2023-02-24_QC_Report\TOF4_20220909_DDA_293T_200ng_300nL_120min_column0909_QC_RB6_1_1817_MQ_Stat_Summary.txt','192.168.100.91',11111)