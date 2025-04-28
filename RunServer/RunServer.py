#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os,sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread
from functools import partial
import Ui_SP_Server,Ui_MQ_Server,Ui_PD_Server
from datetime import datetime
import shutil
from Function_Tool import *
import Socket_Server_MultiC
import sqlite3

# Run_Server主函数 开启服务
class Thread_Server(QThread):
    Window = ''
    Server_Software = ''
    def __init__(self):
        super(Thread_Server,self).__init__()
    def run(self):
        Time = str(datetime.now()) 
        Time = Time.split('.')[0].replace('-','').replace(':','').replace(' ','')
        Port = self.Window.Input_Port.text()
        Received_Dir = self.Window.Show_Received.text().replace('/','\\')
        Exe_Script = self.Window.Show_Exe.text().replace('/','\\')
        # Generate Script & Param file
        if self.Server_Software == 'MQ':
            SP_Param = self.Window.Show_Param.text().replace('/','\\')
            Argument_Param = str(Received_Dir) + r'\\' + str(Time) + '_Example_mqpar.xml'
            RawFile = self.Window.Show_RawFile.text().replace('/','\\')
            ExpName = self.Window.Show_Experiment.text().replace('/','\\')
            shutil.copy(SP_Param,Argument_Param)
            Argument = open(Argument_Param,'a')
            Argument.write('#The_Directory_of_Receive_data^$' + str(Received_Dir) + '\n')
            Argument.write('#The_Directory_of_RawFile^$' + str(RawFile) + '\n')
            Argument.write('#The_Name_of_Experiment^$' + str(ExpName) + '\n')
            Argument.close()
        if self.Server_Software == 'PD':
            SP_Param = self.Window.Show_Param.text().replace('/','\\')
            Argument_Param = str(Received_Dir) + r'\\' + str(Time) + '_Example.param'
            shutil.copy(SP_Param,Argument_Param)
            Argument = open(Argument_Param,'a')
            Argument.write('\n' + '#The_Directory_of_Receive_data^$' + str(Received_Dir) + '\n')
            Argument.close()
        if self.Server_Software == 'SP':
            OutputDir = self.Window.OutputDir.text().replace('/','\\')
            SP_Library = self.Window.Show_Library.text().replace('/','\\')
            SP_Fasta = self.Window.Show_Fasta.text().replace('/','\\')
            SP_WorkFlow = self.Window.Show_WorkFlow.text().replace('/','\\')
            #print(SP_Library + '\t' + SP_Fasta + '\t' + SP_WorkFlow)
            Argument = open(str(OutputDir) + r'\\' + str(Time) + '_Example_arguments.txt','w')
            if SP_Library != '':
                Argument.write(r'-a ' + str(SP_Library) + '\n')
            else:
                Argument.write(r' -direct ' + '\n')
            Argument.write('\n')
            Argument.write(r'-s ' + str(SP_WorkFlow) + ' ' + '\n')
            Argument.write('\n')
            Argument.write(r'-o ' + str(OutputDir) + ' \n')
            Argument.write('\n')
            Argument.write(r'-fasta ' + str(SP_Fasta) + ' \n')
            Argument.write('\n')
            Argument.write(r'#SetReceiced_Dir^$' + str(Received_Dir) + ' \n')
            Argument.close()
        Socket_Server_MultiC.RunService(Port,Received_Dir,Exe_Script,self.Server_Software)

def UpdateStatus(Window,Software):
    Window.Server_Status.setText('Monitoring...')
    Window.RunServer.setEnabled(False)
    Window.Cal = Thread_Server()  # 创建一个线程
    Window.Cal.Window = Window
    Window.Cal.Server_Software = Software
    Window.Cal.start()  # 线程启动

## 数据库添加
def Sql_Add(Window,Type):
    Port = Window.Input_Port.text()
    ExeScript_Dir = Window.Show_Exe.text().replace('/','\\')
    Received_Dir = Window.Show_Received.text().replace('/','\\')
    if Type == 'SP':
        ParamFile = 'None'
        Library = Window.Show_Library.text().replace('/','\\')
        Fasta = Window.Show_Fasta.text().replace('/','\\')
        WorkFlow = Window.Show_WorkFlow.text().replace('/','\\')
        OutputDir = Window.OutputDir.text().replace('/','\\')
        ID = 'SP-' + str(Port)
    if Type == 'MQ':
        ParamFile = Window.Show_Param.text().replace('/','\\')
        Library = Window.Show_RawFile.text().replace('/','\\')
        Fasta = Window.Show_Experiment.text().replace('/','\\')
        WorkFlow = 'None'
        OutputDir = 'None'
        ID = 'MQ-' + str(Port)
    if Type == 'PD':
        ParamFile = Window.Show_Param.text().replace('/','\\')
        Library = Window.Show_UserName.text().replace('/','\\')
        Fasta = Window.Show_HostName.text().replace('/','\\')
        ID = 'PD-' + str(Port)
        WorkFlow = 'None'
        OutputDir = 'None'
        
    Query_ID = '"' + ID + '"'
    Sql_Add = 'INSERT INTO Param VALUES(''"' + ID + '","' + ExeScript_Dir + '","' + Received_Dir + '","' + ParamFile + '","' + OutputDir + '","' + Fasta + '","' + Library + '","' + WorkFlow+ '")'
    Sql_Del = 'DELETE FROM Param WHERE ID = ' + Query_ID
    try:
        ParamSql.execute("SELECT * FROM Param WHERE ID = " + Query_ID)
        ParamSql.execute(Sql_Del)
        ParamSql.execute(Sql_Add)
    except:
        ParamSql.execute(Sql_Add)
    
    ConnSql.commit()

## 数据库查询
def Sql_Query(Window,Type):
    Port = Window.Input_Port.text()
    ID = Type + '-' + str(Port)
    Query_ID = '"' + ID + '"'
    try:
        ParamSql.execute("SELECT * FROM Param WHERE ID = " + Query_ID)
    except:
        msg_box = QMessageBox(QMessageBox.Warning,'Error','Port：' + TestPort + ' Not Find')
        msg_box.exec_()
    
    Query_Info = ParamSql.fetchone()
    if Query_Info:
        Window.Input_Port.setText(Query_Info[0].split('-')[1])
        Window.Show_Exe.setText(Query_Info[1])
        Window.Show_Received.setText(Query_Info[2])
        if Type == 'SP':
            Window.OutputDir.setText(Query_Info[4])
            Window.Show_Fasta.setText(Query_Info[5])
            Window.Show_Library.setText(Query_Info[6])
            Window.Show_WorkFlow.setText(Query_Info[7])
        if Type == 'MQ':
            Window.Show_Param.setText(Query_Info[3])
            Window.Show_RawFile.setText(Query_Info[5])
            Window.Show_Experiment.setText(Query_Info[6])
        if Type == 'PD':
            Window.Show_Param.setText(Query_Info[3])
            Window.Show_UserName.setText(Query_Info[5])
            Window.Show_HostName.setText(Query_Info[6])
# 主面板设置
Server = sys.argv[1]
Path = os.getcwd()
ConnSql = sqlite3.connect(Path + r'\Param.db')
ParamSql = ConnSql.cursor()

# 参数设置-数据库初始
Sql_Inital = '''CREATE TABLE IF NOT EXISTS Param
           (ID TEXT,
            ExeScript_Dir TEXT,
            Received_Dir TEXT,
            Param TEXT,
            Result_Dir TEXT,
            Fasta TEXT,
            Library TEXT,
            WorkFlow TEXT);'''
ParamSql.execute(Sql_Inital)
ConnSql.commit()

if __name__ == '__main__':
    if Server == 'SP':
        print('SP: ' + str(os.getpid()))
        SP_SE_App = QApplication(sys.argv)
        SP_SEMainWindow = QWidget()
        #SEWindow = RunServer.Ui_Form()
        SP_SEWindow = Ui_SP_Server.Ui_Form()
        SP_SEWindow.setupUi(SP_SEMainWindow)
        SP_SEMainWindow.show()
        SP_SEWindow.GetExe.clicked.connect(partial(ChooseParam,SP_SEWindow,'Exe'))
        SP_SEWindow.GetReceived.clicked.connect(partial(ChoosePath,SP_SEWindow,'Received'))
        SP_SEWindow.GetResult.clicked.connect(partial(ChoosePath,SP_SEWindow,'Output'))
        SP_SEWindow.GetWorkFlow.clicked.connect(partial(ChooseParam,SP_SEWindow,'WorkFlow'))
        SP_SEWindow.GetLibrary.clicked.connect(partial(ChooseParam,SP_SEWindow,'Library'))
        SP_SEWindow.GetFasta.clicked.connect(partial(ChooseParam,SP_SEWindow,'Fasta'))
        SP_SEWindow.Input_Port.setText('13579')
        SP_SEWindow.RunServer.setEnabled(False)
        SP_SEWindow.checkBox.stateChanged.connect(partial(CheckStatus,SP_SEWindow,'Server'))
        SP_SEWindow.Record_Add.clicked.connect(partial(Sql_Add,SP_SEWindow,'SP'))
        SP_SEWindow.Record_Query.clicked.connect(partial(Sql_Query,SP_SEWindow,'SP'))
        SP_SEWindow.RunServer.clicked.connect(partial(UpdateStatus,SP_SEWindow,'SP'))
        SP_SE_App.exec_()
    if Server == 'MQ':
        print('MQ: ' + str(os.getpid()))
        MQ_SE_App = QApplication(sys.argv)
        MQ_SEMainWindow = QWidget()
        #SEWindow = RunServer.Ui_Form()
        MQ_SEWindow = Ui_MQ_Server.Ui_Form()
        MQ_SEWindow.setupUi(MQ_SEMainWindow)
        MQ_SEMainWindow.show()
        MQ_SEWindow.GetExe.clicked.connect(partial(ChooseParam,MQ_SEWindow,'Exe'))
        MQ_SEWindow.GetReceived.clicked.connect(partial(ChoosePath,MQ_SEWindow,'Received'))
        MQ_SEWindow.GetParam.clicked.connect(partial(ChooseParam,MQ_SEWindow,'MQ_Param'))
        #MQ_SEWindow.GetRawFile.clicked.connect(partial(ChooseParam,MQ_SEWindow,'RawFile'))
        MQ_SEWindow.Input_Port.setText('13579')
        MQ_SEWindow.RunServer.setEnabled(False)
        MQ_SEWindow.checkBox.stateChanged.connect(partial(CheckStatus,MQ_SEWindow,'Server'))
        MQ_SEWindow.Record_Add.clicked.connect(partial(Sql_Add,MQ_SEWindow,'MQ'))
        MQ_SEWindow.Record_Query.clicked.connect(partial(Sql_Query,MQ_SEWindow,'MQ'))
        MQ_SEWindow.RunServer.clicked.connect(partial(UpdateStatus,MQ_SEWindow,'MQ'))
        MQ_SE_App.exec_()
    if Server == 'PD':
        print('PD: ' + str(os.getpid()))
        PD_SE_App = QApplication(sys.argv)
        PD_SEMainWindow = QWidget()
        PD_SEWindow = Ui_PD_Server.Ui_Form()
        PD_SEWindow.setupUi(PD_SEMainWindow)
        PD_SEMainWindow.show()
        PD_SEWindow.GetExe.clicked.connect(partial(ChooseParam,PD_SEWindow,'Exe'))
        PD_SEWindow.GetReceived.clicked.connect(partial(ChoosePath,PD_SEWindow,'Received'))
        PD_SEWindow.GetParam.clicked.connect(partial(ChooseParam,PD_SEWindow,'PD_Param'))
        PD_SEWindow.Input_Port.setText('13579')
        PD_SEWindow.RunServer.setEnabled(False)
        
        PD_SEWindow.checkBox.stateChanged.connect(partial(CheckStatus,PD_SEWindow,'Server'))
        PD_SEWindow.Record_Add.clicked.connect(partial(Sql_Add,PD_SEWindow,'PD'))
        PD_SEWindow.Record_Query.clicked.connect(partial(Sql_Query,PD_SEWindow,'PD'))
        PD_SEWindow.RunServer.clicked.connect(partial(UpdateStatus,PD_SEWindow,'PD'))
        PD_SE_App.exec_()