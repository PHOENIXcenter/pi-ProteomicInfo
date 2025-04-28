from PyQt5.QtWidgets import *
from socket import *
import os
import pandas as pd

# Nammaping文件比对
def Get_Name(FileInfo):
    with open(FileInfo) as f:
        firstline = f.readline().rstrip()
        return(firstline)

# Nammaping文件比对
def CorrectName(RawFile,MappingFile):
    Raw_Name = Get_Name(RawFile)
    Label = 'TRUE'
    for Info in open(MappingFile):
        if Info.startswith('#RawName'):
            continue
        Info = Info.strip().split(',')
        if Info[0] not in Raw_Name:
            Label = 'FALSE'
            break
    return Label

# 校正信息比对
def CheckStatus(Window,Class):
    Judge = 'True'
    if Class == 'MQ_BE':
        File = Window.Show_BE_Input.text()
        NameMapping = Window.Show_BE_Mapping.text().replace('/','\\')
        if str(Window.checkBox.isChecked()) == 'True':
            Judge = CorrectName(File + r'\proteinGroups.txt',NameMapping)
    if Class == 'MS_BE':
        File = Window.Show_BE_Input.text()
        NameMapping = Window.Show_BE_Mapping.text().replace('/','\\')
        if str(Window.checkBox.isChecked()) == 'True':
            Judge = CorrectName(File + r'\combined_protein.tsv',NameMapping)
    if Class == 'SP_BE':
        File = Window.Show_BE_Input.text()
        NameMapping = Window.Show_BE_Mapping.text().replace('/','\\')
        if str(Window.checkBox.isChecked()) == 'True':
            Judge = CorrectName(File,NameMapping)
            #print(Judge)
    if Judge == 'FALSE':
        Window.checkBox.setChecked(False)
        Window.Run_BE.setEnabled(False)
        msg_box = QMessageBox(QMessageBox.Warning,'Error','File of Name_Mapping is wrong')
        msg_box.exec_()
    Window.Run_BE.setEnabled(True)

# 文件夹选择
def ChoosePath(Window,Info_Acq):
    Exist_Dir = QFileDialog.getExistingDirectory().replace('/','\\')
    if Info_Acq == 'Received':
        Window.Show_Received.setText(str(Exist_Dir))
    if Info_Acq == 'Output':
        Window.OutputDir.setText(str(Exist_Dir))
    if Info_Acq == 'Input':
        Window.Show_BE_Input.setText(str(Exist_Dir))
    if Info_Acq == 'Mapping':
        Window.Show_BE_Mapping.setText(str(Exist_Dir))
    if Info_Acq == 'Battch_Output':
        Window.Show_BE_Output.setText(str(Exist_Dir))
    if Info_Acq == 'Monitor_Dir':
        Window.Show_Monitor.setText(str(Exist_Dir))
    if Info_Acq == 'Daily_Output':
        Window.Show_Output.setText(str(Exist_Dir))

# 文件选择
def ChooseParam(Window,Info_Param):
    Param_File,Type = QFileDialog.getOpenFileName()
    Param_File = Param_File.replace('/','\\')
    if ' ' in str(Param_File):
        msg_box = QMessageBox(QMessageBox.Warning,'Error','Please remove spaces in path')
        msg_box.exec_()
    if Info_Param == 'Exe':
        Window.Show_Exe.setText(str(Param_File))
    if Info_Param == 'Fasta':
        Window.Show_Fasta.setText(str(Param_File))
    if Info_Param == 'WorkFlow':
        Window.Show_WorkFlow.setText(str(Param_File))
    if Info_Param == 'Param':
        Window.Show_Param.setText(str(Param_File))
    if Info_Param == 'Library':
        Window.Show_Library.setText(str(Param_File))
    if Info_Param == 'RawFile':
        Window.Show_RawFile.setText(str(Param_File))
    if Info_Param == 'Input':
        Window.Show_BE_Input.setText(str(Param_File))
        try:
            File = Param_File
            Deal_Data = ''
            if File.endswith('.xls'):
                Deal_Data = pd.read_table(File,sep = '\t',index_col = 0,encoding = 'gbk')
            elif File.endswith('.txt'):
                Deal_Data = pd.read_table(File,sep = '\t',index_col = 0,encoding = 'gbk')
            elif File.endswith('.tsv'):
                Deal_Data = pd.read_table(File,sep = '\t',index_col = 0,encoding = 'gbk')
            elif File.endswith('.xlsx'):
                Deal_Data = pd.read_excel(File,index_col = 0)
            elif File.endswith('.csv'):
                Deal_Data = pd.read_table(File,sep = ',',index_col = 0,encoding = 'gbk')
            else:
                Window.Show_BE_Input.setText('')
                msg_box = QMessageBox(QMessageBox.Warning,'Error','The Format of File is not Supported')
                msg_box.exec_()
            del(Deal_Data)
        except:
            Window.Show_BE_Input.setText('')
            msg_box = QMessageBox(QMessageBox.Warning,'Warning','Something wrong with The Format of File')
            msg_box.exec_()
        
    if Info_Param == 'Mapping':
        Window.Show_BE_Mapping.setText(str(Param_File))
        if not Param_File.endswith('.csv'):
            Window.Show_BE_Mapping.setText('')
            msg_box = QMessageBox(QMessageBox.Warning,'Warning','The Format of File Should be *.CSV')
            msg_box.exec_()

