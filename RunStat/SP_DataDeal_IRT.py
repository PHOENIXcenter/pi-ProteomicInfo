import pandas as pd
import sys
import numpy as np
from datetime import datetime
import os

global Dic_Precursors,Dic_MS_CycleTime,Dic_MS2_CycleTime,Dic_MS_DataPoint,Dic_MS2_DataPoint,Dic_Median_PeakWidth,IRT_Seq
Dic_ProteinGroups = {}
Dic_Peptides = {}
Dic_Precursors = {}
Dic_MS_CycleTime = {}
Dic_MS2_CycleTime = {}
Dic_MS_DataPoint = {}
Dic_MS2_DataPoint = {}
Dic_Median_PeakWidth = {}
Dic_Median_FWHM = {}
Dic_Peak_Capacity = {}
Dic_Number_MS1_Spectra = {}
Dic_Number_MS2_Spectra = {}
Dic_Protein_SumQuantity = {}
Dic_Protein_MedianQuantity = {}
Dic_Protein_MeanQuantity = {}
Dic_PPM_MS1 = {}
Dic_PPM_MS2 = {}
Dic_Median_PPM = {}
Dic_Average_PPM = {}
Dic_No_Cleavages = {}
Dic_Filter_Peptides = {}
Dic_Filter_ProteinGroups = {}
Dic_Missed_Cleavage = {}

IRT_File = os.path.join(os.getcwd(),'Config','CharacteristicPeakIRT.txt')
IRT_Seq = list()

if os.path.exists(IRT_File):
    for Seq in open(IRT_File):
        if str(Seq) not in IRT_Seq and str(Seq) != '':
            IRT_Seq.append(str(Seq).strip())

if len(IRT_Seq) < 1 or not os.path.exists(IRT_File):
    IRT_Seq = ['LGGNEQVTR', 'GAGSSEPVTGLDAK', 'VEATFGVDESNAK', 'YILAGVENSK','TPVISGGPYEYR', 'TPVITGAPYEYR', 'DGLDAASYYAPVR', 'ADVTPADFSEWSK','GTFIIDPGGVIR', 'GTFIIDPAAVIR', 'LFLQFGAQGSPFLK']


def Judge_Error(SubData,Type):
    TT = list(SubData[Type].drop_duplicates())
    Nu = len(TT)
    if Nu > 1:
        return('Error')
    else:
        if Type == 'R.Median Peak Width(EXT)' or Type == 'R.Median FWHM [min](EXT)' or Type == 'R.Peak Capacity(EXT)':
            Value = round(TT[0],3)
        else:
            Value = TT[0]
        return(Value)

# Input 报告存放位置
def SP_Extract(Parm1,Parm2,IRT_Add,QC):
    TargetDir = Parm1
    Output_Dir = Parm2
    #  Output 报告输出位置
    if QC == 'TRUE':
        Label = [Label for Label in os.listdir(TargetDir) if Label.endswith('Report_huiyan (Normal).xls')]
        if not Label:
            Label = [Label for Label in os.listdir(TargetDir) if Label.endswith('Report_huiyan (Normal).tsv')]
        File = os.path.join(TargetDir,Label[0])
        Label = File.split('\\')[-2].split('.')[0]
        os.makedirs(Output_Dir,exist_ok=True)
    else:
        File = TargetDir
        Label = 'Cohort'
    
    Data = pd.read_table(File,sep = '\t',encoding = 'gbk')
    Exp_List = list(Data['R.FileName'].drop_duplicates())
    if IRT_Add == 'TRUE':
        #print('DoDone')
        Output_IRT = open(Output_Dir + r'\\' + str(Label) + r'_IRT_Summary.txt','w')
        Output_IRT.write('Raw file' + '\t' + 'Sequence' + '\t' + 'Intensity' + '\t' + 'Retention time (min)' + '\n') 
    for Name in Exp_List:
        Temp = Data[Data['R.FileName'] == Name]
        Dic_Peptides[Name] = len(Temp['PEP.GroupingKey'].drop_duplicates())
        Zero_C = Temp[Temp['PEP.NrOfMissedCleavages'] == 0].shape[0]
        One_C = Temp[Temp['PEP.NrOfMissedCleavages'] == 1].shape[0]
        Two_C = Temp[Temp['PEP.NrOfMissedCleavages'] == 2].shape[0]
        Missed_Cleavage = (One_C + Two_C * 2) / (Zero_C + One_C * 2 + Two_C * 3)
        No_MissC_Percent = 100 - float(Missed_Cleavage) * 100
        Dic_No_Cleavages[Name] = round(No_MissC_Percent,2)
        Dic_Missed_Cleavage[Name] = 100 - No_MissC_Percent
        Dic_ProteinGroups[Name] = len(Temp['PG.ProteinAccessions'].drop_duplicates())
        Dic_Precursors[Name] = Judge_Error(Temp,'R.PrecursorsIdentified')
        Dic_MS_CycleTime[Name] = Judge_Error(Temp,'R.Cycle Time (MS1)')
        Dic_MS2_CycleTime[Name] = Judge_Error(Temp,'R.Cycle Time (MS2)')
        Dic_MS_DataPoint[Name] = Judge_Error(Temp,'R.Data Points per Peak (MS1)(EXT)')
        Dic_MS2_DataPoint[Name] = Judge_Error(Temp,'R.Data Points per Peak (MS2)(EXT)')
        Dic_Median_PeakWidth[Name] = round(float(Judge_Error(Temp,'R.Median Peak Width(EXT)')) * 60,3)
        Dic_Median_FWHM[Name] = round(float(Judge_Error(Temp,'R.Median FWHM [min](EXT)')) * 60,3)
        Dic_Peak_Capacity[Name] = Judge_Error(Temp,'R.Peak Capacity(EXT)')
        Dic_Number_MS1_Spectra[Name] = Judge_Error(Temp,'R.Number of MS1 Spectra')
        Dic_Number_MS2_Spectra[Name] = Judge_Error(Temp,'R.Number of MS2 Spectra')
        PPM_Data = Temp[['PEP.GroupingKey','FG.RawMassAccuracy (PPM)']]
        PPM_Data = PPM_Data[pd.to_numeric(PPM_Data['FG.RawMassAccuracy (PPM)'], errors='coerce').notnull()]
        Dic_Average_PPM[Name] = PPM_Data.drop_duplicates()['FG.RawMassAccuracy (PPM)'].mean()
        Dic_Median_PPM[Name] = PPM_Data.drop_duplicates()['FG.RawMassAccuracy (PPM)'].median()
        New = Temp[['PG.ProteinAccessions','PG.Quantity']]
        New = New.dropna().drop_duplicates()
        Dic_Protein_SumQuantity[Name] = int(New['PG.Quantity'].sum())
        Dic_Protein_MeanQuantity[Name] = int(New['PG.Quantity'].mean())
        Dic_Protein_MedianQuantity[Name] = int(New['PG.Quantity'].median())
        Temp = Temp.dropna()
        Dic_Filter_Peptides[Name] = len(Temp['PEP.GroupingKey'].drop_duplicates())
        Dic_Filter_ProteinGroups[Name] = len(Temp['PG.ProteinAccessions'].drop_duplicates())
        if IRT_Add == 'TRUE':
            for Seq in IRT_Seq:
                DealData = Temp[Temp['PEP.GroupingKey'] == Seq]
                if DealData.shape[0] > 0:
                    DealData = DealData.sort_values(by = 'PEP.Quantity',ascending = False)
                    Value = DealData['PEP.Quantity'].iloc[0]
                    Value = int(Value)
                    RT  = DealData['EG.ApexRT'].iloc[0]
                else:
                    Value = 'NA'
                    RT = 'NA'
                Output_IRT.write(str(Name) + '\t' + str(Seq) + '\t' + str(Value) + '\t' + str(RT) + '\n')
    if IRT_Add == 'TRUE':
        Output_IRT.close()
    Output = open(Output_Dir + r'\\' + str(Label) + '_SP_Stat_Summary.txt','w')
    Output.write('Raw file' + '\t' + 'Number of ProteinGroups' + '\t' + 'Number of Peptides' + '\t' + 'Number of Precursors' + '\t' + 
    'Peak Capacity' + '\t' + 'Number of MS1 Spectra' + '\t' + 'Number of MS2 Spectra' + '\t' + 
    'Median of FWHM (s)' + '\t' + 'Median of RT Length (s)' + '\t' + 
    'Cycle Time (MS1)' + '\t' + 'Cycle Time (MS2)' + '\t' + 'Data Points per Peak (MS1)' + '\t' + 'Data Points per Peak (MS2)' + '\t' + 
    'Protein Quantity (Sum)' + '\t' + 'Protein Quantity (Median)' + '\t' + 'Protein Quantity (Mean)' + '\t' + 
    'Average_PPM' + '\t' + 'Median_PPM' + '\t' + 'No_Miss_Cleavages_Percent(%)' + '\t' + 'Missed_Cleavage (%)'  + '\t' + 'Quantified_ProteinGroups' + '\t' + 'Quantified_Peptides' + '\n')
    for Name in Exp_List:
        Output.write(str(Name) + '\t' + str(Dic_ProteinGroups[Name]) + '\t' + str(Dic_Peptides[Name]) + '\t' + str(Dic_Precursors[Name]) + '\t' 
        + str(Dic_Peak_Capacity[Name]) + '\t' + str(Dic_Number_MS1_Spectra[Name]) +  '\t' + str(Dic_Number_MS2_Spectra[Name]) +  '\t' 
        + str(Dic_Median_FWHM[Name]) + '\t' + str(Dic_Median_PeakWidth[Name]) + '\t' 
        + str(Dic_MS_CycleTime[Name]) + '\t' + str(Dic_MS2_CycleTime[Name]) + '\t' 
        + str(Dic_MS_DataPoint[Name]) + '\t' + str(Dic_MS2_DataPoint[Name]) + '\t' 
        + str(Dic_Protein_SumQuantity[Name]) + '\t' + str(Dic_Protein_MedianQuantity[Name]) + '\t' 
        + str(Dic_Protein_MeanQuantity[Name]) + '\t' + str(Dic_Average_PPM[Name]) + '\t' + str(Dic_Median_PPM[Name]) + '\t' 
        + str(Dic_No_Cleavages[Name]) + '\t' + str(Dic_Missed_Cleavage[Name]) + '\t' +
        str(Dic_Filter_ProteinGroups[Name]) + '\t' + str(Dic_Filter_Peptides[Name]) + '\n')
    
    Output.close()
    if QC == 'TRUE':
        Analysis_Log = [FileName for FileName in os.listdir(TargetDir) if FileName.endswith('AnalysisLog.txt')]
        Analysis_Log = os.path.join(TargetDir,Analysis_Log[0])
        WarnInfo = list()
        for Info in open(Analysis_Log):
            if 'WARNING' in Info or 'ERROR' in Info: 
                    Temp = Info.strip()
                    if Temp in WarnInfo:
                        continue
                    else:
                        WarnInfo.append(Temp)
        if WarnInfo:
            Output = open(Output_Dir + r'\\' + str(Label) + '_SP_Stat_Summary.txt','a')
            for Info in WarnInfo:
                Output.write(str(Info) + '\n')
            Output.close()
    
    return(Output_Dir + r'\\' + str(Label) + '_SP_Stat_Summary.txt')

