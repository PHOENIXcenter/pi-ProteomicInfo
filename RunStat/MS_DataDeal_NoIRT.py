import pandas as pd
import sys
import numpy as np
import os
import re
import shutil
import time

def MS_Extract(Param1,Param2):
    WorkDir = Param1
    Output_Dir = Param2
    Name_Label = list()
    for File in os.listdir(WorkDir):
        if File.endswith('fp-manifest'):
            Name_Label.append(File)
    
    NameFile = Name_Label[0]
    if len(Name_Label) > 1:
        for New in Name_Label:
            if New > NameFile:
                NameFile = New
    
    # 读取文件信息
    Summary_Info = pd.read_table(os.path.join(WorkDir,NameFile),sep = '\t',header = None)
    if Summary_Info[2].dropna().shape[0] == 0:
        Exp_List = list(Summary_Info[1].drop_duplicates().dropna())
    else:
        Summary_Info['New'] = Summary_Info[1].astype(str).str.cat(Summary_Info[2].astype(str), sep='_')
        Exp_List = list(Summary_Info['New'].drop_duplicates().dropna())
    
    # 统计蛋白数、谱图数、Intensity信息、统计肽段数
    Dic_Protein = {}
    Dic_Intensity_Sum = {}
    Dic_Intensity_Mean = {}
    Dic_PSM = {}
    Dic_Peptide = {}
    Protein = pd.read_table(os.path.join(WorkDir,'combined_protein.tsv'),sep = '\t')
    Peptide = pd.read_table(os.path.join(WorkDir,'combined_peptide.tsv'),sep = '\t')
    for Name in Exp_List:
        Temp = Protein[['Protein',str(Name) + ' Intensity',str(Name) + ' Spectral Count']]
        Dic_PSM[Name] = Temp.iloc[:,2].sum()
        Temp = Temp[Temp[str(Name) + ' Intensity'] > 0]
        Dic_Intensity_Sum[Name] = round(Temp.iloc[:,1].sum(),2)
        Dic_Intensity_Mean[Name] = round(Temp.iloc[:,1].mean(),2)
        Dic_Protein[Name] = Temp.shape[0]
        Temp = Peptide[['Peptide Sequence',str(Name) + ' Intensity']]
        Temp = Temp[Temp[str(Name) + ' Intensity'] > 0]
        Dic_Peptide[Name] = Temp.shape[0]
    # PPM/峰宽/漏切
    Dic_75PPM = {}
    Dic_50PPM = {}
    Dic_25PPM = {}
    Dic_75RL = {}
    Dic_50RL = {}
    Dic_25RL = {}
    Dic_No_Missed_Cleavages ,Dic_Missed_Cleavage = {},{}
    for Name in Exp_List:
        File = os.path.join(WorkDir,str(Name),str(Name) + '_quant.csv')
        Dic_25PPM[Name],Dic_25RL[Name],Dic_50PPM[Name],Dic_50RL[Name],Dic_75PPM[Name],Dic_75RL[Name] = 'NA','NA','NA','NA','NA','NA'
        if os.path.exists(File):
            Data = pd.read_table(File,sep = ',')
            Data['uncalibrated_ppm'] = Data['uncalibrated_ppm'].astype(float)
            List_stat = Data['uncalibrated_ppm'].describe()
            Percent25 = List_stat[4]
            Percent75 = List_stat[6]
            Gap = float(Percent75) - float(Percent25)
            Min = float(Percent25) - Gap * 1.5
            Max = float(Percent75) + Gap * 1.5
            Temp = Data[(Data['uncalibrated_ppm'] > Min ) & (Data['uncalibrated_ppm'] < Max) ]
            Dic_75PPM[Name] = round(float(Percent75),3)
            Dic_50PPM[Name] = round(float(Temp['uncalibrated_ppm'].median()),3)
            Dic_25PPM[Name] = round(float(Percent25),3)
            RT_Data = Data[['retention_time_begin','retention_time_end']].dropna()
            RT_Data['Retention length'] = RT_Data['retention_time_end'] - RT_Data['retention_time_begin']
            List_stat = RT_Data['Retention length'].describe()
            Percent25 = List_stat[4]
            Percent75 = List_stat[6]
            Gap = float(Percent75) - float(Percent25)
            Min = float(Percent25) - Gap * 1.5
            Max = float(Percent75) + Gap * 1.5
            Temp = RT_Data[(RT_Data['Retention length'] > Min ) & (RT_Data['Retention length'] < Max) ]
            Dic_75RL[Name] = round(float(Percent75),3)
            Dic_50RL[Name] = round(float(Temp['Retention length'].median()),3)
            Dic_25RL[Name] = round(float(Percent25),3)
        File = os.path.join(WorkDir,str(Name),'PSM.tsv')
        PSM_Info = pd.read_table(File,sep = '\t')
        Count_0 = PSM_Info[PSM_Info['Number of Missed Cleavages'] == 0].shape[0]
        Count_1 = PSM_Info[PSM_Info['Number of Missed Cleavages'] == 1].shape[0]
        Count_2 = PSM_Info[PSM_Info['Number of Missed Cleavages'] == 2].shape[0]
        Missed_Cleavage = round(100 - 100 * (Count_1 + Count_2 * 2) / (Count_0 + Count_1 * 2 + Count_2 * 3),2)
        Dic_No_Missed_Cleavages[Name] = round(100 * Count_0 / PSM_Info.shape[0],2)
        Dic_Missed_Cleavage [Name] = Missed_Cleavage
    
    Output = open(Output_Dir + r'\Cohort_MS_Stat_Summary.txt','w')
    Output.write('Experiment' + '\t' + 'ProteinGroups' + '\t' + 'Peptides' + '\t' + 'PSM' + '\t' + 'No_Missed_Cleavages (%)' + '\t' + 'Intensity_Sum' + '\t' + 
    'Intensity_Mean' + '\t' + 'Percent75 of PPM' + '\t' + 'Median of PPM' + '\t' + 'Percent25 of PPM' + '\t' + 
    'Percent75 of RL' + '\t' + 'Median of RL' + '\t' + 'Percent25 of RL' + '\t' + 'Missed_Cleavage (%)' + '\n')
    for Name in Exp_List:
        Output.write(str(Name) + '\t' + str(Dic_Protein[Name]) + '\t' + str(Dic_Peptide[Name]) + '\t' + str(Dic_PSM[Name]) + '\t' 
        + str(Dic_No_Missed_Cleavages[Name]) + '\t' + str(Dic_Intensity_Sum[Name]) +  '\t' + str(Dic_Intensity_Mean[Name]) +  '\t' 
        + str(Dic_75PPM[Name]) + '\t' + str(Dic_50PPM[Name]) + '\t' + str(Dic_25PPM[Name]) + '\t' + str(Dic_75RL[Name]) + '\t' 
        + str(Dic_50RL[Name]) + '\t' + str(Dic_25RL[Name]) + '\t' + str(Dic_Missed_Cleavage[Name]) +'\n')
    
    Output.close()
    
    return(os.path.join(Output_Dir,'Cohort_MS_Stat_Summary.txt'))
