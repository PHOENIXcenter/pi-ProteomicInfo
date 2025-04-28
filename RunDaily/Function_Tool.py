import pandas as pd

def Change(List):
    NewList = []
    for Value in List:
        if Value > 200:
            NewList.append(int(Value))
        else:
            NewList.append(round(Value,2))
    return(NewList)

def GetValue(DealData):
    Min = DealData.min().tolist()
    Min.pop(0)
    Max = DealData.max().tolist()
    Max.pop(0)
    Mean = DealData.mean().tolist()
    if len(Min) < 5:
        Min.insert(2,0)
        Min.insert(3,0)
        Max.insert(2,0)
        Max.insert(3,0)
        Mean.insert(2,0)
        Mean.insert(3,0)
    
    Min_Max = Min + Max
    Mean_Mean = Mean + Mean
    Min_Max = Change(Min_Max)
    Mean_Mean = Change(Mean_Mean)
    return(Min_Max,Mean_Mean)

def GetInfo(File):
    Data = pd.read_table(File,sep = '\t')
    ColList = ['Number of ProteinGroups','Number of Peptides','Protein Quantity (Sum)','Protein Quantity (Median)']
    
    if 'Median of RT Length (s)' not in list(Data):
        ColList.append('Retention_length_Median (s)')
    else:
        ColList.append('Median of RT Length (s)')
    
    if 'Median of PPM' not in list(Data):
        ColList.append('Median_PPM')
    else:
        ColList.append('Median of PPM')
    
    Data = Data[ColList]
    List_Info = Data.median()
    return(List_Info)