#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread
from functools import partial
import time
from datetime import datetime
import shutil
import Multi_Acquisition, MQ_Designer, PD_Designer, SP_Designer, MultiRunQC_Ui, Computer_Set,Monitor,Machine_monitor
from multiprocessing import Process

global IP_Path
IP_Path = os.path.join(os.getcwd(),'Config','IP_Config.txt')
if not os.path.exists(IP_Path) or  os.path.getsize(IP_Path) == 0:
    IP_Initial = open(IP_Path,'w')
    IP_Initial.write('#Example:192.168.168.168')
    IP_Initial.close()
if not os.path.exists(r'D:\AutoRun'):
    os.mkdir(r'D:\AutoRun')
    if not os.path.exists(r'D:\AutoRun\Log'):
        os.mkdir(r'D:\AutoRun\Log')

# 定义StackPage转换
def ShowHome():
    ui.StackPage.setCurrentIndex(0)
def ShowMQ():
    ui.StackPage.setCurrentIndex(2)
def ShowSP():
    ui.StackPage.setCurrentIndex(1)
def ShowPD():
    ui.StackPage.setCurrentIndex(3)

## 解读参数文件内容
class Thread_Server(QThread):
    Time = str(datetime.now()) 
    Time = Time.split('.')[0].replace('-','').replace(':','').replace(' ','')
    Class = 'Initial'
    Window = ''
    def __init__(self):
        super(Thread_Server,self).__init__()
    def run(self):
        Port = self.Window.Port.text()
        Computer_Name = self.Window.comboBox.currentText()
        Get_Computer_Pairs()
        Computer_IP = Dic_Info[Computer_Name]
        Analyzer_Info = str(Port) + ':' + str(Computer_IP)
        if self.Class == 'Mon':
            Machine = self.Window.Machine.currentText()
            if Machine == 'timsTOF' or Machine == 'SCIEX':
                filePath = self.Window.Show_Acq_File.toPlainText().replace('/','\\')
            else:
                filePath = self.Window.Show_Acq.toPlainText().replace('/','\\')
            Name_Abbr = self.Window.Abbr_Name.text()
            timeInterval = self.Window.Time.text()
            LogPattern = self.Window.LogFile.toPlainText()
            ErrorPattern = self.Window.Error_Info.toPlainText()
            Machine_monitor.Initial_Run(Machine,Name_Abbr,LogPattern,ErrorPattern,filePath,timeInterval,Analyzer_Info)
        else:
            Param_File = self.Window.Show_Param.toPlainText().replace('/','\\')
            Acq_Dir = self.Window.Show_Acq.toPlainText().replace('/','\\')
            
            if self.Class == 'PD' and self.Window.radioButton.isChecked():
                DataStorge = self.Window.Show_Daemon.toPlainText().replace('/','\\')
            else:
                DataStorge = self.Window.Show_Storge.toPlainText().replace('/','\\')
            if self.Class == 'SP':
                Example_Argument = DataStorge + r'\\' + str(self.Time) + '_Example_argument.txt'
            if self.Class == 'MQ':
                Example_Argument = DataStorge + r'\\' + str(self.Time) + '_Example_mqpar.xml'
            if self.Class == 'PD' and self.Window.radioButton_2.isChecked():
                Example_Argument = DataStorge + r'\\' + str(self.Time) + '_Example.param'
            if self.Class == 'PD' and self.Window.radioButton.isChecked():
                self.Time = Param_File
                self.Class = 'DaemonExe'
            else:
                shutil.copy(Param_File,Example_Argument)
            
            Multi_Acquisition.Initial_Run(Acq_Dir,DataStorge,str(Analyzer_Info),self.Class,str(self.Time))
            #print(Acq_Dir + '\t' + DataStorge + '\t' + str(Analyzer_Info) + '\t' + self.Class + '\t' + str(self.Time))

# 目标功能 点击按钮是跳出新界面（原三个界面之一），与主界面相互不影响，具有原界面的功能
def Single_MQ():
    global MQWindow
    MQ_App = QApplication(sys.argv)
    MQMainWindow = QWidget()
    MQWindow = MQ_Designer.Ui_Form()
    MQWindow.setupUi(MQMainWindow)
    MQMainWindow.show()
    Name_List = GetName_Info()
    MQWindow.comboBox.addItems(Name_List)
    MQWindow.DataStorge.clicked.connect(partial(ChoosePath,'Storge',MQWindow))
    MQWindow.Acquisition.clicked.connect(partial(ChoosePath,'Acq',MQWindow))
    MQWindow.Param.clicked.connect(partial(ChooseParam,'Param',MQWindow))
    MQWindow.Run.clicked.connect(partial(UpdateStatus,'MQ',MQWindow))
    MQWindow.UpData_Computer.clicked.connect(partial(UpdateIP,'MQ'))
    MQWindow.Computer.clicked.connect(partial(Run_Single_Page,'PC'))
    MQ_App.exec_()

def Single_PD():
    global PDWindow, Dic_Computer
    PD_App = QApplication(sys.argv)
    PDMainWindow = QWidget()
    PDWindow = PD_Designer.Ui_Form()
    PDWindow.setupUi(PDMainWindow)
    PDMainWindow.show()
    Name_List = GetName_Info()
    PDWindow.comboBox.addItems(Name_List)
    PDWindow.radioButton.setChecked(True)
    PDWindow.DataStorge.hide()
    PDWindow.Show_Storge.hide()
    PDWindow.comboBox.setEnabled(False)
    PDWindow.Port.hide()
    PDWindow.PD_Acquisition_3.setEnabled(False)
    PDWindow.DataStorge.clicked.connect(partial(ChoosePath,'Storge',PDWindow))
    PDWindow.Acquisition.clicked.connect(partial(ChoosePath,'Acq',PDWindow))
    PDWindow.Param.clicked.connect(partial(ChooseParam,'Param',PDWindow))
    PDWindow.DaemonExe.clicked.connect(partial(ChooseParam,'DaemonExe',PDWindow))
    PDWindow.Computer.clicked.connect(partial(Run_Single_Page,'PC'))
    PDWindow.UpData_Computer.clicked.connect(partial(UpdateIP,'PD',PDWindow))
    PDWindow.Run.clicked.connect(partial(UpdateStatus,'PD',PDWindow))
    PD_App.exec_()

def Single_SP():
    global SPWindow, Dic_Computer
    SP_App = QApplication(sys.argv)
    SPMainWindow = QWidget()
    SPWindow = SP_Designer.Ui_Form()
    SPWindow.setupUi(SPMainWindow)
    SPMainWindow.show()
    Name_List = GetName_Info()
    SPWindow.comboBox.addItems(Name_List)
    SPWindow.DataStorge.clicked.connect(partial(ChoosePath,'Storge',SPWindow))
    SPWindow.Acquisition.clicked.connect(partial(ChoosePath,'Acq',SPWindow))
    SPWindow.Param.clicked.connect(partial(ChooseParam,'Param',SPWindow))
    SPWindow.Computer.clicked.connect(partial(Run_Single_Page,'PC'))
    SPWindow.UpData_Computer.clicked.connect(partial(UpdateIP,'SP',SPWindow))
    SPWindow.Run.clicked.connect(partial(UpdateStatus,'SP',SPWindow))
    SP_App.exec_()

def Monitor_Choose(Window):
    Machine = Window.Machine.currentText()
    if Machine == 'timsTOF' or Machine == 'SCIEX':
        Window.Acquisition.setEnabled(False)
        Window.Show_Acq.setEnabled(False)
        Window.Acquisition_File.setEnabled(True)
        Window.Show_Acq_File.setEnabled(True)
        if Machine == 'timsTOF':
            Window.LogFile.setText('CompassHyStarErrorLogbook.log')
            Window.Error_Info.setText('E:')
            Window.Show_Acq_File.setPlaceholderText('C:\BDalSystemData\HyStar\LogFiles\CompassHyStarErrorLogbook.log')
        if Machine == 'SCIEX':
            Window.LogFile.setText('Developer_Error.log')
            Window.Error_Info.setText('[ERROR]')
            Window.Show_Acq_File.setPlaceholderText('C:\ProgramData\SCIEX\Logs\SciexOS\Developer_Error.log')
    elif Machine == 'E480' or Machine == 'Eclipse':
        Window.Acquisition_File.setEnabled(False)
        Window.Show_Acq_File.setEnabled(False)
        Window.Acquisition.setEnabled(True)
        Window.Show_Acq.setEnabled(True)
        if Machine == 'E480':
            Window.LogFile.setText('^MS-Log-*')
            Window.Error_Info.setText('[Type=error]')
        if Machine == 'Eclipse':
            Window.LogFile.setText('^Firmware-*')
            Window.Error_Info.setText('{level}=ERROR')
        Window.Show_Acq.setPlaceholderText('C:\ProgramData\Thermo\Exploris\Log')

def Single_Monitor():
    global MonitorWindow, Dic_Computer
    Mon_App = QApplication(sys.argv)
    MonMainWindow = QWidget()
    MonitorWindow = Monitor.Ui_Form()
    MonitorWindow.setupUi(MonMainWindow)
    MonMainWindow.show()
    Name_List = GetName_Info()
    MonitorWindow.comboBox.addItems(Name_List)
    MonitorWindow.Port.setText('11111')
    MonitorWindow.Machine.currentIndexChanged.connect(partial(Monitor_Choose,MonitorWindow))
    MonitorWindow.Acquisition_File.clicked.connect(partial(ChooseParam,'Acq',MonitorWindow))
    MonitorWindow.Acquisition.clicked.connect(partial(ChoosePath,'Acq',MonitorWindow))
    MonitorWindow.Computer.clicked.connect(partial(Run_Single_Page,'PC'))
    MonitorWindow.UpData_Computer.clicked.connect(partial(UpdateIP,'Mon',MonitorWindow))
    MonitorWindow.Run.clicked.connect(partial(UpdateStatus,'Mon',MonitorWindow))
    Mon_App.exec_()

# 自定义IP模块的修改
def GetName_Info():
    Info_List = list()
    for Info in open(IP_Path):
        Info_List.append(Info.strip().split(':')[0])
    return(Info_List)

def Get_Computer_Pairs():
    global Dic_Info
    Dic_Info = {}
    for Info in open(IP_Path):
        Info = Info.strip().split(':')
        Dic_Info[Info[0]] = Info[1]

def UpdateIP(Page,Window):
    global Dic_Computer
    Dic_Computer = {}
    NameList = list()
    if os.path.exists(IP_Path):
        for Info in open(IP_Path):
            NameList.append(Info.strip().split(':')[0])
            Info = Info.strip().split(':')
            Dic_Computer[Info[0]] = Info[1]
    Window.comboBox.clear()
    Window.comboBox.addItems(NameList)

# 弹出子界面，设置电脑参数 按钮触动
def SetComputer_Window():
    global IP_Set, IP_Set_Info, Dic_Computer
    Dic_Computer = {}
    IP_Set_Info = list()
    if os.path.exists(IP_Path):
        for Info in open(IP_Path):
            IP_Set_Info.append(Info.strip())
            Info = Info.strip().split(':')
            Dic_Computer[Info[0]] = Info[1]
    ComSet_App = QApplication(sys.argv)
    Set_Computer = QWidget()
    IP_Set = Computer_Set.Ui_Form()
    IP_Set.setupUi(Set_Computer)
    Set_Computer.show()
    #IP_Set.Input_Info.setText('#?Name:IP')
    ShowNameIP(IP_Set_Info)
    IP_Set.Add.clicked.connect(AddIP)
    IP_Set.Remove.clicked.connect(RemoveIP)
    IP_Set.Run_Write.accepted.connect(ChangeIP)
    IP_Set.Run_Write.rejected.connect(NoChange)
    ComSet_App.exec_()

def ChangeIP():
    global Dic_Computer, IP_Set_Info
    print('Update')
    IP_File = open(IP_Path,'w')
    Dic_Computer = {}
    for Key in IP_Set_Info:
        IP_File.write(str(Key) + '\n')
        Info = Key.split(':')
        Dic_Computer[Info[0]] = Info[1]
    IP_File.close()
    IP_Set.Add.setEnabled(False)
    IP_Set.Remove.setEnabled(False)
    IP_Set.Run_Write.setEnabled(False)

def NoChange():
    IP_Set.Add.setEnabled(False)
    IP_Set.Remove.setEnabled(False)
    IP_Set.Run_Write.setEnabled(False)
    MsgBox = QMessageBox(QMessageBox.Warning,'Tip','Nothing modified ')
    MsgBox.exec_()

def AddIP():
    global IP_Set_Info,Dic_Computer
    Input_Info = list(IP_Set.Input_Info.toPlainText().split('\n'))
    for Value in list(Input_Info):
        Info = Value.split(':')
        if Info[0] in Dic_Computer.keys():
            Old_Info = Info[0] + ':' + Dic_Computer[Info[0]]
            Dic_Computer[Info[0]] = Info[1]
            IP_Set_Info.remove(Old_Info)
        IP_Set_Info.insert(0,Value)
    ShowNameIP(IP_Set_Info)

def RemoveIP():
    global IP_Set_Info
    RowCount = list()
    for item in IP_Set.ShowTable.selectedItems():
        if item.row() not in RowCount:
            RowCount.append(int(item.row()))
    print(RowCount)
    for Row in sorted(RowCount,reverse = True):
        IP_Set_Info.pop(Row)
    ShowNameIP(IP_Set_Info)

def ShowNameIP(IPListInfo):
    IP_Set.ShowTable.setRowCount(len(IPListInfo))
    for Row in range(0,int(len(IPListInfo))):
        Name = IP_Set_Info[Row].split(':')[0]
        IP = IP_Set_Info[Row].split(':')[1]
        #print(str(Name) + '\t' + str(IP))
        IP_Set.ShowTable.setItem(Row,0,QTableWidgetItem(str(Name)))
        IP_Set.ShowTable.setItem(Row,1,QTableWidgetItem(str(IP)))

# 按钮功能设置 IP/选择文件等 考虑主界面与新生成界面
def ChoosePath(Info_Acq,Window):
    Exist_Dir = QFileDialog.getExistingDirectory().replace('/','\\')
    if ' ' in str(Exist_Dir):
        msg_box = QMessageBox(QMessageBox.Warning,'Attention','Please remove spaces in path')
        msg_box.exec_()
    else:
        if Info_Acq == 'Acq':
            Window.Show_Acq.setText(str(Exist_Dir))
        elif Info_Acq == 'Storge':
            MQ_DataStorge = Exist_Dir
            Window.Show_Storge.setText(str(Exist_Dir))

def ChooseParam(Info_Param,Window):
    Param_File,Type = QFileDialog.getOpenFileName()
    Param_File = Param_File.replace('/','\\')
    if ' ' in str(Param_File):
        msg_box = QMessageBox(QMessageBox.Warning,'Attention','Please remove spaces in path')
        msg_box.exec_()
    else:
        if Info_Param == 'Param':
            Window.Show_Param.setText(str(Param_File))
        if Info_Param == 'Acq':
            Window.Show_Acq_File.setText(str(Param_File))
        if Info_Param == 'DaemonExe':
            Window.Show_Daemon.setText(str(Param_File))
# 多进程执行子界面
def Run_Single_Page(Page_Type):
    if Page_Type == 'SP':
        Cal_SP = Process(target = Single_SP)
        Cal_SP.start()
    if Page_Type == 'PD':
        Cal_PD = Process(target = Single_PD)
        Cal_PD.start()
    if Page_Type == 'MQ':
        Cal_MQ = Process(target = Single_MQ)
        Cal_MQ.start()
    if Page_Type == 'PC':
        Cal_PC = Process(target = SetComputer_Window)
        Cal_PC.start()
    if Page_Type == 'Mon':
        Cal_Mon = Process(target = Single_Monitor)
        Cal_Mon.start()

# 多线程执行 Run_Status
def UpdateStatus(Software,Window):
    Window.Run_Status.setText('Monitoring...')
    Window.Run.setEnabled(False)
    Window.Cal = Thread_Server()
    Window.Cal.Window = Window
    if Software == 'PD':
        Window.Cal.Class = 'PD'
    if Software == 'MQ':
        Window.Cal.Class = 'MQ'
    if Software == 'SP':
        Window.Cal.Class = 'SP'
    if Software == 'Mon':
        Window.Cal.Class = 'Mon'
    Window.Cal.start()

# 示例模块
def Example_SP():
    ui.StackPage.setCurrentIndex(1)
    ui.Show_SP_DataStorge.setText('D:\AutoRun\DataStorge')
    ui.Show_Acq_SP.setText(r'Path\Acquisition_Dir')
    ui.Show_RunSP_Param.setText(r'D:\AutoRun\SetParam.txt')
    ui.Run_SP.setEnabled(False)

def Example_MQ():
    ui.StackPage.setCurrentIndex(2)
    ui.Show_Storge_MQ.setText(r'D:\AutoRun\DataStorge')
    ui.Show_Acq_MQ.setText(r'Path\Acquisition_Dir')
    ui.Show_Mqpar_MQ.setText(r'D:\AutoRun\Condition\Example_MQ_mqpar.xml')
    ui.Run_MQ.setEnabled(False)

def Example_PD():
    ui.StackPage.setCurrentIndex(3)
    ui.Show_Acq_PD.setText(r'Path\Acquisition_Dir')
    ui.Show_Param_PD.setText(r'D:\AutoRun\Condition\480-7.param')
    ui.Run_PD.setEnabled(False)

def Show_Message(Info_Param):
    if Info_Param == 'About':
        msg_box = QMessageBox(QMessageBox.Information,'Project','International Academy of Phronesis Medicine (GuangDong)')
        msg_box.exec_()
    if Info_Param == 'Author':
        msg_box = QMessageBox(QMessageBox.Information,'Email','Author: huangcx@XXX.com')
        msg_box.exec_()
    if Info_Param == 'User_Guide':
        msg_box = QMessageBox(QMessageBox.Information,'User Guide','please find the file in Server module')
        msg_box.exec_()


# 主面板设置
if __name__ == '__main__':
    App = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = MultiRunQC_Ui.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    # 预设变量名
    Version, Port_MQ, Port_SP,  = '','',''
    ui.actionHome.triggered.connect(ShowHome)
    ui.actionRunMQ.triggered.connect(partial(Run_Single_Page,'MQ'))
    ui.actionRunSP.triggered.connect(partial(Run_Single_Page,'SP'))
    ui.actionRunPD.triggered.connect(partial(Run_Single_Page,'PD'))
    ui.actionAdd_MQ.triggered.connect(partial(Show_Message,'About'))
    ui.actionAdd_SP.triggered.connect(partial(Show_Message,'User_Guide'))
    ui.actionAdd_PD.triggered.connect(partial(Show_Message,'Author'))
    ui.actionRemote_PC.triggered.connect(partial(Run_Single_Page,'PC'))
    ui.actionInstrument_Monitor.triggered.connect(partial(Run_Single_Page,'Mon'))
    ui.actionExample_MQ.triggered.connect(Example_MQ)
    ui.actionExample_SP.triggered.connect(Example_SP)
    ui.actionExample_PD.triggered.connect(Example_PD)

    # 按钮及菜单栏设置
    ui.SP_Show.clicked.connect(partial(Run_Single_Page,'SP'))
    ui.PD_Show.clicked.connect(partial(Run_Single_Page,'PD'))
    ui.MQ_Show.clicked.connect(partial(Run_Single_Page,'MQ'))

    sys.exit(App.exec_())
