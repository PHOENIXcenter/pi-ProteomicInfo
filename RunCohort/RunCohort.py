#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os,sys
from PyQt5.QtWidgets import *
from functools import partial
import Ui_SP_BE_monitor,Ui_MQ_BE_monitor,Ui_MS_BE_monitor,Ui_Martix_BE
from Function_Tool import *
import DataMonitor

# Run_Server主函数 开启服务
def RunBE(Window,Type):
    #global Header ,Jianwei, Normalization, Impute
    GetClickRadio(Window)
    Output_Dir = Window.Show_BE_Output.text().replace('/','\\')
    Work_Dir = Window.Show_BE_Input.text().replace('/','\\')
    NameMapping_File = Window.Show_BE_Mapping.text().replace('/','\\')
    ProbabilityMin = 0.99
    C_Site = 'True'
    Header = 'Intensity'
    if Type == 'Matrix':
        Unique_Pep_Nu = 0
    else:
        print(Type)
        Unique_Pep_Nu = Window.Unique_Pep_Nu.text()
        if Type == 'MQ':
            if Window.Data_Intensity.isChecked():
                Header = 'Intensity'
            elif Window.Data_iBAQ.isChecked():
                Header = 'iBAQ'
            elif Window.Data_LFQ.isChecked():
                Header = 'LFQ intensity'
            C_Site = str(Window.Box_Site.isChecked())
        if Type == 'MS':
            if Window.Data_Intensity.isChecked():
                Header = 'Intensity'
            elif Window.Data_LFQ.isChecked():
                Header = 'LFQ intensity'
            ProbabilityMin = Window.ProbabilityMin.text()
    
    # 过滤条件
    if Window.Both_Filter.isChecked():
        Filter_Nu = Window.Sample_Nu.text()
        SubGroup_Percent = Window.SubGroup_Percent.text()
    elif Window.Only_SubGroup.isChecked():
        Filter_Nu = 0
        SubGroup_Percent = Window.SubGroup_Percent.text()
    elif Window.Only_Sample_Num.isChecked():
        Filter_Nu = Window.Sample_Nu.text()
        SubGroup_Percent = 0
    
    ParamFile = open(Output_Dir + r'\ParamFile.txt','w')
    ParamFile.write('Directory of RawFile: ' + str(Work_Dir) + '\n')
    ParamFile.write('Directory of Output: ' + str(Output_Dir) + '\n')
    ParamFile.write('Directory of the renamed file: ' + str(NameMapping_File) + '\n')
    ParamFile.write('At least N samples have identification results: ' + str(Filter_Nu) + '\n')
    ParamFile.write('Min identified Percent in One SubGroup: ' + str(SubGroup_Percent) + '\n')
    if Type == 'MQ':
        ParamFile.write('Dealing Data: ' + str(Header) + '\n')
        if C_Site == 'True':
            ParamFile.write('Proteingroups labeled by "Only identified by site"/"Potential contaminant"/"Reverse" will be removed ' + '\n')
        else:
            ParamFile.write('Proteingroups labeled by "Potential contaminant"/"Reverse" will be removed ' + '\n')
    ParamFile.write('Params for Dealing Data : Normalization-' + str(Normalization) + '\n' + 'Dim_Redution-' + str(Jianwei) + '\n' + 'Fill_NAs-' + str(Impute) + '\n')
    ParamFile.write('Probability(Min): ' + str(ProbabilityMin) + '\n' + 'Unique Peptides Number: ' + str(Unique_Pep_Nu) + '\n')
    ParamFile.close()
    #print(str(Work_Dir) + ' ' + str(NameMapping_File) + ' ' + str(Output_Dir) + ' ' + str(C_Site) + ' ' + str(Header) + ' ' + str(Jianwei) + ' ' + str(Normalization) + ' ' + str(ProbabilityMin) )
    
    try:
        print('DO')
        DataMonitor.RunMonitor(Type,Work_Dir,Output_Dir,Filter_Nu,Normalization,Impute,Jianwei,NameMapping_File,Header,C_Site,Unique_Pep_Nu,ProbabilityMin,SubGroup_Percent)
        msg_box = QMessageBox(QMessageBox.Information,'Status','Job is Done')
        msg_box.exec_()
        Window.Run_BE.setEnabled(False)
    except Exception as e:
        LogError = open(Output_Dir + r'\Error_Log_Record.txt','w')
        LogError.write('-----------------------------------------------------------------------------------------' + '\n')
        LogError.write(str(e))
        LogError.write('\n')
        LogError.write('-----------------------------------------------------------------------------------------' + '\n')
        LogError.close()
        msg_box = QMessageBox(QMessageBox.Information,'Error',Output_Dir + r'\Error_Log_Record.txt' )
        msg_box.exec_()

def GetClickRadio(Window):
    global Header ,Jianwei, Normalization, Impute
    if Window.Nor_Median.isChecked():
        Normalization = 'Median'
    if Window.Nor_Mean.isChecked():
        Normalization = 'Mean'
    if Window.Dim_PCA.isChecked():
        Jianwei = 'PCA'
    if Window.Dim_T_SNE.isChecked():
        Jianwei = 'T-SNE'
    if Window.Dim_UMAP.isChecked():
        Jianwei = 'UMAP'
    if Window.Fill_KNN.isChecked():
        Impute = 'KNN'
    if Window.Fill_Min.isChecked():
        Impute = 'Minimum'
    if Window.Fill_Quantile.isChecked():
        Impute = 'Quantile'
    if Window.Nor_Quantile.isChecked():
        Normalization = 'Quantile'

def ClickRadio(Window,Info_Param):
    if Info_Param == 'Nor_Quantile':
        Normalization = 'Quantile'
        Window.Fill_Quantile.setChecked(True)
        Window.Fill_KNN.setEnabled(False)
        Window.Fill_Min.setEnabled(False)
    else:
        Window.Fill_KNN.setEnabled(True)
        Window.Fill_Min.setEnabled(True)

# 主面板设置
Server = sys.argv[1]
Header = ''
if Server == 'Matrix':
    QM_BE_App = QApplication(sys.argv)
    QM_BE_MainWindow = QWidget()
    QM_BE_Window = Ui_Martix_BE.Ui_Form()
    QM_BE_Window.setupUi(QM_BE_MainWindow)
    QM_BE_MainWindow.show()
    # 默认选项
    QM_BE_Window.Sample_Nu.setText('1')
    QM_BE_Window.Nor_Median.setChecked(True)
    QM_BE_Window.Fill_KNN.setChecked(True)
    QM_BE_Window.Dim_PCA.setChecked(True)
    QM_BE_Window.Run_BE.setEnabled(False)
    QM_BE_Window.Both_Filter.setChecked(True)
    QM_BE_Window.SubGroup_Percent.setText('0.7')

    QM_BE_Window.Nor_Quantile.clicked.connect(partial(ClickRadio,QM_BE_Window,'Nor_Quantile'))
    QM_BE_Window.Nor_Median.clicked.connect(partial(ClickRadio,QM_BE_Window,'Nor_Median'))
    QM_BE_Window.Nor_Mean.clicked.connect(partial(ClickRadio,QM_BE_Window,'Nor_Mean'))
    
    QM_BE_Window.Get_BE_Input.clicked.connect(partial(ChooseParam,QM_BE_Window,'Input'))
    QM_BE_Window.Get_BE_Mapping.clicked.connect(partial(ChooseParam,QM_BE_Window,'Mapping'))
    QM_BE_Window.Get_BE_Output.clicked.connect(partial(ChoosePath,QM_BE_Window,'Battch_Output'))
    QM_BE_Window.checkBox.stateChanged.connect(partial(CheckStatus,QM_BE_Window,'QM_BE'))
    QM_BE_Window.Run_BE.clicked.connect(partial(RunBE,QM_BE_Window,'Matrix'))
    QM_BE_App.exec_()

if Server == 'SP':
    SP_BE_App = QApplication(sys.argv)
    SP_BE_MainWindow = QWidget()
    SP_BE_Window = Ui_SP_BE_monitor.Ui_Form()
    SP_BE_Window.setupUi(SP_BE_MainWindow)
    SP_BE_MainWindow.show()
    # 默认选项
    SP_BE_Window.Sample_Nu.setText('1')
    SP_BE_Window.Unique_Pep_Nu.setText('1')
    SP_BE_Window.Nor_Median.setChecked(True)
    SP_BE_Window.Fill_KNN.setChecked(True)
    SP_BE_Window.Dim_PCA.setChecked(True)
    SP_BE_Window.Run_BE.setEnabled(False)
    SP_BE_Window.Both_Filter.setChecked(True)
    SP_BE_Window.SubGroup_Percent.setText('0.7')

    SP_BE_Window.Nor_Quantile.clicked.connect(partial(ClickRadio,SP_BE_Window,'Nor_Quantile'))
    SP_BE_Window.Nor_Median.clicked.connect(partial(ClickRadio,SP_BE_Window,'Nor_Median'))
    SP_BE_Window.Nor_Mean.clicked.connect(partial(ClickRadio,SP_BE_Window,'Nor_Mean'))
    
    SP_BE_Window.Get_BE_Input.clicked.connect(partial(ChooseParam,SP_BE_Window,'Input'))
    SP_BE_Window.Get_BE_Mapping.clicked.connect(partial(ChooseParam,SP_BE_Window,'Mapping'))
    SP_BE_Window.Get_BE_Output.clicked.connect(partial(ChoosePath,SP_BE_Window,'Battch_Output'))
    SP_BE_Window.checkBox.stateChanged.connect(partial(CheckStatus,SP_BE_Window,'SP_BE'))
    SP_BE_Window.Run_BE.clicked.connect(partial(RunBE,SP_BE_Window,'SP'))
    SP_BE_App.exec_()

if Server == 'MQ':
    MQ_BE_App = QApplication(sys.argv)
    MQ_BE_MainWindow = QWidget()
    MQ_BE_Window = Ui_MQ_BE_monitor.Ui_Form()
    MQ_BE_Window.setupUi(MQ_BE_MainWindow)
    MQ_BE_MainWindow.show()
    # 默认选项
    MQ_BE_Window.Box_Reverse.setChecked(True)
    MQ_BE_Window.Box_Contaminant.setChecked(True)
    MQ_BE_Window.Box_Site.setChecked(True)
    MQ_BE_Window.Sample_Nu.setText('1')
    MQ_BE_Window.Unique_Pep_Nu.setText('1')
    MQ_BE_Window.Data_Intensity.setChecked(True)
    MQ_BE_Window.Nor_Median.setChecked(True)
    MQ_BE_Window.Fill_KNN.setChecked(True)
    MQ_BE_Window.Dim_PCA.setChecked(True)
    MQ_BE_Window.Run_BE.setEnabled(False)
    MQ_BE_Window.Both_Filter.setChecked(True)
    MQ_BE_Window.SubGroup_Percent.setText('0.7')

    MQ_BE_Window.Nor_Quantile.clicked.connect(partial(ClickRadio,MQ_BE_Window,'Nor_Quantile'))
    MQ_BE_Window.Nor_Median.clicked.connect(partial(ClickRadio,MQ_BE_Window,'Nor_Median'))
    MQ_BE_Window.Nor_Mean.clicked.connect(partial(ClickRadio,MQ_BE_Window,'Nor_Mean'))
    MQ_BE_Window.Get_BE_Input.clicked.connect(partial(ChoosePath,MQ_BE_Window,'Input'))
    MQ_BE_Window.Get_BE_Mapping.clicked.connect(partial(ChooseParam,MQ_BE_Window,'Mapping'))
    MQ_BE_Window.Get_BE_Output.clicked.connect(partial(ChoosePath,MQ_BE_Window,'Battch_Output'))
    MQ_BE_Window.checkBox.stateChanged.connect(partial(CheckStatus,MQ_BE_Window,'MQ_BE'))
    MQ_BE_Window.Run_BE.clicked.connect(partial(RunBE,MQ_BE_Window,'MQ'))
    MQ_BE_App.exec_()

if Server == 'MS':
    MS_BE_App = QApplication(sys.argv)
    MS_BE_MainWindow = QWidget()
    MS_BE_Window = Ui_MS_BE_monitor.Ui_Form()
    MS_BE_Window.setupUi(MS_BE_MainWindow)
    MS_BE_MainWindow.show()
    # 默认选项
    MS_BE_Window.Sample_Nu.setText('1')
    MS_BE_Window.Unique_Pep_Nu.setText('1')
    MS_BE_Window.ProbabilityMin.setText('0.99')
    MS_BE_Window.Data_Intensity.setChecked(True)
    MS_BE_Window.Nor_Median.setChecked(True)
    MS_BE_Window.Fill_KNN.setChecked(True)
    MS_BE_Window.Dim_PCA.setChecked(True)
    MS_BE_Window.Run_BE.setEnabled(False)
    MS_BE_Window.Both_Filter.setChecked(True)
    MS_BE_Window.SubGroup_Percent.setText('0.7')

    MS_BE_Window.Nor_Quantile.clicked.connect(partial(ClickRadio,MS_BE_Window,'Nor_Quantile'))
    MS_BE_Window.Nor_Median.clicked.connect(partial(ClickRadio,MS_BE_Window,'Nor_Median'))
    MS_BE_Window.Nor_Mean.clicked.connect(partial(ClickRadio,MS_BE_Window,'Nor_Mean'))
    MS_BE_Window.Get_BE_Input.clicked.connect(partial(ChoosePath,MS_BE_Window,'Input'))
    MS_BE_Window.Get_BE_Mapping.clicked.connect(partial(ChooseParam,MS_BE_Window,'Mapping'))
    MS_BE_Window.Get_BE_Output.clicked.connect(partial(ChoosePath,MS_BE_Window,'Battch_Output'))
    MS_BE_Window.checkBox.stateChanged.connect(partial(CheckStatus,MS_BE_Window,'MS_BE'))
    MS_BE_Window.Run_BE.clicked.connect(partial(RunBE,MS_BE_Window,'MS'))
    MS_BE_App.exec_()