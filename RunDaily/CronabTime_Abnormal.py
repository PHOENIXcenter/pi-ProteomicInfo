## 目标针对特定文件夹，定时启动程序，监测新产生的文件夹结果并运行新结果
import os
import sys
import time
import schedule
from datetime import datetime,timedelta
import shutil
import pandas as pd
import Socket_Client
import sqlite3
from Function_Tool import *
import numpy as np
import scipy.stats as stats
#import SP_DataDeal_IRT,MQ_DataDeal_IRT,PD_DataDeal_NoIRT
from PyQt5.QtWidgets import QMessageBox
import subprocess

Path = os.getcwd()

def GetDir(Work_Dir,SetDir,Software):
    Date = str(datetime.now()).split(' ')[0]
    SetOutput_Dir = SetDir + '\\' + str(Date) + r'_QC_Report'
    if Software == 'SP':
        Label = [Label for Label in os.listdir(Work_Dir) if Label.endswith('Report_huiyan (Normal).xls')]
        if not Label:
            Label = [Label for Label in os.listdir(Work_Dir) if Label.endswith('Report_huiyan (Normal).tsv')]
        File = os.path.join(Work_Dir,Label[-1])
        Label = File.split('\\')[-2].split('.')[0]
        NameLabel = os.path.join(SetOutput_Dir,str(Label) + '_SP_Stat_Summary.txt')
    if Software == 'MQ':
        Label = Work_Dir.split('\\')[-1]
        NameLabel  = os.path.join(SetOutput_Dir,str(Label) + '_MQ_Stat_Summary.txt')
    return(NameLabel,SetOutput_Dir)


# 新文件处理
def Get_File_Info(NewFile):
    Data = pd.read_table(NewFile,sep = '\t')
    Num_Protein = Data['Number of ProteinGroups'][0]
    Num_Peptides = Data['Number of Peptides'][0]
    Quantity_Sum = Data['Protein Quantity (Sum)'][0]
    Quantity_Median = Data['Protein Quantity (Median)'][0]
    
    if 'Median of RT Length (s)' not in list(Data):
        RT_Length = Data['Retention_length_Median (s)'][0]
    else:
        RT_Length = Data['Median of RT Length (s)'][0]
    
    if 'Median of PPM' not in list(Data):
        PPM_Median = Data['Median_PPM'][0]
    else:
        PPM_Median = Data['Median of PPM'][0]
    
    return(Num_Protein,Num_Peptides,Quantity_Sum,Quantity_Median,RT_Length,PPM_Median)

# 计算Grubb的临界值
def Calculate_critical_value(size, alpha):
    t_dist = stats.t.ppf(1 - alpha / (2 * size), size - 2)
    numerator = (size - 1) * t_dist
    denominator = np.sqrt(size) * np.sqrt(size - 2 + np.square(t_dist))
    critical_value = numerator / denominator
    return critical_value

# 循环判断
def Grubb_Test(Input_List,Alpha,Outlier):
    # GSED方法-基于假设检验依次排除异常值
    Mean = np.mean(Input_List)
    Std = np.std(Input_List)
    Outlier = abs(Outlier - Mean) 
    Grubb = Outlier / Std
    Threshold = Calculate_critical_value(len(Input_List),Alpha)
    if Grubb > Threshold:
        return('Abnormal')
    else:
        return('Normal')

# 箱线图四分法
def Box_Quantile(Input_List,Judge_Value):
    List_stat_PPM = np.percentile(Input_List,(25,75))
    Percent25 = List_stat_PPM[0]
    Percent75 = List_stat_PPM[1]
    Gap = float(Percent75) - float(Percent25)
    Gap = float(Gap) * 1.5
    Min = float(Percent25) - Gap
    Max = float(Percent75) + Gap
    if float(Judge_Value) < Min or float(Judge_Value) > Max:
        return('Abnormal')
    else:
        return('Normal')

# 判断是否为异常值
def Judge_Abnormal(Value_Info,Threshold_Value):
    Threshold = 'Normal'
    if float(Value_Info[0]) < float(Threshold_Value[1]) or float(Value_Info[0]) > float(Threshold_Value[7]):
        Threshold = 'Abnormal'
    if float(Value_Info[1]) < float(Threshold_Value[2]) or float(Value_Info[1]) > float(Threshold_Value[8]):
        Threshold = 'Abnormal'
    if Value_Info[2] != 'NA':
        if float(Value_Info[2]) < float(Threshold_Value[3]) or float(Value_Info[2]) > float(Threshold_Value[9]):
            Threshold = 'Abnormal'
        if float(Value_Info[3]) < float(Threshold_Value[4]) or float(Value_Info[3]) > float(Threshold_Value[10]):
            Threshold = 'Abnormal'
    if float(Value_Info[4]) < float(Threshold_Value[5]) or float(Value_Info[4]) > float(Threshold_Value[11]):
        Threshold = 'Abnormal'
    if float(Value_Info[5]) < float(Threshold_Value[6]) or float(Value_Info[5]) > float(Threshold_Value[12]) or abs(float(Value_Info[5])) > 5:
        Threshold = 'Abnormal'
    return Threshold

# 实验室过往标准蛋白-5% 肽段10% 信号强度-25%
def Judge_Gap(Value,Average,Percent):
    Gap = float(Average) * Percent + float(Average)
    Min = int(Value) - int(Gap)
    Max = int(Value) + int(Gap)
    if Value >= Min and Value <= Max:
        Feature_Gap = 'Normal'
    else:
        Feature_Gap = 'Abnormal'
    
    return(Feature_Gap)

# 统计学检验判断结果是否正常
def Judge_File(JudgeFile,Value_Mean,Feature):
    Judge_Data = pd.read_table(JudgeFile,sep = '\t')
    RawFile = JudgeFile.split('\\')[-1].split('.')[0]
    Reference_Data = pd.read_table(Path + r'\\Config\\' + str(Feature) + '.txt',sep = '\t')
    Alpha = 0.05
    Exist_Abnormal = 'False'
    List_exclude = ['Number of ProteinGroups','Number of Peptides','Protein Quantity (Sum)','Protein Quantity (Median)','Median of RT Length (s)','Retention_length_Median (s)','Median of PPM','Median_PPM']
    List_Label = list(Judge_Data)
    Output = open(JudgeFile,'a')
    Output.write('#outlier#' + '\n')
    Output.write('Raw file' + '\t' + 'Lable' + '\t' + 'Judge_BoxIQR' + '\t' + 'Judge_GrubbTest' + '\t' + 'Judge_Experience' + '\t' + 'Judge_Decide' +'\n')
    for Label in List_Label:
        if Label not in List_exclude:
            continue
        Temp = Reference_Data[Label]
        Temp = Temp.tolist()
        Value = Judge_Data[Label][0]
        Box_Outlier,Grubb_Outlier,Judge_Exp = 'Normal','Normal','Normal'
        Box_Outlier = Box_Quantile(Temp,Value)
        Grubb_Outlier = Grubb_Test(Temp,Alpha,Value)
        if Label == 'Number of ProteinGroups':
            Judge_Exp = Judge_Gap(Value,Value_Mean[1],0.05)
        if Label == 'Number of Peptides':
            Judge_Exp = Judge_Gap(Value,Value_Mean[2],0.01)
        if Label == 'Protein Quantity (Sum)' and int(Value_Mean[3]) != 0:
            Judge_Exp = Judge_Gap(Value,Value_Mean[3],0.25)
        if Label == 'Median of PPM' or Label == 'Median_PPM':
            if abs(float(Value)) > 5:
                Judge_Exp = 'Abnormal'
        Decide_Judge = [Box_Outlier,Grubb_Outlier,Judge_Exp]
        if Decide_Judge.count('Abnormal') == 1:
            Judge_Decide = 'Warn'
        elif Decide_Judge.count('Abnormal') > 1:
            Judge_Decide = 'Abnormal'
        if Box_Outlier == 'Abnormal' or Grubb_Outlier == 'Abnormal' or Judge_Exp == 'Abnormal':
            Output.write(str(RawFile) + '\t' + str(Label) + '\t' + str(Box_Outlier) + '\t' + str(Grubb_Outlier) + '\t' + str(Judge_Exp) + '\t' + str(Judge_Decide) + '\n')
            Exist_Abnormal = 'True'
    Output.close()
    # 是否存在异常对数据进行判读，无异常数据不修改原内容
    if Exist_Abnormal != 'True':
        Outlier_Dir = '\\'.join(str(JudgeFile).split('\\')[0:-1])
        Output = open(Outlier_Dir + '\Temp.txt','w')
        for Line in open(JudgeFile):
            if Line.startswith('#outlier#'):
                break
            else:
                Output.write(Line)
        Output.close()
        shutil.move(Outlier_Dir + '\Temp.txt',JudgeFile)
    Send_Wechat(JudgeFile)
    return(Exist_Abnormal)

def Send_Wechat(SendFile):
    # 发送文件
    Wechat_File = os.path.join(os.getcwd(),'Config','Wechat_File.txt')
    if os.path.exists(Wechat_File):
        for Info in open(Wechat_File):
            Info = Info.strip().split(':')
            IP = '192.168.100.91'
            Port = 11111
            if Info[0] == 'IP':
                IP = Info[1]
            if Info[0] == 'Socket_Port':
                Port = int(Info[1])
        Socket_Client.TransferFile(SendFile,IP,Port)

## 初始记录
def Data_Extract(Parm1,Pamr2,Pamr3,Pamr4,IRT_Add,Pamr6,Pamr7):
    global Target_Dir,Software,Num,Indicate,List_Info
    Target_Dir = Parm1
    Software = Pamr2
    Num = Pamr3
    Output_Dir = Pamr4
    Indicate,List_Info = Pamr6,Pamr7
    if not os.path.exists(Target_Dir + '\\Complete_FileName_List.txt'):
        Output = open(Target_Dir + '\\Complete_FileName_List.txt','w')
        for File in os.listdir(Target_Dir):
            if os.path.isdir(Target_Dir + '\\' + File):
                Output.write(str(File) + '\n')
        Output.close()
    print(str(datetime.now()) + ' Initial Record Done')
    
    ConnSql = sqlite3.connect(Path + r'\Param.db')
    ParamSql = ConnSql.cursor()
    
    ## 数据库添加
    def Sql_Add(ID,Info_List):
        Query_ID = '"' + ID + '"'
        Sql_Add_Info = 'INSERT INTO Reference_Data VALUES(''"' + ID + '","' + str(Info_List[0]) + '","' + str(Info_List[1]) + '","' + str(Info_List[2]) + '","' + str(Info_List[3]) + '","' + str(Info_List[4]) + '","' + str(Info_List[5]) + '","' + str(Info_List[6]) + '","' + str(Info_List[7]) + '","' + str(Info_List[8]) + '","' + str(Info_List[9]) + '","' + str(Info_List[10]) + '","' + str(Info_List[11]) + '")'
        Sql_Del = 'DELETE FROM Reference_Data WHERE ID = ' + Query_ID
        try:
            ParamSql.execute("SELECT * FROM Reference_Data WHERE ID = " + Query_ID)
            ParamSql.execute(Sql_Del)
            ParamSql.execute(Sql_Add_Info)
        except:
            ParamSql.execute(Sql_Add_Info)
        
        ConnSql.commit()
    
    ## 数据库查询
    def Sql_Query(ID):
        Query_ID = '"' + ID + '"'
        ID_Mean = '"' + ID + '@Mean' + '"'
        try:
            ParamSql.execute("SELECT * FROM Reference_Data WHERE ID = " + Query_ID)
        except:
            msg_box = QMessageBox(QMessageBox.Information,'Error','ID：' + ID + ' Not Find')
            msg_box.exec_()
        Query_Info = ParamSql.fetchone()
        try:
            ParamSql.execute("SELECT * FROM Reference_Data WHERE ID = " + ID_Mean)
        except:
            msg_box = QMessageBox(QMessageBox.Information,'Error','ID：' + ID + '@Mean Not Find')
            msg_box.exec_()
        Query_Info_Mean = ParamSql.fetchone()
        return(Query_Info,Query_Info_Mean)
    
    # 更新参考文件信息 Update_Info(Label_Set,File)
    def Update_Info(Label_Set,File):
        Reference_File = Path + r'\Config\\' + Label_Set + '.txt'
        with open(File,'r',encoding = 'utf-8') as f:
            Value_Info = f.readlines()
        
        Value_Info = Value_Info[1]
        
        with open(Reference_File,'r',encoding = 'utf-8') as f:
            Lines = f.readlines()
        Output = open(Reference_File,'w')
        for n in range(0,len(Lines)):
            if len(Lines) > 31 and n == 1:
                continue
            Output.write(Lines[n])
        Output.write(Value_Info)
        Output.close()
        Data = pd.read_table(Reference_File,sep = '\t')
        ColList = ['Raw file','Number of ProteinGroups','Number of Peptides','Protein Quantity (Sum)','Protein Quantity (Median)']
        
        if 'Median of RT Length (s)' not in list(Data):
            ColList.append('Retention_length_Median (s)')
        else:
            ColList.append('Median of RT Length (s)')
        if 'Median of PPM' not in list(Data):
            ColList.append('Median_PPM')
        else:
            ColList.append('Median of PPM')
        
        Data = Data[ColList]
        Min_Max,Mean_Mean = GetValue(Data)
        Sql_Add(Label_Set,Min_Max)
        Sql_Add(Label_Set + '@Mean',Mean_Mean)
    
    def WriteLog(Info,NameLabel):
        LogError = open(Target_Dir + r'\File_Send_Error_Log_Record.txt','a')
        LogError.write('-----------------------------------------------------------------------------------------' + '\n')
        LogError.write(str(datetime.now()) + ': Transfer File Failed' + '\n')
        LogError.write(NameLabel + r'_Stat_Summary.txt' + '\n')
        LogError.write(str(Info))
        LogError.write('\n')
        LogError.write('-----------------------------------------------------------------------------------------' + '\n')
        LogError.close()
    # 指示是否异常
    def Report_Abnormal_Info(File):
        print('--------------------------')
        #考虑多个条件
        for Label_Set in List_Info:
            Label = Label_Set.split('-')
            TT = [i for i in Label if i in str(File)]
            # 符合条件的新文件--判断是否为异常值
            if Label == TT:
                Value_Info = Get_File_Info(File)
                #print('Do')
                Threshold_Value,Value_Mean = Sql_Query(Label_Set)
                Threshold = Judge_Abnormal(Value_Info,Threshold_Value)
                #print(Threshold)
                # 范围内
                if Threshold == 'Normal':
                    Update_Info(Label_Set,File)
                    Send_Wechat(File)
                    continue
                else:
                    Decide_Update =  Judge_File(File,Value_Mean,Label_Set)
                    #print(Decide_Update)
                    if Decide_Update == 'False':
                        Update_Info(Label_Set,File)
            else:
                Send_Wechat(File)
    
    def Extract_Info_Job(Dir):
        global Target_Dir
        global Dic_Intial_Record
        Dic_Intial_Record = {}
        for File in open(Target_Dir + '\\Complete_FileName_List.txt'):
            Dic_Intial_Record[File[:-1]] = 0
        if Software == 'SP':
            for File in os.listdir(Dir):
                if os.path.isdir(Target_Dir + '\\' + File) and os.path.exists(Target_Dir + '\\' + File + r'\RunSummaries') and File not in Dic_Intial_Record.keys():
                    Judge = 'FALSE'
                    try:
                        NameLabel,SetOutput_Dir = GetDir(Target_Dir + '\\' + File,Output_Dir,'SP')
                        #print(SetOutput_Dir)
                        #print(Path + r'\Core\RunStat\RunStat.exe ' + os.path.join(Target_Dir,File) + ' ' + SetOutput_Dir + ' ' + IRT_Add + ' SP TRUE None')
                        subprocess.Popen(Path + r'\Core\RunStat\RunStat.exe ' + os.path.join(Target_Dir,File) + ' ' + SetOutput_Dir + ' ' + IRT_Add + ' SP TRUE None')
                        #NameLabel = SP_DataDeal_IRT.SP_Extract(Target_Dir + '\\' + File,Output_Dir,IRT_Add)
                        if Indicate == 'Monitoring':
                            Report_Abnormal_Info(NameLabel)
                        else:
                            Send_Wechat(NameLabel)
                        Dic_Intial_Record[File] = 0
                        #print(Dic_Intial_Record)
                    except Exception as e:
                        WriteLog(str(e),File)
        if Software == 'MQ':
            for File in os.listdir(Target_Dir):
                if File not in Dic_Intial_Record.keys():
                    #print(os.path.join(Target_Dir,File))
                    if os.path.exists(Target_Dir + r'\\' + File + r'\combined\txt\evidence.txt') and os.path.getsize(Target_Dir + r'\\' + File + r'\combined\txt\evidence.txt') > 3000 :
                        Judge = 'FALSE'
                        try:
                            NameLabel,SetOutput_Dir = NameLabel = GetDir(Target_Dir + '\\' + File,Output_Dir,'MQ')
                            #print(Path + r'\Core\RunStat\RunStat.exe ' + os.path.join(Target_Dir,File) + ' ' + SetOutput_Dir + ' ' + IRT_Add + ' MQ TRUE None')
                            subprocess.Popen(Path + r'\Core\RunStat\RunStat.exe ' + os.path.join(Target_Dir,File) + ' ' + SetOutput_Dir + ' ' + IRT_Add + ' MQ TRUE None')
                            if Indicate == 'Monitoring':
                                Report_Abnormal_Info(NameLabel)
                            else:
                                Send_Wechat(NameLabel)
                            Dic_Intial_Record[File] = 0
                        except Exception as e:
                            WriteLog(str(e),File)
        if Software == 'PD':
            for File in os.listdir(Dir):
                if os.path.isdir(Target_Dir + '\\' + File) and len(os.listdir(Target_Dir + '\\' + File)) >= 14 and File not in Dic_Intial_Record.keys():
                    FileList = os.listdir(Target_Dir + '\\' + File)
                    Temp = [Name for Name in FileList if Name.split('.')[-1] == 'raw']
                    Temp2 = Temp.copy()
                    while len(Temp) > 0:
                        Info = Temp[0]
                        del Temp[0]
                        Name = Info.split('.')[0:-1][0]
                        Protein_File = Target_Dir + '\\' + File + '\\' + Name + r'_Proteins.txt'
                        Judge = 'False'
                        if os.path.exists(Protein_File):
                            Size = os.path.getsize(Protein_File)
                            if 'Blank' in Name or int(Size) < 10000:
                                Judge = 'False'
                                break
                            else:
                                Judge = 'True'
                    Judge2 = 'FALSE'
                    if Judge == 'True':
                        for Info in Temp2:
                            Name = Info.split('.')[0:-1][0]
                            try:
                                NameLabel = os.path.join(Output_Dir, str(Name) + '_PD_Stat_Summary.txt')
                                subprocess.Popen(Path + r'\Core\RunStat\RunStat.exe ' + os.path.join(Target_Dir,File) + ' ' + Output_Dir + ' ' + IRT_Add + ' PD TRUE ' + str(Name))
                                if Indicate == 'Monitoring':
                                    Report_Abnormal_Info(NameLabel)
                                else:
                                    Send_Wechat(NameLabel)
                                Dic_Intial_Record[File] = 0
                            except Exception as e:
                                WriteLog(str(e),File)
        NewRecord = open(Target_Dir + '\\Complete_FileName_List.txt','w')
        for Key in Dic_Intial_Record.keys():
            NewRecord.write(str(Key) + '\n')
        NewRecord.close()
        print(str(datetime.now()) + " Info Record Done")
    
    #schedule.every(10).seconds.do(Extract_Info_Job,Dir = Target_Dir)
    schedule.every(int(Num)).minutes.do(Extract_Info_Job,Dir = Target_Dir)

    while True:
        schedule.run_pending()