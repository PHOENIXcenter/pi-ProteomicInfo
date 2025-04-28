import os
import sys
import re
import time
import shutil
from datetime import datetime,timedelta
import Socket_Client_OneS

regex = re.compile('.*\.raw$')
regex_Dir = re.compile('.*\.d$')

Dic_Initial = {}
Dic_New_Dir = {}
Dic_New_File = {}
LogDir = r'D:\AutoRun\Log'

def get_last_modified_time(file_path):
    # 获取文件的最后修改时间的时间戳
    mtime = os.path.getmtime(file_path)
# 将时间戳转换为 datetime 对象
    last_modified_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S") 
    return last_modified_date

# WorkDir-监测路径 DataStorge-传送路径 Port-端口 IP-传输电脑IP 
# Version-Maxquant记录的部分更换信息文件（待更换的raw file 路径及 Experiment 名） Label-时间标签
# Raw_File = r'D:\QC_Report_HCX\Test_Data\Example_Huang_TestRun.d'
# Raw_ExpName = 'Example_Huang_TestRun'

# Monitor_Size -->文件大小限制  Time_Wait_Size --> 文件大小不变后的等待时间  Time_Gap --> 监测新文件的间隔时间
# Wash_Gap --> 柱子清洗时间  
TimeFile = os.path.join(os.getcwd(),'Config','Monitor_Time.txt')
Monitor_Size = 300000000
Time_Wait_Size = 600
Time_Gap = 600
Wash_Gap = 1800
if os.path.exists(TimeFile):
    for Info in open(TimeFile,encoding = 'utf-8'):
        if Info.startswith('#'):
            continue
        else:
            Info = Info.strip().split(':')
            if Info[0] == 'Monitor_Size':
                Monitor_Size = int(Info[1])
            if Info[0] == 'Time_Wait_Size':
                Time_Wait_Size = int(Info[1])
            if Info[0] == 'Time_Gap':
                Time_Gap = int(Info[1])
            if Info[0] == 'Wash_Gap':
                Wash_Gap = int(Info[1])
#print(str(Monitor_Size))

def GetSize(Dir,Type):
    if Type == 'Bruker':
        Af_Size = 0
        for path,dirs,files in os.walk(Dir):
            for file in files:
                filename = os.path.join(path,file)
                filesize = os.path.getsize(filename)
                Af_Size += filesize
    elif Type == 'Thermo':
        Af_Size = os.path.getsize(Dir)
    return(Af_Size)

def Initial_Run(Parse1,Parse2,Parse3,Parse4,Parse5):
    global WorkDir,DataStorge,Example_Argument,Port,IP,Version,Label,Received_Dir,Raw_File,Raw_ExpName
    WorkDir = Parse1
    DataStorge = Parse2
    Version = Parse4
    Label = Parse5
    Port = Parse3.split(':')[0]
    if Port :
        Port = int(Port)
        #print('YYY')
    IP = Parse3.split(':')[1]
    if Version == 'SP':
        #print(Version)
        Example_Argument = DataStorge + r'\\' + Label + '_Example_argument.txt'
        for Info in open(Example_Argument):
            if Info.startswith('#SetReceiced_Dir'):
                Received_Dir = Info.strip().split('^$')[1]
    if Version == 'MQ':
        Example_Argument = DataStorge + r'\\' + Label + '_Example_mqpar.xml'
        for Info in open(Example_Argument,encoding = 'utf-8'):
            if Info.startswith('#The_Directory_of_Receive_data'):
                Received_Dir = Info.strip().split('^$')[1]
            if Info.startswith('#The_Directory_of_RawFile'):
                Raw_File = Info.strip().split('^$')[1]
                Raw_File = '   <filePaths>\n      <string>' + str(Raw_File) + '</string>\n   </filePaths>\n'
            if Info.startswith('#The_Name_of_Experiment'):
                Raw_ExpName = Info.strip().split('^$')[1]
                Raw_ExpName = '   <experiments>\n      <string>' + str(Raw_ExpName) + '</string>\n   </experiments>\n'
    if Version == 'PD':
        Example_Argument = DataStorge + r'\\' + Label + '_Example.param'
        for Info in open(Example_Argument,encoding = 'utf-8'):
            if Info.startswith('#The_Directory_of_Receive_data'):
                Received_Dir = Info.strip().split('^$')[1]
    # 不同的参数文件对应信息在不同的行 移除自主添加文件才为实际执行参数
    if Port:
        with open(Example_Argument,encoding = 'utf-8') as f:
            lines = f.readlines()
            if Version == 'SP':
                lines = lines[:-1]
            elif Version == 'MQ':
                lines = lines[:-3]
            elif Version == 'PD':
                lines = lines[:-1]
        FileInfo = open(Example_Argument,'w',encoding = 'utf-8')
        FileInfo.writelines(lines)
        FileInfo.close()
    
    if not os.path.exists(WorkDir + r'\\Acquisition_Record.txt'):
        for path,dirs,files in os.walk(WorkDir):
            for file in files:
                filename = os.path.join(path,file)
                if regex.match(file):
                    Dic_Initial[filename] = 1
            for Dir in dirs:
                fileDir = os.path.join(path,Dir)
                if regex_Dir.match(Dir):
                    Dic_Initial[fileDir] = 1
        Output = open(WorkDir + r'\\Acquisition_Record.txt','w')
        for Key in Dic_Initial.keys():
            Output.write(str(Key) + '\n')
        Output.close()
    print(str(datetime.now()) + ' Initial Record Done')
    #print(str(Received_Dir))
    time.sleep(300)
    JudgeNewFile(WorkDir)

# 判断是否产生新文件,并记录新文件
def JudgeNewFile(Monitor_Dir):
    global Dic_New_Dir,WorkDir
    global Dic_New_File
    global Dic_Initial
    global LogLabel
    print('Monitoring ...')
    LogLabel = str(datetime.now()).split(' ')[0].replace('-','')
    LogFile = open(LogDir + r'\\' + LogLabel + '_Client.log','a')
    LogFile.write(str(datetime.now()) + ' Monitoring ...' + '\n' )
    LogFile.close()
    Dic_Initial = {}
    for Info in open(WorkDir + '\\Acquisition_Record.txt'):
        Info = Info[:-1]
        Dic_Initial[Info] = 1
    for path,dirs,files in os.walk(Monitor_Dir):
        for file in files:
            filename = os.path.join(path,file)
            if regex.match(file) and filename not in Dic_Initial.keys():
                Dic_New_File[filename] = 1
        if Port != 'None':
            for Dir in dirs:
                fileDir = os.path.join(path,Dir)
                if regex_Dir.match(Dir) and fileDir not in Dic_Initial.keys():
                    Dic_New_Dir[fileDir] = 1
    Judge = 'FALSE'
    if len(Dic_New_File) > 0:
        Judge = 'TRUE'
        for filename in list(Dic_New_File.keys()):
            LogFile = open(LogDir + r'\\' + LogLabel + '_Client.log','a')
            LogFile.write(str(datetime.now()) + ' Dealing ' + str(filename) + '\n')
            LogFile.close()
            print(str(datetime.now()) + ' Deal ' + filename)
            Size = os.path.getsize(filename)
            #if Size > 20000000:
            time.sleep(Time_Wait_Size)
            Dic_Initial[filename] = 1
            JudgeComplete(filename,Size,'Thermo')
            
    if len(Dic_New_Dir) > 0 :
        Judge = 'TRUE'
        for filedir in list(Dic_New_Dir.keys()):
            LogFile = open(LogDir + r'\\' + LogLabel + '_Client.log','a')
            LogFile.write(str(datetime.now()) + ' Dealing ' + str(filedir) + '\n')
            LogFile.close()
            print(str(datetime.now()) + ' Deal ' + str(filedir))
            Size = GetSize(filedir,'Bruker')
            #if Size > 20000000:
            time.sleep(Time_Wait_Size)
            Dic_Initial[filedir] = 1
            JudgeComplete(filedir,Size,'Bruker')
    if Judge == 'TRUE':
        Output = open(WorkDir + '\\Acquisition_Record.txt','w')
        for Key in Dic_Initial.keys():
            Output.write(str(Key) + '\n')
        Output.close()
        JudgeNewFile(WorkDir)
    else:
        time.sleep(Time_Gap)
        JudgeNewFile(WorkDir)

def JudgeComplete(Dir,Be_Size,Type):
    global LogLabel
    Af_Size = GetSize(Dir,Type)
    if Af_Size != int(Be_Size):
        time.sleep(Time_Wait_Size)
        JudgeComplete(Dir,Af_Size,Type)
    else :
        time.sleep(Wash_Gap)
        NewSize = GetSize(Dir,Type)
        if NewSize == Af_Size:
            JudgeComplete_End(Dir,Af_Size,Type)
        else:
            print(str(datetime.now()) + Dir + ' NoCompleted.... ' + str(NewSize))
            LogFile = open(LogDir + r'\\' + LogLabel + '_Client.log','a')
            LogFile.write(str(datetime.now()) + Dir + ' NoCompleted.... ' + str(NewSize) + '\n')
            LogFile.close()
            JudgeComplete(Dir,NewSize,Type)

def JudgeComplete_End(Dir,Be_End_Size,Type):
    #print('End')
    global LogLabel,Dic_New_Dir
    Af_Size_End = 0
    if Type == 'Bruker':
        Value = Dic_New_Dir[Dir]
        Value = Value + 1
        Dic_New_Dir[Dir] = Value
    else:
        Value = Dic_New_File[Dir]
        Value = Value + 1
        Dic_New_File[Dir] = Value
    Af_Size_End = GetSize(Dir,Type)
    if Af_Size_End == int(Be_End_Size) and int(Af_Size_End) > Monitor_Size:
        #print('Do1')
        if Type == 'Bruker':
            CopyTranferDir(Dir)
            #print('Dir')
            del Dic_New_Dir[Dir]
        elif Type == 'Thermo':
            CopyTranferFile(Dir)
            #print('File')
            del Dic_New_File[Dir]
        LogFile = open(LogDir + r'\\' + LogLabel + '_Client.log','a')
        LogFile.write(str(datetime.now()) + ' ' + Dir + ' Completed ' + '\n')
        LogFile.close()
    # 文件夹大小一直小于设定大小 重复判断3次间隔时间确认 判定文件不正常取消采集，忽略该文件 应对初始取消的部分情况
    elif Af_Size_End == int(Be_End_Size) and Value == 4:
        #print('Do2')
        if Type == 'Bruker':
            del Dic_New_Dir[Dir]
        else:
            del Dic_New_File[Dir]
        LogFile = open(LogDir + r'\\' + LogLabel + '_Client.log','a')
        LogFile.write(str(datetime.now()) + Dir + ' Canceled.... ' + str(Af_Size_End) + '\n')
        LogFile.close()
    else:
        #print('Do3')
        print(str(datetime.now()) + Dir + ' NoCompleted.... ' + str(Af_Size_End))
        LogFile = open(LogDir + r'\\' + LogLabel + '_Client.log','a')
        LogFile.write(str(datetime.now()) + Dir + ' NoCompleted.... ' + str(Af_Size_End) + '\n')
        LogFile.close()
        time.sleep(Time_Wait_Size)
        JudgeComplete_End(Dir,Af_Size_End,Type) 

def CopyDir(Source,Target):
    NameList = ['analysis.tdf','analysis.tdf_bin','chromatography-data.sqlite','chromatography-data-pre.sqlite','SampleInfo.xml','chromatography-data.sqlite-journal']
    for File in os.listdir(Source):
        if File in NameList:
            filename = os.path.join(Source,File)
            shutil.copy(filename,Target)

# Name .d文件夹 NewDir新建文件夹 Time 现在时间
def CopyTranferDir(TOFDir):
    global DataStorge,Port,WorkDir,Version,Label,Received_Dir
    Name = TOFDir.split('\\')[-1]
    NewDir = Name.split('.')[0]
    Time = str(datetime.now()) 
    Time = Time.split('.')[0].replace('-','').replace(':','').replace(' ','')
    if not os.path.exists(DataStorge + r'\\' + Time):
        os.mkdir(DataStorge + r'\\' + Time)
        os.mkdir(DataStorge + r'\\' + Time + r'\\' + NewDir)
        os.mkdir(DataStorge + r'\\' + Time + r'\\' + NewDir + r'\\' + Name)
    CopyDir(TOFDir,DataStorge + r'\\' + Time + r'\\' + NewDir + r'\\' + Name)
    if Version == 'SP':
        shutil.copy(Example_Argument,os.path.join(DataStorge,Time,NewDir,NewDir + '_argument.txt'))
        Argument = open(os.path.join(DataStorge,Time,NewDir,NewDir + '_argument.txt'),'a')
        Argument.write('\n')
        Argument.write('-n ' + str(NewDir) + '\n')
        Argument.write('\n')
        Argument.write(' -r ' + os.path.join(str(Received_Dir),NewDir,str(Name),'analysis.tdf') + '\n')
        Argument.close()
    if Version == 'MQ':
        FileDir = os.path.join(Received_Dir,NewDir,Name)
        NameList = NewDir.split('_')
        Exp_Name = NameList[0] + '_' + NameList[1] + '_' + NameList[-1]
        shutil.copy(Example_Argument,DataStorge + r'\\' + Time + r'\\' + NewDir + r'\\' + NewDir + '_mqpar.xml')
        Mqpar = open(DataStorge + r'\\' + Time + r'\\' + NewDir + r'\\' + NewDir + '_mqpar.xml','r',encoding = 'utf-8')
        Mqpar_Text = Mqpar.read()
        Mqpar.close()
        Exp_Name = '   <experiments>\n      <string>' + str(Exp_Name) + '</string>\n   </experiments>\n'
        New_File = '   <filePaths>\n      <string>' + str(FileDir) + '</string>\n   </filePaths>\n'
        NewMqpar = Mqpar_Text.replace(Raw_File,New_File)
        NewMqpar = NewMqpar.replace(Raw_ExpName,Exp_Name)
        Output = open(DataStorge + r'\\' + Time + r'\\' + NewDir + r'\\' + NewDir + '_mqpar.xml','w',encoding='utf-8')
        Output.write(NewMqpar)
        Output.close()
        
    #print(DataStorge + '\\' + Time + '\t' + str(Port) + ':' + DataStorge + r'\\' + Time + r'\\' + NewDir + r'\\' + NewDir + '_argument.txt')
    File = TOFDir + r'\analysis.tdf_bin'
    if not os.path.exists(File):
        File = TOFDir + r'\SampleInfo.xml'
    Modified_Date = get_last_modified_time(File)
    LogFile = open(LogDir + r'\File_Send_Client.log','a')
    LogFile.write(str(TOFDir) + '\t' + str(datetime.now()) + '\t' + str(Modified_Date) + '\n' )
    LogFile.close()
    Socket_Client_OneS.TransferFile(DataStorge + '\\' + Time,Port,IP)
    shutil.rmtree(DataStorge + r'\\' + Time)

def CopyTranferFile(Name):
    global DataStorge,Port,WorkDir,Version,Received_Dir,Label
    if not Port:
        os.system(DataStorge + ' -p ' + Label + ' ' + Name)
        Modified_Date = get_last_modified_time(Name)
        LogFile = open(LogDir + r'\File_Send_Client.log','a')
        LogFile.write(str(Name) + '\t' + str(datetime.now()) + '\t' + str(Modified_Date) + '\n' )
        LogFile.close()
    else:
        NewFile = Name.split('\\')[-1]
        NewName = NewFile.split('.')[0]
        Time = str(datetime.now()) 
        Time = Time.split('.')[0].replace('-','').replace(':','').replace(' ','')
        if not os.path.exists(DataStorge + '\\' + Time):
            os.mkdir(DataStorge + '\\' + Time)
            os.mkdir(DataStorge + '\\' + Time + '\\' + NewName)
        shutil.copy(Name,DataStorge + '\\' + Time + '\\' + NewName)
        if Version == 'MQ':
            shutil.copy(Example_Argument,DataStorge + '\\' + Time + '\\' + NewName + '\\' + NewName + '_mqpar.xml')
            FileDir = os.path.join(Received_Dir,NewName,NewFile)
            NameList = NewName.split('_')
            Exp_Name = NameList[0] + '_' + NameList[1] + '_' + NameList[-1]
            Mqpar = open(DataStorge + '\\' + Time + '\\' + NewName + '\\' + NewName + '_mqpar.xml',encoding = 'utf-8')
            Mqpar_Text = Mqpar.read()
            Mqpar.close()
            Exp_Name = '   <experiments>\n      <string>' + str(Exp_Name) + '</string>\n   </experiments>\n'
            New_File = '   <filePaths>\n      <string>' + str(FileDir) + '</string>\n   </filePaths>\n'
            NewMqpar = Mqpar_Text.replace(Raw_File,New_File)
            NewMqpar = NewMqpar.replace(Raw_ExpName,Exp_Name)
            Output = open(DataStorge + '\\' + Time + '\\' + NewName + '\\' + NewName + '_mqpar.xml','w',encoding='utf-8')
            Output.write(NewMqpar)
            Output.close()
        #print(DataStorge + '\\' + Time + '\t' + str(Port) + ':' + DataStorge + '\\' + Time + '\\' + NewName + r'\\' + NewName + '_argument.txt')
        if Version == 'SP' :
            shutil.copy(Example_Argument,os.path.join(DataStorge,str(Time),NewName,NewName + '_argument.txt'))
            Argument = open(DataStorge + '\\' + Time + '\\' + NewName + '\\' + NewName + '_argument.txt','a')
            Argument.write('\n')
            Argument.write('-n ' + str(NewName) + '\n')
            Argument.write('\n')
            Argument.write(' -r '+ Received_Dir + r'\\' + NewName + r'\\' + str(NewFile) + '\n')
            Argument.close()
        #print(DataStorge + '\\' + Time + '\t' + str(Port) + ':' + DataStorge + '\\' + Time + '\\' + NewName + r'\\' + NewName + '_argument.txt')
        if Version == 'PD':
            shutil.copy(Example_Argument,os.path.join(DataStorge,str(Time),NewName,'PD_Run.param'))
        if Port:
            Socket_Client_OneS.TransferFile(DataStorge + '\\' + Time,Port,IP)
            Modified_Date = get_last_modified_time(Name)
            LogFile = open(LogDir + r'\File_Send_Client.log','a')
            LogFile.write(str(Name) + '\t' + str(datetime.now()) + '\t' + str(Modified_Date) + '\n' )
            LogFile.close()
        shutil.rmtree(DataStorge + '\\' + Time)

#Initial_Run(r'D:\Huanan\Spectronaut_Result\Test',r'D:\Huanan\Spectronaut_Result\Pic','14444:192.168.100.53','1.6','LabelTest','None')
