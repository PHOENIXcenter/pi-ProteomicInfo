# -*- coding:utf-8 -*-

import threading
from socket import *
import os
import sys
import struct
import re
import shutil
from datetime import datetime

global Port,Exe_Script,Received_Dir,Result_Dir,ThermoRawFileParser,CHUNKSIZE,Supp_Param,Fasta,path,OutputDir,Sample_Num,ParamFile

def RunMerge():
    os.system('python3 /root/HCX/Script/Linux_Quant_Search.py ' + str(ParamFile) + ' ' + str(Received_Dir))
    MergeScript = os.path.join(Result_Dir,'DIA-NN_Quant_Search.sh')
    os.system('sh '  + str(MergeScript))

# 这是检查条件的函数
def check_condition():
    # 这里放置你的条件检查逻辑
    # 假设条件满足时返回True
    Count = 0
    for DirInfo in os.listdir(Received_Dir):
        Path = os.path.join(Received_Dir,DirInfo)
        if os.path.isdir(Path) and os.path.exists(os.path.join(Path,'Report.tsv')):
            Count = Count + 1
    if Count == Sample_Num:
        RunMerge()
        sys.exit()
    else:
        print("条件不满足，不执行任务A。")
    
    # 每隔20分钟（1200秒）再次检查条件
    threading.Timer(1200, check_condition).start()

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
            print('Downloading ' + str(filename) + '...' + '\t' + 'Expecting ' + str(length) + ': bytes...')
            path = os.path.join(Received_Dir,filename)
            path = str(path).replace('\\','/')
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            if path.endswith('.raw') or path.endswith('analysis.tdf_bin'):
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
        
        try:
            if Param_Info != '':
                LogRecord = open(Received_Dir + r'/AutoSearch_Log_Record.txt','a')
                LogRecord.write('-----------------------------------------------------------------------------------------' + '\n')
                LogRecord.write(str(Param_Info) + '\n')
                LogRecord.write(str(datetime.now()) + ': Start Auto Search' + '\n')
                LogRecord.write('-----------------------------------------------------------------------------------------' + '\n')
                LogRecord.close()
                if Param_Info.endswith('.raw'):
                    OutputDir = '/'.join(str(Param_Info).split('/')[0:-1])
                    mzML_File = str(Param_Info).replace('.raw','.mzML')
                    Input_File = os.path.join(OutputDir,mzML_File)
                    os.system(r'mono '+ str(ThermoRawFileParser) + ' -i ' + str(Param_Info) + ' -o ' + str(OutputDir) + ' -L 1- --noPeakPicking')
                if Param_Info.endswith('analysis.tdf_bin'):
                    OutputDir = '/'.join(str(Param_Info).split('/')[0:-2])
                    Input_File = '/'.join(str(Param_Info).split('/')[0:-1])
                ResultFile = os.path.join(OutputDir,'Report.tsv')
                LibFile = os.path.join(OutputDir,'report-lib.tsv')
                os.system(str(Exe_Script) + ' --f ' + str(Input_File) + ' --lib '+ '"' + '"' + ' --threads 30 --verbose 1 --out ' + str(ResultFile) + ' --out-lib ' + str(LibFile) + ' --gen-spec-lib --qvalue 0.01 --matrices --predictor --fasta ' + str(Fasta) + str(Supp_Param))
                Count = 0
                for DirInfo in os.listdir(Received_Dir):
                    Path = os.path.join(Received_Dir,DirInfo)
                    if os.path.isdir(Path) and os.path.exists(os.path.join(Path,'Report.tsv')):
                        Count = Count + 1
                if Count == Sample_Num - 5:
                    check_condition(Sample_Num)
        
        except Exception as error:
            print(error)


ParamFile = sys.argv[1]
for Line in open(ParamFile):
    if Line.startswith('Exe_Path'):
        Exe_Script = Line.split(':')[1].strip()
    if Line.startswith('Port'):
        Port = Line.split(':')[1].strip()
    if Line.startswith('Received_Dir'):
        Received_Dir = Line.split(':')[1].strip()
    if Line.startswith('Result_Dir'):
        Result_Dir = Line.split(':')[1].strip()
    if Line.startswith('Sample_Num'):
        Sample_Num = Line.split(':')[1].strip()
    if Line.startswith('Fasta'):
        Fasta = Line.split(':')[1].strip()
    if Line.startswith('ThermoRawFileParser_Path'):
        ThermoRawFileParser = Line.split(':')[1].strip()

Supp_Param = ' --fasta-search --min-fr-mz 200 --max-fr-mz 1800 --met-excision --cut K*,R* --missed-cleavages 2 --min-pep-len 7 --max-pep-len 30 --min-pr-mz 300 --max-pr-mz 1800 --min-pr-charge 1 --max-pr-charge 4 --unimod4 --var-mods 5 --var-mod UniMod:35,15.994915,M --var-mod UniMod:1,42.010565,*n --monitor-mod UniMod:1 --relaxed-prot-inf --smart-profiling --peak-center --no-ifs-removal'
Port = int(Port)
CHUNKSIZE = 10000000
sock = socket()
sock.bind(('',Port))
sock.listen(5)
print(str(Port) + '\t' + str(Exe_Script) + '\t' + str(Received_Dir))
print('Waiting for a client...')

#if __name__ == '__main__':
while True:
    client, client_ip = sock.accept()
    client.settimeout(60)  # Waiting Time
    print("New client joined from " + str(client_ip))
    # Multi Thread -- talk
    thd = threading.Thread(target=talk, args=(client, client_ip))
    thd.setDaemon(True)  # 设置守护主线程 应对多个客户端同时传输
    thd.start()
            


