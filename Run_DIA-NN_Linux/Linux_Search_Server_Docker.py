# -*- coding:utf-8 -*-

import threading
from socket import *
import os
import sys
import struct
import re
import shutil
import time
from datetime import datetime
import subprocess

global Port,Exe_Script,Received_Dir,Result_Dir,ThermoRawFileParser,CHUNKSIZE,Supp_Param,Fasta,path,OutputDir,Sample_Num,ParamFile

# 参数读入-可变参数
ParamFile = sys.argv[1]
for Line in open(ParamFile):
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
        Fasta_Label = str(Fasta).split('/')[-1]

# 固定参数
Supp_Param = ' --fasta-search --min-fr-mz 200 --max-fr-mz 1800 --met-excision --cut K*,R* --missed-cleavages 2 --min-pep-len 7 --max-pep-len 30 --min-pr-mz 300 --max-pr-mz 1800 --min-pr-charge 1 --max-pr-charge 4 --unimod4 --var-mods 5 --var-mod UniMod:35,15.994915,M --var-mod UniMod:1,42.010565,*n --monitor-mod UniMod:1 --reanalyse --relaxed-prot-inf --smart-profiling --peak-center --no-ifs-removal --use-quant --no-norm'
Exe_Script = '/usr/diann/1.8.1/diann-1.8.1'
if not os.path.exists('/public/home/chuanxi/Docker/Fasta/' + Fasta_Label):
    print('Fasta Create')
    shutil.copy(Fasta,'/public/home/chuanxi/Docker/Fasta/' + Fasta_Label)
print('Fasta Exist')
Fasta = '/Fasta/' + Fasta_Label
python_Quant = r'/public/home/chuanxi/Docker/Linux_Quant_Search_Docker.py'


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
                if not os.path.exists(Received_Dir + r'/SBatch'):
                    os.mkdir(Received_Dir + r'/SBatch')
                if Param_Info.endswith('.raw'):
                    Label = str(Param_Info).split('/')[-1].replace('.raw','')
                    Raw_File = '/data/' + str(Label) + '/' + str(Label) + '.raw'
                    OutputDir = '/data/' + str(Label)
                    mzML_File = str(Label) + '.mzML'
                    Input_File = '/data/' + str(Label) + '/' + str(mzML_File)
                    MonoScript = 'mono /Software/ThermoRawFileParser1.4.2/ThermoRawFileParser.exe ' + ' -i ' + str(Raw_File) + ' -o ' + str(OutputDir) + ' -L 1- --noPeakPicking'
                if Param_Info.endswith('analysis.tdf_bin'):
                    Label = str(Param_Info).split('/')[-2].replace('.d','')
                    print(Label)
                    Input_File = '/data/' + str(Label) + '/' + str(Label) + '.d'
                    MonoScript = ''
                if Param_Info.endswith('.mzML'):
                    Label = str(Param_Info).split('/')[-1]
                    Input_File = '/data/' + str(Label)
                    MonoScript = ''
                
                Label = str(Label).split('.')[0]
                ResultFile = '/data/' + str(Label) + '/Report.tsv'
                LibFile = '/data/' + str(Label) + '/report-lib.tsv'
                SBatch_Single = open(Received_Dir + r'/SBatch/' + str(Label) + '.job','w')
                SBatch_Single.write('#!/bin/bash' + '\n')
                SBatch_Single.write('#SBATCH --job-name=Run_DIA-NN-' + str(Label) + '\n')
                SBatch_Single.write('#SBATCH -N 1' + '\n' + '#SBATCH -n 11' + '\n')
                SBatch_Single.write('#SBATCH -o ' + str(Received_Dir) + '/' + str(Label) + '/' + str(Label) + '.normal.log' + '\n' + '#SBATCH -e ' + str(Received_Dir) + '/' + str(Label) + '/' + str(Label) + '.error.log' + '\n')
                SBatch_Single.write('\n')
                #Script_Param = str(Exe_Script) + ' --f ' + str(Input_File) + ' --lib '+ '"' + '"' + ' --threads 20 --verbose 1 --out ' + str(ResultFile) + ' --out-lib ' + str(LibFile) + ' --gen-spec-lib --qvalue 0.01 --matrices --double-search --predictor --fasta ' + str(Fasta) + str(Supp_Param) 
                Script_Param = str(Exe_Script) + ' --f ' + str(Input_File) + ' --lib '+ '"' + '"' + ' --threads 20 --verbose 1 --out ' + str(ResultFile) + ' --out-lib ' + str(LibFile) + ' --gen-spec-lib --qvalue 0.01 --matrices --predictor --fasta ' + str(Fasta) + str(Supp_Param) 
                if MonoScript:
                    SBatch_Single.write('docker run -v ' + str(Received_Dir) + ':/data run-diann ' + str(MonoScript) + ' && echo "mzML Succeed"' + '\n')
                    SBatch_Single.write('\n')
                SBatch_Single.write('docker run -v ' + str(Received_Dir) + ':/data -v /public/home/chuanxi/Docker/Fasta:/Fasta run-diann ' + str(Script_Param) + ' && echo "DIA-NN Succeed"' + '\n')
                SBatch_Single.write('docker container prune -f ' + '\n')
                SBatch_Single.close()
                time.sleep(5)
                os.system('sbatch '  + Received_Dir + r'/SBatch/' + str(Label) + '.job')
                Count = 0
                for DirInfo in os.listdir(Received_Dir):
                    Path = os.path.join(Received_Dir,DirInfo)
                    if os.path.isdir(Path) and os.path.exists(os.path.join(Path,'Report.tsv')):
                        Count = Count + 1
                print(Count)
                if int(Count) >= int(Sample_Num) - 1:
                    JobName = 'Run_DIA-NN-' + str(Label)
                    JobID = subprocess.run('scontrol show job |grep ' + JobName  + "|cut -d ' ' -f 1", shell=True, capture_output=True, text=True)
                    ID = JobID.stdout.strip().split('=')[-1]
                    print(ID)
                    Output = open(os.path.join(Result_Dir,'Get_DIA-NN_Quant_Search.job'),'w')
                    Output.write('#!/bin/bash' + '\n')
                    Output.write('#SBATCH --job-name=Get_DIA-NN_Quant_Search-' + str(Result_Dir) + '\n')
                    Output.write('#SBATCH -N 1' + '\n' + '#SBATCH -n 2' + '\n' + '#SBATCH -o ' + str(Result_Dir) + '/Get_DIA-NN_Quant_Search_normal.log' + '\n' + '#SBATCH -e ' + str(Result_Dir) + '/Get_DIA-NN_Quant_Search_error.log' + '\n')
                    Output.write('\n')
                    Output.write('python3 ' + str(python_Quant) + str(ParamFile) + ' ' + str(Received_Dir))
                    Output.close()
                    if ID :
                        os.system('sbatch --dependency=afterok:' + str(ID) + ' ' + os.path.join(Result_Dir,'Get_DIA-NN_Quant_Search.job'))
                    else:
                        os.system('sbatch ' + os.path.join(Result_Dir,'Get_DIA-NN_Quant_Search.job'))
        except Exception as error:
            print(error)

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

