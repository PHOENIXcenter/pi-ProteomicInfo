import pandas as pd
import sys
import os
import numpy as np
from datetime import datetime

# Proteins文件
def Stat_PD_Protein(Protein,ExpName):
    Data = pd.read_table(Protein,sep = '\t')
    Filter_Data = Data[Data['Master'] == 'IsMasterProtein']
    ## Abundance列中的NaN是否要过滤
    Name = 'Abundance: ' + ExpName
    Temp = Filter_Data[['Accession',Name]].dropna()
    return (Filter_Data['# Unique Peptides'].sum(),Filter_Data.shape[0],Temp.sum()[1],Temp.median()[0],Temp.mean()[0])

# PSM 文件
def Stat_PD_PSM(PSM):
    Data = pd.read_table(PSM,sep = '\t')
    PPM_Data = Data[['RT [min]','DeltaM [ppm]']]
    
    List_stat_PPM = PPM_Data['DeltaM [ppm]'].describe()
    Percent25 = List_stat_PPM[4]
    Percent75 = List_stat_PPM[6]
    Gap = float(Percent75) - float(Percent25)
    Gap = float(Gap) * 1.5
    Min = float(Percent25) - Gap
    Max = float(Percent75) + Gap

    PPM_Data = PPM_Data[(PPM_Data['DeltaM [ppm]'] > Min ) & (PPM_Data['DeltaM [ppm]'] < Max) ]
    Median = PPM_Data['DeltaM [ppm]'].median()
    Percent75 = round(float(Percent75),3)
    Percent50 = round(float(Median),3)
    Percent25 = round(float(Percent25),3)
    return(Percent25, Percent50, Percent75)

def Stat_PD_Peptide(Peptides):
    Data = pd.read_table(Peptides,sep = '\t')
    if int(Data.shape[0]) != 0:
        Missed_Cleavages = Data[['Sequence','# Missed Cleavages']]
        Temp = Missed_Cleavages[Missed_Cleavages['# Missed Cleavages'] == 0]
        MC_Percent = float(Temp.shape[0]) / float(Data.shape[0])
        MC_Percent = round(MC_Percent * 100,2)
        return(Data.shape[0],MC_Percent)
    else:
        return(0,0)

def Stat_PD_MSMS(MSMS):
    Data = pd.read_table(MSMS,sep = '\t')
    return(Data.shape[0])

def Stat_ConsensusFeatures(ConsensusFeatures):
    Data = pd.read_table(ConsensusFeatures,sep = '\t')
    RT_Length = Data[['Right RT [min]','Left RT [min]']]
    RT_Length['Length'] = RT_Length['Right RT [min]'] - RT_Length['Left RT [min]']
    RT_Length['RT_Length'] = RT_Length['Length'] * 60
    List_stat = RT_Length['RT_Length'].describe()
    Percent25 = List_stat[4]
    Percent75 = List_stat[6]
    Gap = float(Percent75) - float(Percent25)
    Gap = float(Gap) * 1.5
    Min = float(Percent25) - Gap
    Max = float(Percent75) + Gap
    RT_Length = RT_Length[(RT_Length['RT_Length'] > Min ) & (RT_Length['RT_Length'] < Max) ]
    Median = RT_Length['RT_Length'].median()
    Percent75 = round(float(Percent75),3)
    Median = round(float(Median),3)
    Percent25 = round(float(Percent25),3)
    return Percent75, Median, Percent25

def PD_Extract(Parm1,Parm2,Parm3,QC):
    Date = str(datetime.now()).split(' ')[0]
    Work_Dir = Parm1
    Sample = Parm2
    New = Parm3
    if QC == 'TRUE':
        Output_Dir = os.path.join(New,str(Date) + '_QC_Report')
        os.makedirs(Output_Dir,exist_ok=True)
    #else:
    #    Output_Dir = Parm3
    #    Sample = 'Stat'
    
    Protein_File = Work_Dir + '\\' + Sample + r'_Proteins.txt'
    PSM_File = Work_Dir + '\\' + Sample + r'_PSMs.txt'
    Peptides_File = Work_Dir + '\\' + Sample + r'_PeptideGroups.txt'
    MSMS_File = Work_Dir + '\\' + Sample + r'_MSMSSpectrumInfo.txt'
    ConsensusFeatures_File = Work_Dir + '\\' + Sample + r'_ConsensusFeatures.txt'
    
    Nu_Uniq_Peptide,Nu_Protein,Sum_Intensity,Median_Intensity,Mean_Intensity = Stat_PD_Protein(Protein_File,Sample)
    PPM_25,PPM_50,PPM_75 = Stat_PD_PSM(PSM_File)
    Nu_Peptide,Missed_Cleavages_Percent = Stat_PD_Peptide(Peptides_File)
    Nu_MSMS = Stat_PD_MSMS(MSMS_File)
    Nu_75,Nu_Median,Nu_25 = Stat_ConsensusFeatures(ConsensusFeatures_File)
    Temp = pd.read_table(PSM_File,sep = '\t')
    Nu_PSM = Temp.shape[0]
    del(Temp)
    
    Output = open(Output_Dir + r'\\' + str(Sample) + '_PD_Stat_Summary.txt','w')
    Output.write('Raw file' + '\t' + 'Number of ProteinGroups' + '\t' + 'Number of Peptides' + '\t' + 'Number of PSM' + '\t' + 
    'Number of MSMS' + '\t' + 'No_Missed_Cleavage (%)' + '\t' + 'Experiment' + '\t' + 'Percent75 of RT Length (s)' + '\t' + 'Median of RT Length (s)' + '\t' + 
    'Percent25 of RT Length (s)' + '\t' + 'Percent75 of PPM' + '\t' + 'Median of PPM' + '\t' + 'Percent25 of PPM' + '\t' + 'Protein Quantity (Sum)' + '\t' + 'Protein Quantity (Median)' + '\t' + 'Protein Quantity (Mean)' + '\n')
    
    Group = Sample.split('_')
    NewGroup = Group[0] + '_' + Group[1] + '_' + Group[2] + '_' + Group[3] + '_' + Group[-1]
    
    Output.write(str(Sample) + '\t' + str(Nu_Protein) + '\t' + str(Nu_Peptide) + '\t' + str(Nu_PSM) + '\t' + str(Nu_MSMS) + 
    '\t' + str(Missed_Cleavages_Percent) + '\t' + str(NewGroup) + '\t' + str(Nu_75) + '\t' + str(Nu_Median) + '\t' + 
    str(Nu_25) + '\t' + str(PPM_75) + '\t' + str(PPM_50) + '\t' + str(PPM_25) + '\t' + str(Sum_Intensity) + '\t' + str(Median_Intensity) + '\t' + str(Mean_Intensity) + '\n')
    
    Output.close()
    
    return(Output_Dir + r'\\' + str(Sample) + '_PD_Stat_Summary.txt')

