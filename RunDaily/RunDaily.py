#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os,sys
from PyQt5.QtWidgets import *
from functools import partial
from PyQt5.QtCore import QThread
import Reference_Result,UI_Report_Abnormal
from multiprocessing import Process
import pandas as pd
import sqlite3
from Function_Tool import *
import CronabTime_Abnormal

Path = os.getcwd()
ModelFile = os.path.join(Path,'Config','Data_Characteristics.txt')
ConnSql = sqlite3.connect(Path + r'\Param.db')
ParamSql = ConnSql.cursor()
#ModelFile_Temp = os.path.join(Path,'Config','Data_Characteristics_Temp.txt')
# 文件夹选择
def ChoosePath(Window,Info_Acq):
    Exist_Dir = QFileDialog.getExistingDirectory()
    if ' ' in str(Exist_Dir):
        msg_box = QMessageBox(QMessageBox.Information,'Error','Please remove spaces in path')
        msg_box.exec_()
    else:
        if Info_Acq == 'Monitor_Dir':
            Window.Show_Monitor.setText(str(Exist_Dir))
        if Info_Acq == 'Daily_Output':
            Window.Show_Output.setText(str(Exist_Dir))
        if Info_Acq == 'Choose_Dir':
            Window.Dir_Txt.setText(str(Exist_Dir))

# Model-参考数据记录
def Record_File(Window):
    Label = Window.ShowLabel.text()
    List_Label = Initial_Model()
    if Label != '':
        Add = 'True'
        if Label in List_Label:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setInformativeText("The operation will replace the original result")
            msg_box.setStandardButtons(QMessageBox.Yes|QMessageBox.No);
            QQ = msg_box.exec_()
            # 确认是否需要调整记录
            if QQ == QMessageBox.No:
                #print('DO Nothing')
                Add = 'False'
            else:
                List_Label.remove(Label)
        List_Label.insert(0,str(Label))
        if Add == 'True':
            Dir = Window.Dir_Txt.text()
            #print(str(Dir))
            # 数据汇总及监查
            Regular = Window.ShowRegular.text().split(';')
            Output = open(Path + r'\Config\\' + Label + '.txt','w')
            # 获取title表头信息 break 减少读取的内容
            for File in os.listdir(Dir):
                if Regular != '':
                    TT = [i for i in Regular if i in str(File)]
                    if Regular == TT:
                        with open(Dir + r'\\' + File,'r',encoding = 'utf-8') as f:
                            Lines = f.readline()
                            Output.write(Lines)
                            break
                else:
                    with open(Dir + r'\\' + File,'r',encoding = 'utf-8') as f:
                        Lines = f.readline()
                        Output.write(Lines)
                        break
            # 汇总Reference文件信息
            for File in os.listdir(Dir):
                if Regular != '':
                    TT = [i for i in Regular if i in str(File)]
                    if Regular == TT:
                        for f in open(Dir + r'\\' + File):
                            if f.split('\t')[0] == 'Raw file' or f.split('\t')[0] == 'Experiment' or 'WARNING' in str(f.split('\t')[0]) or 'ERROR' in str(f.split('\t')[0]):
                                continue
                            Output.write(f)
                else:
                    for f in open(Dir + r'\\' + File):
                        if f.split('\t')[0] == 'Raw file' or f.split('\t')[0] == 'Experiment' or 'WARNING' in str(f.split('\t')[0]) or 'ERROR' in str(f.split('\t')[0]):
                            continue
                        Output.write(f)
            Output.close()
            Data = pd.read_table(Path + r'\Config\\' + Label + '.txt',sep = '\t')
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
            Sql_Add(Label,Min_Max)
            Sql_Add(Label + '@Mean',Mean_Mean)
            Write_Model(List_Label)
            #print(List_Label)
            ## 以汇总文件去判断后续结果
            Window.Record_File.setEnabled(False)
            msg_box = QMessageBox(QMessageBox.Information,'Success','Reference files added')
            msg_box.exec_()
    else:
        msg_box = QMessageBox(QMessageBox.Information,'Attention','Please add the label of data characteristic')
        msg_box.exec_()

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

# 参数设置-数据库初始
Sql_Inital = '''CREATE TABLE IF NOT EXISTS Reference_Data
           (ID TEXT,
            Min_Protein TEXT,
            Min_Peptide TEXT,
            Min_SumQ TEXT,
            Min_MedQ TEXT,
            Min_RT_Med TEXT,
            Min_PPM_Med TEXT,
            Max_Protein TEXT,
            Max_Peptide TEXT,
            Max_SumQ TEXT,
            Max_MedQ TEXT,
            Max_RT_Med TEXT,
            Max_PPM_Med TEXT);'''
ParamSql.execute(Sql_Inital)
ConnSql.commit()

# Characteristics Model文本初始化 反馈所有模型信息
def Initial_Model():
    Item = []
    if os.path.exists(ModelFile):
        for Info in open(ModelFile):
            Info = Info.strip()
            if Info != '':
                if Info in Item:
                    Item.remove(str(Info))
                Item.append(str(Info))
    if len(Item) == 0:
        Item.append('Please Add Characteristics Model')
    return Item

# 更新模型名称 新添加的内容出现的最顶端
def Update_Model():
    Item = []
    for Info in open(ModelFile):
        Info = Info.strip()
        if Info != '' :
            if Info in Item:
                Item.remove(str(Info))
            Item.append(str(Info))
    if 'Please Add Characteristics Model' in Item:
        Item.remove('Please Add Characteristics Model')
    if len(Item) == 0:
        Item.append(str('Please Add Characteristics Model'))
    Daily_Window.tableWidget.setRowCount(len(Item))
    for Row in range(0,int(len(Item))):
        Name = str(Item[Row])
        Daily_Window.tableWidget.setItem(Row,0,QTableWidgetItem(str(Name)))
    Write_Model(Item)

# Characteristics Model文本写入
def Write_Model(FileList):
    Output = open(ModelFile,'w')
    for Value in FileList:
        Output.write(str(Value) + '\n')
    Output.close()

# Characteristics Model文本特征选择-支持多选
def ShowSelect(Window):
    Label_Value = list()
    ShowLabel = ''
    for item in Window.tableWidget.selectedItems():
        if item.text() not in Label_Value:
            Label_Value.append(item.text())
            if ShowLabel == '':
                ShowLabel = item.text()
            else:
                ShowLabel = ShowLabel + ';' + item.text()
    #print(Label_Value)
    # 用户未选择
    if ShowLabel == '':
        ShowLabel = Window.Model.text()
    # 去除选中状态
    Window.tableWidget.clearSelection()
    Window.Model.setText(ShowLabel)

# Characteristics Model导入界面
def SetModel_Window():
    ComSet_App = QApplication(sys.argv)
    SetModel = QWidget()
    Model_Set = Reference_Result.Ui_Form()
    Model_Set.setupUi(SetModel)
    SetModel.show()
    Model_Set.Record_File.setEnabled(True)
    Model_Set.Choose_Dir.clicked.connect(partial(ChoosePath,Model_Set,'Choose_Dir'))
    Model_Set.Record_File.clicked.connect(partial(Record_File,Model_Set))
    ComSet_App.exec_()

# 多进程执行子界面
def Run_Single_Page(Page_Type):
    if Page_Type == 'Add_Record':
        Cal_Add_Record = Process(target = SetModel_Window)
        Cal_Add_Record.start()

# 监控主体程序
class Thread_Daily(QThread):
    Window = ''
    def __init__(self):
        super(Thread_Daily,self).__init__()
    def run(self):
        Num = self.Window.spinBox.value()
        Monitor_Dir = self.Window.Show_Monitor.text().replace('/','\\')
        Output_Result = self.Window.Show_Output.text().replace('/','\\')
        Characteristics_Info = self.Window.Model.text().split(';')
        if self.Window.IRT.isChecked():
            IRT_Add = 'TRUE'
        else:
            IRT_Add = 'FALSE'
        
        if self.Window.S_MQ.isChecked() or self.Window.S_SP.isChecked() or self.Window.S_PD.isChecked():
            if self.Window.S_MQ.isChecked():
                Daily_S = 'MQ'
            if self.Window.S_SP.isChecked():
                Daily_S = 'SP'
            if self.Window.S_PD.isChecked():
                Daily_S = 'PD'
        else:
            #print('5')
            msg_box = QMessageBox(QMessageBox.Information,'Attention','Please select a Software')
            msg_box.exec_()
        if self.Window.T_Min.isChecked() or self.Window.T_Hour.isChecked() or self.Window.T_Day.isChecked():
            if self.Window.T_Min.isChecked():
                Value = Num
            if self.Window.T_Hour.isChecked():
                Value = Num * 60
            if self.Window.T_Day.isChecked():
                Value = Num * 60 * 24
        else:
            msg_box = QMessageBox(QMessageBox.Information,'Attention','Please select a frequency')
            msg_box.exec_()
        if self.Window.Show_AB.isChecked():
            #print('1')
            CronabTime_Abnormal.Data_Extract(Monitor_Dir,Daily_S,Value,Output_Result,IRT_Add,'Monitoring',Characteristics_Info)
        else:
            CronabTime_Abnormal.Data_Extract(Monitor_Dir,Daily_S,Value,Output_Result,IRT_Add,'Neglect',Characteristics_Info)

def UpdateStatus(Window):
    Window.Run_monitor.setText('Monitoring...')
    Window.Cal = Thread_Daily()  # 创建一个线程
    Window.Cal.Window = Window
    Window.Cal.start()  # 线程启动

def ClickRadio(Window,Info_Class):
    if Info_Class == 'PD':
        Window.IRT.setChecked(False)
        Window.IRT.setEnabled(False)
    else:
        Window.IRT.setEnabled(True)

# 主面板设置
if __name__ == '__main__':
    App = QApplication(sys.argv)
    MainWindow = QWidget()
    Daily_Window = UI_Report_Abnormal.Ui_Form()
    Daily_Window.setupUi(MainWindow)
    MainWindow.show()
    Initial_Item = Initial_Model()
    Daily_Window.tableWidget.setRowCount(len(Initial_Item))
    for Row in range(0,int(len(Initial_Item))):
        Name = str(Initial_Item[Row])
        Daily_Window.tableWidget.setItem(Row,0,QTableWidgetItem(str(Name)))
    Daily_Window.Model.setText(Initial_Item[0])
    Daily_Window.Ignore_AB.setChecked(True)
    Daily_Window.Output.clicked.connect(partial(ChoosePath,Daily_Window,'Daily_Output'))
    Daily_Window.IRT.setChecked(True)
    Daily_Window.S_MQ.setChecked(True)
    Daily_Window.T_Min.setChecked(True)
    Daily_Window.Monitor_Dir.clicked.connect(partial(ChoosePath,Daily_Window,'Monitor_Dir'))
    Daily_Window.spinBox.setValue(30)
    
    Daily_Window.Add_Record.clicked.connect(partial(Run_Single_Page,'Add_Record'))
    Daily_Window.SelectModel.clicked.connect(partial(ShowSelect,Daily_Window))
    Daily_Window.Run_monitor.clicked.connect(partial(UpdateStatus,Daily_Window))
    
    Daily_Window.S_MQ.clicked.connect(partial(ClickRadio,Daily_Window,'MQ'))
    Daily_Window.S_SP.clicked.connect(partial(ClickRadio,Daily_Window,'SP'))
    Daily_Window.S_PD.clicked.connect(partial(ClickRadio,Daily_Window,'PD'))
    Daily_Window.UpDate_Record.clicked.connect(partial(Update_Model))
    
    Daily_Window.tableWidget.setEnabled(False) # type: ignore
    Daily_Window.GetModel.setEnabled(False) # type: ignore
    Daily_Window.Model.setEnabled(False) # type: ignore
    Daily_Window.SelectModel.setEnabled(False) # type: ignore
    Daily_Window.UpDate_Record.setEnabled(False) # type: ignore
    Daily_Window.Add_Record.setEnabled(False) # type: ignore
    sys.exit(App.exec_())



