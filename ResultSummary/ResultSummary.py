#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
from PyQt5.QtWidgets import *
from functools import partial
import Ui_Result_Merge
import pandas as pd
from pathlib import Path


# 确保IRT文件是可调整的
IRT_File = os.path.join(os.getcwd(),'Config','CharacteristicPeakIRT.txt')
IRT_Seq = []
if os.path.exists(IRT_File):
    for Seq in open(IRT_File):
        IRT_Seq.append(str(Seq).strip())

if len(IRT_Seq) < 1 or not os.path.exists(IRT_File):
    IRT_Seq = ['LGGNEQVTR', 'GAGSSEPVTGLDAK', 'VEATFGVDESNAK', 'YILAGVENSK','TPVISGGPYEYR', 'TPVITGAPYEYR', 'DGLDAASYYAPVR', 'ADVTPADFSEWSK','GTFIIDPGGVIR', 'GTFIIDPAAVIR', 'LFLQFGAQGSPFLK']


# 配置常量
CONFIG = {
    'MQ': {
        'merge_suffix': '_MQ_Stat_Summary.txt',
        'title': 'Experiment\tNumber of ProteinGroups\tNumber of Peptides\tProtein Quantity (Sum)\tProtein Quantity (Median)\tProtein Quantity (Mean)\tRaw file\tMS\tMS/MS\tMS/MS identified\tMS/MS identified [%]\tPeptide sequences identified\tPercent75 of PPM\tMedian of PPM\tPercent25 of PPM\tRetention_length_Mean (s)\tRetention_length_Median (s)\n'
    },
    'SP': {
        'merge_suffix': '_SP_Stat_Summary.txt',
        'title': 'Raw file\tNumber of ProteinGroups\tNumber of Peptides\tNumber of Precursors\tPeak Capacity\tNumber of MS1 Spectra\tNumber of MS2 Spectra\tRetention_length_Median (FWHM) (s)\tMedian of RT Length (s)\tCycle Time (MS1)\tCycle Time (MS2)\tData Points per Peak (MS1)\tData Points per Peak (MS2)\tProtein Quantity (Sum)\tProtein Quantity (Median)\tProtein Quantity (Mean)\tAverage PPM\tMedian PPM\n'
    },
    'PD': {
        'merge_suffix': '_PD_Stat_Summary.txt',
        'title': 'Raw file\tNumber of ProteinGroups\tNumber of Peptides\tNumber of PSM\tNumber of MSMS\tNo_Missed_Cleavage (%)\tExperiment\tPercent75 of RT Length (s)\tMedian of RT Length (s)\tPercent25 of RT Length (s)\tPercent75 of PPM\tMedian of PPM\tPercent25 of PPM\tProtein Quantity (Sum)\tProtein Quantity (Median)\tProtein Quantity (Mean)\n'
    }
}

def write_irt_files(output_dir, irt_rt, irt_intensity):
    """ 写入 IRT 相关文件 """
    with open(output_dir / 'IRT_RT_Summary.txt', 'w') as rt_file, \
         open(output_dir / 'IRT_Intensity_Summary.txt', 'w') as intensity_file:
        rt_file.write('Raw file\t' + '\t'.join(IRT_Seq) + '\n')
        intensity_file.write('Raw file\t' + '\t'.join(IRT_Seq) + '\n')


def process_file(file_path, output_file):
    """ 处理单个文件 """
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith(('Raw file', 'Experiment')) or 'WARNING' in line or 'ERROR' in line:
                continue
            if line.startswith('#outlier#'):
                break
            output_file.write(line)

def process_irt_summary(file_path, irt_rt_path, irt_intensity_path):
    """ 处理 IRT Summary 文件 """
    IRT_RT = open(irt_rt_path,'a')
    IRT_Intensity = open(irt_intensity_path,'a')
    RT_Info = pd.read_table(file_path,sep = '\t')
    
    IRT_Intensity.write(str(file_path).replace('_IRT_Summary.txt','') + '\t')
    IRT_RT.write(str(file_path).replace('_IRT_Summary.txt','') + '\t')
    for Intensity in RT_Info['Intensity']:
        IRT_Intensity.write(str(Intensity) + '\t')
    IRT_Intensity.write('\n')
    for RT in RT_Info['Retention time (min)']:
        IRT_RT.write(str(RT) + '\t')
    IRT_RT.write('\n')


def WriteFile(File,irt_rt_path,irt_intensity_path,merge_suffix,output_file):
    if File.endswith(merge_suffix):
        #print("Do")
        process_file(File, output_file)
    if File.endswith('_IRT_Summary.txt') and merge_suffix != '_PD_Stat_Summary.txt':
        process_irt_summary(File, irt_rt_path, irt_intensity_path)

def RunMerge(Window):
    monitor_dir = Path(Window.Show_Monitor.text())
    output_dir = Path(Window.Show_Output.text())
    regular = [r.strip() for r in Window.Show_Regular.text().split(';') if r.strip()]
    # 获取预设内容
    merge_suffix = CONFIG.get(Window.Info_Class, {}).get('merge_suffix', '')
    title = CONFIG.get(Window.Info_Class, {}).get('title', '')
    if not merge_suffix or not title:
        QMessageBox(QMessageBox.Warning, 'Error', 'Invalid configuration').exec_()
        return

    # 输出文件
    output_path = os.path.join(output_dir, 'Merge_Summary.txt')
    irt_rt_path = os.path.join(output_dir, 'IRT_RT_Summary.txt') if merge_suffix != '_PD_Stat_Summary.txt' else None
    irt_intensity_path = os.path.join(output_dir, 'IRT_Intensity_Summary.txt') if merge_suffix != '_PD_Stat_Summary.txt' else None

    try:
        with open(output_path, 'w') as output_file:
            output_file.write(title)
        
            if irt_rt_path and irt_intensity_path:
                write_irt_files(output_dir, irt_rt_path, irt_intensity_path)
            for file in os.listdir(monitor_dir):
                if not regular :
                    WriteFile(os.path.join(monitor_dir,file),irt_rt_path,irt_intensity_path,merge_suffix,output_file)
                else:
                    # TT 确保所有条件都符合
                    TT = [i for i in regular if i in str(file)]
                    if TT == regular:
                        WriteFile(os.path.join(monitor_dir,file),irt_rt_path,irt_intensity_path,merge_suffix,output_file)
    
        QMessageBox(QMessageBox.Information, 'Status', 'Job is Done').exec_()
    except Exception as e:
        QMessageBox(QMessageBox.Critical, 'Error', f'Failed to process files: {e}').exec_()


def ClickRadio(Info_Param, Info_Class, Window):
    Window.Info_Class = Info_Class

def ChoosePath(Window, Info_Acq):
    exist_dir = QFileDialog.getExistingDirectory()
    if ' ' in str(exist_dir):
        QMessageBox(QMessageBox.Warning, 'Error', 'Please remove spaces in path').exec_()
    else:
        if Info_Acq == 'Monitor_Dir':
            Window.Show_Monitor.setText(str(exist_dir))
        elif Info_Acq == 'Merge_Output':
            Window.Show_Output.setText(str(exist_dir))

# 主面板设置
if __name__ == '__main__':
    Merge_App = QApplication(sys.argv)
    Merge_MainWindow = QWidget()
    Merge_Window = Ui_Result_Merge.Ui_Form()
    Merge_Window.setupUi(Merge_MainWindow)
    Merge_MainWindow.show()
    
    Merge_Window.S_MQ.clicked.connect(partial(ClickRadio, 'Daily', 'MQ', Merge_Window))
    Merge_Window.S_SP.clicked.connect(partial(ClickRadio, 'Daily', 'SP', Merge_Window))
    Merge_Window.S_PD.clicked.connect(partial(ClickRadio, 'Daily', 'PD', Merge_Window))
    Merge_Window.Output.clicked.connect(partial(ChoosePath, Merge_Window, 'Merge_Output'))
    Merge_Window.Monitor_Dir.clicked.connect(partial(ChoosePath, Merge_Window, 'Monitor_Dir'))
    Merge_Window.Run_monitor.clicked.connect(partial(RunMerge, Merge_Window))

    Merge_App.exec_()