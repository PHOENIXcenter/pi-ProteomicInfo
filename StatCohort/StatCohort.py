#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os,sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread
from functools import partial
import UiCohort
#import Get_Cohort
import subprocess

global Path
Path = os.getcwd()

def RunStat(Window,Path):
    Output_Result = Window.Show_Output.text().replace('/','\\')
    try:
        if Window.S_MQ.isChecked():
            StatFile = Window.Show_Dir.text().replace('/','\\')
            #Get_Cohort.MQ_Extract(StatFile,Output_Result)
            subprocess.Popen(Path + r'\Core\RunStat\RunStat.exe ' + StatFile + ' ' + Output_Result + ' TRUE MQ FALSE None')
        if Window.S_SP.isChecked():
            StatFile = Window.Show_File.text().replace('/','\\')
            os.system(Path + r'\Core\RunStat\RunStat.exe ' + StatFile + ' ' + Output_Result + ' TRUE SP FALSE None')
        if Window.S_MS.isChecked():
            StatFile = Window.Show_Dir.text().replace('/','\\')
            #Get_Cohort.MS_Extract(StatFile,Output_Result)
            subprocess.Popen(Path + r'\Core\RunStat\RunStat.exe ' + StatFile + ' ' + Output_Result + ' FALSE MS FALSE None')
        msg_box = QMessageBox(QMessageBox.Information,'Success','Job Done' )
        msg_box.exec_()
    except Exception as e:
        msg_box = QMessageBox(QMessageBox.Information,'Error',str(e) )
        msg_box.exec_()

# 文件夹选择
def ChoosePath(Window,Info_Acq):
    Exist_Dir = QFileDialog.getExistingDirectory()
    if ' ' in str(Exist_Dir):
        Exist_Dir = '"' + str(Exist_Dir) + '"'
    if Info_Acq == 'Monitor_Dir':
        Window.Show_Dir.setText(str(Exist_Dir))
    if Info_Acq == 'Stat_Output':
        Window.Show_Output.setText(str(Exist_Dir))

def ChooseParam(Window,Info_Param):
    Param_File,Type = QFileDialog.getOpenFileName()
    Param_File = Param_File.replace('/','\\')
    if Info_Param == 'Monitor_File':
        if ' ' in str(Param_File):
            Param_File = '"' + str(Param_File) + '"'
        Window.Show_File.setText(str(Param_File))


# 主面板设置
Stat_App = QApplication(sys.argv)
Stat_MainWindow = QWidget()
Stat_Window = UiCohort.Ui_Form()
Stat_Window.setupUi(Stat_MainWindow)
Stat_MainWindow.show()

Stat_Window.Output.clicked.connect(partial(ChoosePath,Stat_Window,'Stat_Output'))
Stat_Window.Monitor_Dir.clicked.connect(partial(ChoosePath,Stat_Window,'Monitor_Dir'))
Stat_Window.Monitor_File.clicked.connect(partial(ChooseParam,Stat_Window,'Monitor_File'))

Stat_Window.S_MQ.setChecked(True)
Stat_Window.Show_File.setHidden(True)
Stat_Window.Monitor_File.setHidden(True)

Stat_Window.Run_monitor.clicked.connect(partial(RunStat,Stat_Window,Path))
Stat_App.exec_()
