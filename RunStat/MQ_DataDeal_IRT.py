import os
import sys
import re
import shutil
import time
from datetime import datetime
import pandas as pd

global Dic_Peptide_Nu,Dic_Protein_Nu,Dic_Mean_Intensity,Dic_Sum_Intensity,IRT_Seq
List_Name = list()
Dic_Peptide_Nu = {}
Dic_Protein_Nu = {}
Dic_Mean_Intensity = {}
Dic_Sum_Intensity = {}
Dic_Median_Intensity = {}

IRT_File = os.path.join(os.getcwd(),'Config','CharacteristicPeakIRT.txt')
IRT_Seq = list()

if os.path.exists(IRT_File):
    for Seq in open(IRT_File):
        if str(Seq) not in IRT_Seq and str(Seq) != '':
            IRT_Seq.append(str(Seq).strip())

if len(IRT_Seq) < 1 or not os.path.exists(IRT_File):
    IRT_Seq = ['LGGNEQVTR', 'GAGSSEPVTGLDAK', 'VEATFGVDESNAK', 'YILAGVENSK','TPVISGGPYEYR', 'TPVITGAPYEYR', 'DGLDAASYYAPVR', 'ADVTPADFSEWSK','GTFIIDPGGVIR', 'GTFIIDPAAVIR', 'LFLQFGAQGSPFLK']

def Stat_Peptide(Dir_Work):
    global List_Name
    Peptide = Dir_Work + r'\\peptides.txt'
    Data = pd.read_table(Peptide,sep = '\t')
    Filter_Data = Data[(Data['Reverse'] != '+') & (Data['Potential contaminant'] != '+')]
    Intensity_Name = list(filter(re.compile("Intensity[\w\W]+").match,Filter_Data.columns))
    Intensity_Bar = Filter_Data[Intensity_Name]
    Exp_Name = list(Intensity_Bar)
    Exp_Name = [str(Exp_Name[i]).replace('Intensity ','') for i in range(len(Exp_Name))]
    Intensity_Bar.columns = Exp_Name
    List_Name = Exp_Name
    for Name in Exp_Name:
        Temp = Intensity_Bar[Intensity_Bar[Name] != 0]
        Dic_Peptide_Nu[Name] = str(Temp.shape[0])

def Stat_Protein(Dir_Work):
    Protein = Dir_Work + r'\\proteinGroups.txt'
    Data = pd.read_table(Protein,sep = '\t')
    Filter_Data = Data[(Data['Reverse'] != '+') & (Data['Potential contaminant'] != '+') & (Data['Only identified by site'] != '+')]
    Intensity_Name = list(filter(re.compile("Intensity[\w\W]+").match,Filter_Data.columns))
    Intensity_Bar = Filter_Data[Intensity_Name]
    Exp_Name = list(Intensity_Bar)
    Exp_Name = [str(Exp_Name[i]).replace('Intensity ','') for i in range(len(Exp_Name))]
    Intensity_Bar.columns = Exp_Name
    for Name in Exp_Name:
        Temp = Intensity_Bar[Intensity_Bar[Name] != 0]
        Dic_Protein_Nu[Name] = str(Temp.shape[0])
        Dic_Mean_Intensity[Name] = str(Temp[Name].mean())
        Dic_Sum_Intensity[Name] = str(Temp[Name].sum())
        Dic_Median_Intensity[Name] = str(Temp[Name].median())

def Stat_Summary(Dir_Work,IRT_Add,NameLabel):
    global Summary_Info,Output_Dir
    Label = NameLabel
    Summary = Dir_Work + r'\\summary.txt'
    Data = pd.read_table(Summary,sep = '\t',dtype = {'Experiment':'str'})
    if 'MS/MS Identified' in Data.columns:
        NameList = ['Raw file','Experiment','MS','MS/MS','MS/MS Identified','MS/MS Identified [%]','Peptide Sequences Identified']
    else:
        NameList = ['Raw file','Experiment','MS','MS/MS','MS/MS identified','MS/MS identified [%]','Peptide sequences identified']
    Summary_Info = Data[NameList]
    Summary_Info = Summary_Info.dropna()
    
    Evidence = Dir_Work + r'\evidence.txt'
    ColName = ['Raw file','Experiment','Sequence','m/z','Charge','Retention time','Retention length','Intensity','Uncalibrated mass error [ppm]']
    Data = pd.read_table(Evidence,sep = '\t',usecols = ColName)
    Data = Data[['Raw file','Experiment','Sequence','m/z','Charge','Retention time','Retention length','Intensity','Uncalibrated mass error [ppm]']]

    List_stat = Data['Uncalibrated mass error [ppm]'].describe()
    Percent25 = List_stat[4]
    Percent75 = List_stat[6]
    Gap = float(Percent75) - float(Percent25)
    Min = float(Percent25) - Gap
    Max = float(Percent75) + Gap
    Temp = Data[(Data['Uncalibrated mass error [ppm]'] > Min ) & (Data['Uncalibrated mass error [ppm]'] < Max) ]
    Summary_Info['Percent75 of PPM'] = round(float(Percent75),3)
    Summary_Info['Median of PPM'] = round(float(Temp['Uncalibrated mass error [ppm]'].median()),3)
    Summary_Info['Percent25 of PPM'] = round(float(Percent25),3)
    Allpeptides = Dir_Work + r'\allPeptides.txt'
    
    if IRT_Add == 'TRUE':
        Temp = Summary_Info[['Raw file','Experiment']]
        RawFile = list(Temp['Raw file'])
        Mapping = Temp
        del(Temp)
        OutputFile = open(Dir_Work + r'\Evidence_MZ.txt','w')
        OutputFile.write('Sequence' + '\t' + 'm/z' + '\t' + 'File' + '\n')
        for Name in RawFile:
            DealFile = Data[Data['Raw file'] == Name]
            for Seq in IRT_Seq:
                Temp = DealFile[DealFile['Sequence'] == Seq]
                if int(Temp.shape[0] > 0):
                    Temp = Temp.sort_values(by = 'Intensity',ascending = False)
                    MZ = Temp.iloc[0]['m/z']
                    OutputFile.write(str(Seq) + '\t' + str(MZ) + '\t' + str(Name) + '\n')
                else:
                    OutputFile.write(str(Seq) + '\t' + 'None' + '\t' + str(Name) + '\n')

        OutputFile.close()
        ColName = ['Raw file','Charge','m/z','Mass','Retention time','Retention length (FWHM)','Retention length','Intensity']
        Data = pd.read_table(Allpeptides,sep = '\t',usecols = ColName)
        Data = Data[['Raw file','Charge','m/z','Mass','Retention time','Retention length (FWHM)','Retention length','Intensity']]

        Name = RawFile[0]
        Output = open(Dir_Work + r'\\' + Label + '_IRT_Summary.txt','w')
        Output.write('Raw file' + '\t' + 'Charge' + '\t' + 'm/z' + '\t' + 'Mass' + '\t' + 'Retention time' + '\t' + 'Retention length (FWHM)' + '\t' + 'Retention length' + '\t' + 'Intensity' + '\t' + 'Seq' + '\n')
        for Row in open(Dir_Work + r'\Evidence_MZ.txt'):
            Info = Row.strip().split('\t')
            if Info[0] == 'Sequence':
                continue
            Seq = Info[0]
            MZ = Info[1]
            if str(MZ) == 'None':
                Output.write(str(Name) + '\t' + '2' + '\t' + 'NA' + '\t' + 'NA' + '\t' + 'NA' + '\t' + 'NA' + '\t' + 'NA' + '\t' + 'NA' + '\t' + str(Seq) + '\n')
                continue
            # 10ppm
            MZ_Min = float(MZ) - 0.00001 * float(MZ)
            MZ_Max = float(MZ) + 0.00001 * float(MZ)
            #20ppm
            Gap2 = float(MZ[0]) * 0.00002
            Candidate1_Mix = float(MZ) - Gap2
            Candidate1_Max = float(MZ) + Gap2
            #30ppm
            Gap3 = float(MZ) * 0.00003
            Candidate2_Mix = float(MZ) - Gap3
            Candidate2_Max = float(MZ) + Gap3
            New = Data[(Data['m/z'] > MZ_Min) & (Data['m/z'] < MZ_Max) ]
            NewPPM20 = Data[(Data['m/z'] > Candidate1_Mix) & (Data['m/z'] < Candidate1_Max) ]
            NewPPM30 = Data[(Data['m/z'] > Candidate2_Mix) & (Data['m/z'] < Candidate2_Max) ]
            
            Temp = New[ (New['Raw file'] == Name) & (New['Charge'] == 2)]
            Temp2 = NewPPM20[ (NewPPM20['Raw file'] == Name) & (NewPPM20['Charge'] == 2)]
            Temp3 = NewPPM30[ (NewPPM20['Raw file'] == Name) & (NewPPM30['Charge'] == 2)]
            if int(Temp.shape[0] > 0):
                Temp = Temp.sort_values(by = 'Intensity',ascending = False)
            else:
                if int(Temp2.shape[0] > 0):
                    Temp = Temp2.sort_values(by = 'Intensity',ascending = False)
                else:
                    if int(Temp3.shape[0] > 0):
                        Temp = Temp3.sort_values(by = 'Intensity',ascending = False)
                    else:
                        Output.write(str(Name) + '\t' + '2' + '\t' + str(MZ) + '\t' + 'NA' + '\t' + 'NA' + '\t' + 'NA' + '\t' + 'NA' + '\t' + 'NA' + '\t' + str(Seq) + '\n')
            Output.write(str(Name) + '\t' + '2' + '\t' + str(MZ) + '\t' + str(Temp.iloc[0]['Mass']) + '\t' + str(Temp.iloc[0]['Retention time']) + '\t' + str(Temp.iloc[0]['Retention length (FWHM)']) + '\t' + str(Temp.iloc[0]['Retention length']) + '\t' + str(Temp.iloc[0]['Intensity']) + '\t' + str(Seq) + '\n')
        
        Output.close()
        Output = pd.read_table(Dir_Work + r'\\' + Label + '_IRT_Summary.txt',sep = '\t')
        Output = pd.merge(Mapping,Output,on = 'Raw file')
        Output = Output.rename(columns = {'Retention time':'Retention time (min)'})
        Output.to_csv(Dir_Work + r'\\' + Label + '_IRT_Summary.txt',sep = '\t',index = False)
        shutil.copy(Dir_Work + r'\\' + Label + '_IRT_Summary.txt',Output_Dir)
    
    else:
        ColName = ['Raw file','Charge','m/z','Mass','Retention time','Retention length (FWHM)','Retention length','Intensity']
        Data = pd.read_table(Allpeptides,sep = '\t',usecols = ColName)
        Data = Data[['Raw file','Charge','m/z','Mass','Retention time','Retention length (FWHM)','Retention length','Intensity']]
    
    List_stat = Data['Retention length'].describe()
    Percent25 = List_stat[4]
    Percent75 = List_stat[6]
    Gap = float(Percent75) - float(Percent25)
    Min = float(Percent25) - Gap
    Max = float(Percent75) + Gap
    Data = Data[(Data['Retention length'] > Min ) & (Data['Retention length'] < Max) ]
    MeanValue = float(Data['Retention length'].mean()) * 60
    MedianValue = float(Data['Retention length'].median()) * 60
    Summary_Info['Retention_length_Mean (s)'] = round(MeanValue,3)
    Summary_Info['Retention_length_Median (s)'] = round(MedianValue,3)

def MQ_Extract(Parm1,Parm2,Parm3,QC):
    global List_Name,Output_Dir,IRT_Add
    Date = str(datetime.now()).split(' ')[0]
    Work_Dir = Parm1
    Output_Dir = Parm2
    IRT_Add = Parm3
    if QC == 'TRUE':
        os.makedirs(Output_Dir,exist_ok=True)
        Name = Work_Dir.split('\\')[-1]
        NameLabel = Name
    else:
        NameLabel = 'Cohort'
    
    Dir = Work_Dir + r'\combined\txt'
    Stat_Protein(Dir)
    Stat_Peptide(Dir)
    Stat_Summary(Dir,IRT_Add,NameLabel)
    
    
    Output = open(Output_Dir + r'\\' + NameLabel + r'_MQ_Stat_Summary.txt','w')
    Output.write('Experiment' + '\t' + 'Number of ProteinGroups'+ '\t' + 'Number of Peptides' + '\t' +'Protein Quantity (Sum)'+ '\t' + 'Protein Quantity (Median)' + '\t' +'Protein Quantity (Mean)'+ '\n')
    for Name in List_Name:
        Output.write(str(Name) + '\t' + str(Dic_Protein_Nu[Name]) + '\t' + str(Dic_Peptide_Nu[Name]) + '\t' + str(Dic_Sum_Intensity[Name]) + '\t' + str(Dic_Median_Intensity[Name]) + '\t' + str(Dic_Mean_Intensity[Name]) + '\n')
    
    Output.close()
    
    Summary_Info['Experiment'] = Summary_Info['Experiment'].astype(str)
    Record = pd.read_table(Output_Dir + r'\\' + NameLabel + r'_MQ_Stat_Summary.txt',sep = '\t')
    Record['Experiment'] = Record['Experiment'].astype(str)
    AllData = pd.merge(Record,Summary_Info,on = 'Experiment')
    AllData.to_csv(Output_Dir + r'\\' + NameLabel + r'_MQ_Stat_Summary.txt',sep = '\t',index = False)
    return(Output_Dir + r'\\' + NameLabel + r'_MQ_Stat_Summary.txt')

