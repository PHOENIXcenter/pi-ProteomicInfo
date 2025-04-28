#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os,sys
from PyQt5.QtWidgets import *
from functools import partial
import subprocess
import UiMain

def FunExist(Path,Param,Name):
    if os.path.exists(Path):
        if Param != 'none':
            subprocess.Popen(Path + ' ' + Param)
        else:
            subprocess.Popen(Path)
    else:
        MsgBox = QMessageBox(QMessageBox.Information, 'Information', 
                            '    "' + str(Name) +  '" module need to be downloaded.' + '\n' +
                            '    After decompression, the files should be placed in: \n"' + os.path.join(os.getcwd(),'Core') + '"' + '\n')
        MsgBox.exec_()

# Script
def Run_Single_Page(Page_Type,Dir):
    if Page_Type == 'SP_Server':
        RunScript = os.path.join(Dir,'Core','RunServer','RunServer.exe')
        FunExist(RunScript,'SP','RunServer')
    if Page_Type == 'PD_Server':
        RunScript = os.path.join(Dir,'Core','RunServer','RunServer.exe')
        FunExist(RunScript,'PD','RunServer')
    if Page_Type == 'MQ_Server':
        try:
            subprocess.run(['mono', '--version'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            mono_installed = True
        except:
            mono_installed = False
        if not mono_installed:
            MsgBox = QMessageBox(QMessageBox.Information, 'Information', 
                                 'Maxquant Service: Software "mono" should add to environment variable' + '\n' + 
                                 '    Download : <a href="https://www.mono-project.com/download/stable/">Mono Download</a>')
            MsgBox.setTextFormat(Qt.RichText) 
            MsgBox.exec_()
        RunScript = os.path.join(Dir,'Core','RunServer','RunServer.exe')
        FunExist(RunScript,'MQ','RunServer')
    if Page_Type == 'Battch_SP':
        RunScript = os.path.join(Dir,'Core','RunCohort','RunCohort.exe')
        FunExist(RunScript,'SP','RunCohort')
    if Page_Type == 'Battch_MQ':
        RunScript = os.path.join(Dir,'Core','RunCohort','RunCohort.exe')
        FunExist(RunScript,'MQ','RunCohort')
    if Page_Type == 'Battch_MS':
        RunScript = os.path.join(Dir,'Core','RunCohort','RunCohort.exe')
        FunExist(RunScript,'MS','RunCohort')
    if Page_Type == 'Battch_Matrix':
        RunScript = os.path.join(Dir,'Core','RunCohort','RunCohort.exe')
        FunExist(RunScript,'Matrix','RunCohort')
    if Page_Type == 'Daily':
        RunScript = os.path.join(Dir,'Core','RunDaily','RunDaily.exe')
        FunExist(RunScript,'none','RunDaily')
    if Page_Type == 'Summary_Result':
        RunScript = os.path.join(Dir,'Core','ResultSummary','ResultSummary.exe')
        FunExist(RunScript,'none','ResultSummary')
    #if Page_Type == 'MSG':
        #RunScript = os.path.join(Dir,'Core','Instrument_Monitor','Monitor_Instrument.exe')
        #subprocess.Popen(RunScript)
    #    msg_box = QMessageBox(QMessageBox.Information,'Attention','Version not Support')
    #    msg_box.exec_()
    if Page_Type == 'Stat':
        RunScript = os.path.join(Dir,'Core','StatCohort','StatCohort.exe')
        FunExist(RunScript,'none','StatCohort')

def Show_Message(Info_Param):
    if Info_Param == 'About':
        msg_box = QMessageBox(QMessageBox.Information,'Project','International Academy of Phronesis Medicine (GuangDong)')
        msg_box.exec_()
    if Info_Param == 'Author':
        msg_box = QMessageBox(QMessageBox.Information,'Email','Author: huangcx@XX.com')
        msg_box.exec_()
    if Info_Param == 'User_Guide':
        msg_box = QMessageBox(QMessageBox.Information,'User Guide','File in ' + os.path.join(os.getcwd(),'Config','User_Guide.pdf'))
        msg_box.exec_()


# 主面板设置
if __name__ == '__main__':
    #print(str(os.getpid()))
    FilePath = os.getcwd()
    if not os.path.exists(FilePath + r'\Log'):
        os.mkdir(FilePath + r'\Log')
    App = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = UiMain.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    # 预设变量
    Server_Software, Port ,Header ,Jianwei, Normalization, Daily_S, Daily_T = '','','','','','',''
    ui.RunServer_SP.clicked.connect(partial(Run_Single_Page,'SP_Server',FilePath))
    ui.RunServer_MQ.clicked.connect(partial(Run_Single_Page,'MQ_Server',FilePath))
    ui.RunServer_PD.clicked.connect(partial(Run_Single_Page,'PD_Server',FilePath))
    ui.RunBE_SP.clicked.connect(partial(Run_Single_Page,'Battch_SP',FilePath))
    ui.RunBE_MQ.clicked.connect(partial(Run_Single_Page,'Battch_MQ',FilePath))
    ui.RunDaily.clicked.connect(partial(Run_Single_Page,'Daily',FilePath))
    ui.actionMQ_Server.triggered.connect(partial(Run_Single_Page,'MQ_Server',FilePath))
    ui.actionSP_Server.triggered.connect(partial(Run_Single_Page,'SP_Server',FilePath))
    ui.actionPD_Server.triggered.connect(partial(Run_Single_Page,'PD_Server',FilePath))
    ui.actionMQ_BE.triggered.connect(partial(Run_Single_Page,'Battch_MQ',FilePath))
    ui.actionSP_BE.triggered.connect(partial(Run_Single_Page,'Battch_SP',FilePath))
    ui.actionDeal_Matrix.triggered.connect(partial(Run_Single_Page,'Battch_Matrix',FilePath))
    ui.actionMS_BE.triggered.connect(partial(Run_Single_Page,'Battch_MS',FilePath))
    ui.actionDaily_monitor.triggered.connect(partial(Run_Single_Page,'Daily',FilePath))
    ui.actionResult_Summary.triggered.connect(partial(Run_Single_Page,'Summary_Result',FilePath))
    ui.actionCohort_Stat.triggered.connect(partial(Run_Single_Page,'Stat',FilePath))
    ui.actionEmailSend.triggered.connect(partial(Run_Single_Page,'MSG',FilePath))
    ui.actionAbout_US.triggered.connect(partial(Show_Message,'About'))
    ui.actionConcat_Author.triggered.connect(partial(Show_Message,'Author'))
    ui.actionUser_Guide.triggered.connect(partial(Show_Message,'User_Guide'))
    sys.exit(App.exec_())
