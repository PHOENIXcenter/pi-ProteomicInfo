# Author: huangcx
# ProteinGroups数据处理

import sys
import os
import pandas as pd
import numpy as np
import re
from plotnine import *
from matplotlib.cbook import boxplot_stats
from sklearn.preprocessing import StandardScaler
from sklearn.impute import KNNImputer
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap
from matplotlib import pyplot as plt
import seaborn as sns

#除去非0值的结果 中值归一化
def GetMedian(Data):
    Base = Data.median().mean()
    Data = Data.apply(lambda x: x / pd.DataFrame([ n for n in x if n > 0]).median()[0] * Base,axis = 0)
    return(Data)


def GetMean(Data):
    Data = Data.apply(lambda x: x / pd.DataFrame([ n for n in x if n > 0]).mean()[0],axis = 0)
    return(Data)

##Method min与max设置考虑存在重复定量的数据值，min(相同数值取排名小的作为最终排序)结果大点max(相同数值取排名大的作为最终排序)结果小点
## Quantile处理前将NA值填充为最小值后，再次进行处理
def GetQuantile(Data):
    Sorted_Data = pd.DataFrame(np.sort(Data.values,axis = 0),columns = Data.columns)  ## axis = 0 按列排序 axis = 1 按行排序
    Mean_Index = Sorted_Data.T.mean()
    Mean_Index.index = range(1,len(Mean_Index) + 1)
    Data = Data.rank(method = 'min').stack().astype(int).map(Mean_Index).unstack()
    return(Data)

# 填充数据

def Replace_minimum(Data,ColName):
    Store = list()
    for Name in ColName:
        Min = Data[Name][Data[Name] > 0].min()
        Store.append(float(Min))
    Min = min(Store)
    return(Min)

def Boxplot_Pic(Data,X_Name,Y_Name,FileName,Width_Size,S_N,E_N):
    Pic = ggplot(Data,aes(X_Name,Y_Name,fill = 'Type')) + geom_boxplot() + coord_cartesian(ylim = [S_N,E_N]) + theme_classic()
    Pic = Pic + theme(axis_text_x = element_text(angle = 90,hjust = 1,size = 12),axis_text_y = element_text(size = 12),axis_title_x = element_blank(),axis_title_y = element_text(size = 17))
    Pic = Pic + labs(y = 'Distribution of ' + Y_Name) + guides(fill = False)
    ggplot.save(Pic,filename = Output_Dir + '\\' + FileName + '.pdf',width = Width_Size,height = 6,path = Output_Dir)
    ggplot.save(Pic,filename = Output_Dir + '\\' + FileName + '.jpg',width = Width_Size,height = 6,path = Output_Dir,dpi = 500)

def Boxplot_Pic2(Data,X_Name,Y_Name,FileName,Width_Size,S_N,E_N):
    Pic = ggplot(Data,aes(X_Name,Y_Name,fill = 'Type')) + geom_boxplot() + coord_cartesian(ylim = [S_N,E_N]) + theme_classic()
    Pic = Pic + theme(axis_text_x = element_blank(),axis_text_y = element_text(size = 12),axis_title_x = element_blank(),axis_title_y = element_text(size = 17))
    Pic = Pic + labs(y = 'Distribution of ' + Y_Name) + guides(fill = False)
    ggplot.save(Pic,filename = Output_Dir + '\\' + FileName + '.pdf',width = Width_Size,height = 6,path = Output_Dir)
    ggplot.save(Pic,filename = Output_Dir + '\\' + FileName + '.jpg',width = Width_Size,height = 6,path = Output_Dir,dpi = 500)

def Coord_cartesian(Value):
    Stats = boxplot_stats(Value)
    Start = float(Stats[0]['whislo']) / 1.3
    End = float(Stats[0]['whishi']) * 1.2
    return Start,End

def Transfor_Data_Boxplot(File,List_Name):
    Data_Tran = pd.DataFrame()
    for Name in List_Name:
        Temp = pd.DataFrame(File[Name])
        #print(Name)
        Temp.columns = ['Intensity']
        Temp['Group'] = Name
        Temp['Type'] = Dic_Group[Name]
        Data_Tran = pd.concat([Data_Tran,Temp])
    return(Data_Tran)

def RunMonitor(Param_1,Param_2,Param_3,Param_4,Param_5,Param_6,Param_7,Param_8,Param_9,Param_10,Param_11,Param_12,Param_13):
    global Work_Dir, Output_Dir,Dic_Raw,Dic_Group
    SoftWare = Param_1
    Work_Dir = Param_2
    Output_Dir = Param_3
    Filter_Nu = int(Param_4)
    Normalize = Param_5
    Impute = Param_6
    Jiangwei = Param_7
    NameMapping = Param_8
    Header = Param_9
    Filter_Only_Identified_By_Site = Param_10
    UniquePeptide = int(Param_11)
    ProbabilityMin = float(Param_12)
    Filter_Group = float(Param_13)
    
    if SoftWare == 'MQ':
        File = Work_Dir + r'\proteinGroups.txt'
    elif SoftWare == 'SP' or SoftWare == 'Matrix':
        File = Work_Dir
    elif SoftWare == 'MS':
        File = Work_Dir + r'\combined_protein.tsv'
    #print(File)
    Dic_Raw = {}
    Dic_Group = {}
    Group_List = list()
    for Info in open(NameMapping):
        if Info.startswith('#RawName'):
            continue
        Info = Info.rstrip().split(',')
        Dic_Raw[Info[0]] = Info[1]
        Dic_Group[Info[1]] = Info[2]
        if Info[2] not in Group_List:
            Group_List.append(Info[2])
    
    # 必须过滤项 Reverse Potential contaminant 可选过滤 Only identified by site 、UniquePeptide
    if SoftWare == 'MQ':
        Data = pd.read_table(File,sep = '\t')
        if Filter_Only_Identified_By_Site == 'True':
            Filter_Data = Data[(Data['Reverse'] != '+') & (Data['Potential contaminant'] != '+') &(Data['Only identified by site'] != '+')]
        else:
            Filter_Data = Data[(Data['Reverse'] != '+') & (Data['Potential contaminant'] != '+')]
        Filter_Data = Filter_Data[(Filter_Data['Unique peptides'] > int(UniquePeptide))] 
        del(Data)
        
        # 统计非零值
        ColList = list(set(filter(re.compile(Header + " [\w\W]+").match, Filter_Data.columns)).difference(set(['iBAQ peptides'])))
        Filter_Data.index = list(Filter_Data['Majority protein IDs'])
        Intensity_Data = Filter_Data[ColList]
        Exp_Name = list(Intensity_Data)
        Exp_Name = [str(Exp_Name[i]).replace(Header + ' ','') for i in range(len(Exp_Name))]
    
    if SoftWare == 'MS':
        Data = pd.read_table(File,sep = '\t')
        Filter_Data = Data[(Data['Protein Probability'] >= ProbabilityMin) & (Data['Combined Unique Spectral Count']  > int(UniquePeptide))]
        del(Data)
        # 统计非零值
        if Header == 'Intensity':
            ColList = list(set(filter(re.compile("[\w\W]+ " + Header + '$').match, Filter_Data.columns)).difference(set(filter(re.compile("[\w\W]+ MaxLFQ Intensity" + '$').match, Filter_Data.columns))))
        else:
            ColList = list(filter(re.compile("[\w\W]+ MaxLFQ Intensity" + '$').match, Filter_Data.columns))
        Filter_Data.index = list(Filter_Data['Protein ID'])
        Intensity_Data = Filter_Data[ColList]
        Exp_Name = list(Intensity_Data)
        if Header == 'Intensity':
            Exp_Name = [str(Exp_Name[i]).replace(' Intensity','') for i in range(len(Exp_Name))]
        else:
            Exp_Name = [str(Exp_Name[i]).replace(' MaxLFQ Intensity','') for i in range(len(Exp_Name))]
    
    if SoftWare == 'Matrix':
        if File.endswith('.xls'):
            Deal_Data = pd.read_table(File,sep = '\t',index_col = 0,encoding = 'gbk')
        if File.endswith('.txt'):
            Deal_Data = pd.read_table(File,sep = '\t',index_col = 0,encoding = 'gbk')
        if File.endswith('.xlsx'):
            Deal_Data = pd.read_excel(File,index_col = 0)
        if File.endswith('.csv'):
            Deal_Data = pd.read_table(File,sep = ',',index_col = 0,encoding = 'gbk')
        if File.endswith('.tsv'):
            Deal_Data = pd.read_table(File,sep = '\t',index_col = 0,encoding = 'gbk')
        Filter_Data = Deal_Data.replace(np.nan,0)
        Intensity_Data = Filter_Data.replace('Filtered',0)
        Exp_Name = list(Intensity_Data)
    
    if SoftWare == 'SP':
        if File.endswith('.xls'):
            Deal_Data = pd.read_table(File,sep = '\t',index_col = 0,encoding = 'gbk')
        if File.endswith('.txt'):
            Deal_Data = pd.read_table(File,sep = '\t',index_col = 0,encoding = 'gbk')
        if File.endswith('.xlsx'):
            Deal_Data = pd.read_excel(File,index_col = 0)
        if File.endswith('.csv'):
            Deal_Data = pd.read_table(File,sep = ',',index_col = 0,encoding = 'gbk')
        if File.endswith('.tsv'):
            Deal_Data = pd.read_table(File,sep = '\t',index_col = 0,encoding = 'gbk')
        Filter_Data = Deal_Data.replace(np.nan,0)
        Filter_Data = Filter_Data[Filter_Data['PG.NrOfStrippedSequencesIdentified (Experiment-wide)'] > int(UniquePeptide)]
        Intensity_Data = Filter_Data.replace('Filtered',0)
        Exp_Name = list(Intensity_Data)
        if 'PG.NrOfStrippedSequencesIdentified (Experiment-wide)' in Exp_Name:
            Exp_Name.remove('PG.NrOfStrippedSequencesIdentified (Experiment-wide)')
        if 'PG.Genes' in Exp_Name:
            Exp_Name.remove('PG.Genes')
        Intensity_Data = Intensity_Data[Exp_Name]
        Exp_Name = list(Intensity_Data)
    Exp_Name = [Dic_Raw[str(Exp_Name[i])] for i in range(len(Exp_Name))]
    Intensity_Data.columns = Exp_Name
    # Zero_Nu统计的非0值的个数
    Intensity_Data = Intensity_Data.astype(float)
    Intensity_Data['Zero_Nu'] = (Intensity_Data == 0).astype(int).sum(axis = 1)
    
    for Group in Group_List:
        ColName = {Key for Key, value in Dic_Group.items() if value == Group}
        Group_Data = Intensity_Data[list(ColName)]
        Intensity_Data[Group] = (Group_Data > 0).astype(int).sum(axis = 1) / len(ColName)
    
    Retain_Nu = len(Exp_Name) - Filter_Nu
    Intensity_Data['Max_Group_Percent'] = Intensity_Data[Group_List].max(axis=1)
    Intensity_Data.to_csv(Output_Dir + r'\Experss_Data_Count_Zero.txt',sep = '\t')
    print(Filter_Nu)
    print(Filter_Group)
    if int(Filter_Nu) == 0 :
        print('Do1')
        Part2 = Intensity_Data[(Intensity_Data['Max_Group_Percent'] >= Filter_Group) ]
        Deal_Data = Part2
    elif float(Filter_Group) == 0:
        print('Do2')
        Part1 = Intensity_Data[(Intensity_Data['Zero_Nu'] <= Retain_Nu)]
        Deal_Data = Part1
    else:
        print('Do3')
        Part1 = Intensity_Data[(Intensity_Data['Zero_Nu'] <= Retain_Nu)]
        Part2 = Intensity_Data[(Intensity_Data['Max_Group_Percent'] >= Filter_Group) ]
        Deal_Data = pd.concat([Part1, Part2]).drop_duplicates()
    
    Deal_Data = Deal_Data[Exp_Name]
    del(Intensity_Data,Filter_Data)
    
    Nu = len(Exp_Name)
    Size = float(Nu) * 0.6
    if float(Size) > 20:
        Size = 20
    
    Deal_Data = Deal_Data.astype(float)
    PlotData = Transfor_Data_Boxplot(Deal_Data,Exp_Name)
    PlotData = PlotData[PlotData['Intensity'] != 0]
    PlotData['Log10 (Intensity)'] = PlotData['Intensity'].apply(np.log10)
    if int(Nu) <= 100:
        Start,End = Coord_cartesian(PlotData['Intensity'])
        Boxplot_Pic(PlotData,'Group','Intensity','Intensity_Before_Normalize_Box',Size,Start,End)
        Start,End = Coord_cartesian(PlotData['Log10 (Intensity)'])
        Boxplot_Pic(PlotData,'Group','Log10 (Intensity)','Log10_Intensity_Before_Normalize_Box',Size,Start,End)
    else:
        Start,End = Coord_cartesian(PlotData['Intensity'])
        Boxplot_Pic2(PlotData,'Group','Intensity','Intensity_Before_Normalize_Box',Size,Start,End)
        Start,End = Coord_cartesian(PlotData['Log10 (Intensity)'])
        Boxplot_Pic2(PlotData,'Group','Log10 (Intensity)','Log10_Intensity_Before_Normalize_Box',Size,Start,End)
    
    ## 数据归一化 Normalize Median(样本中位数) 均值（样本均值）Quantile(样本均值 + 秩序)
    
    if Normalize == "Median":
        try:
            Deal_Data = GetMedian(Deal_Data)
        except:
            print("Normalize Error : The Median exist 0")
            exit(1)
    
    if Normalize == "Mean":
        try:
            Deal_Data = GetMean(Deal_Data)
        except:
            print("Normalize Error : The Mean exist 0")
            exit(1)
    
    if Normalize == "Quantile":
        Value = Replace_minimum(Deal_Data,Exp_Name)
        Deal_Data = Deal_Data.replace(0,float(Value))
        Deal_Data = GetQuantile(Deal_Data)
    
    PlotData = Transfor_Data_Boxplot(Deal_Data,Exp_Name)
    PlotData = PlotData[PlotData['Intensity'] > 0]
    PlotData['Log10 (Intensity)'] = PlotData['Intensity'].apply(np.log10)
    
    if int(Nu) <= 100:
        Start,End = Coord_cartesian(PlotData['Intensity'])
        Boxplot_Pic(PlotData,'Group','Intensity','Intensity_After_Normalize_Box',Size,Start,End)
        Start,End = Coord_cartesian(PlotData['Log10 (Intensity)'])
        Boxplot_Pic(PlotData,'Group','Log10 (Intensity)','Log10_Intensity_After_Normalize_Box',Size,Start,End)
    else:
        Start,End = Coord_cartesian(PlotData['Intensity'])
        Boxplot_Pic2(PlotData,'Group','Intensity','Intensity_After_Normalize_Box',Size,Start,End)
        Start,End = Coord_cartesian(PlotData['Log10 (Intensity)'])
        Boxplot_Pic2(PlotData,'Group','Log10 (Intensity)','Log10_Intensity_After_Normalize_Box',Size,Start,End)
        
    Deal_Data.to_csv(Output_Dir + r'\Normalized_Data.txt',sep = '\t')
    
    #Deal_Data = pd.read_table(Output_Dir + r'\Normalized_Data.txt',sep = '\t',index_col = 0)
    All_CV_Data = pd.DataFrame()
    CV_Data = Deal_Data.T
    CV_Data = CV_Data.replace(0,np.nan)
    CV_Std = CV_Data.std()
    CV_Mean = CV_Data.mean()
    CV_Data = pd.DataFrame(CV_Std / CV_Mean)
    CV_Data.columns = ['CV']
    CV_Data['Percent'] = CV_Data['CV'] * 100
    CV_Data['ID'] = 'All'
    All_CV_Data = pd.concat([All_CV_Data,CV_Data])
    CV_Median = All_CV_Data['Percent'].median()
    CV_Median = round(CV_Median,2)
    CV_Info = ''
    Nu = 0
    for Name in Group_List:
        File_List = [Label for Label in Exp_Name if Dic_Group[Label] == Name]
        NewData = Deal_Data[File_List]
        CV_Data = NewData.T
        CV_Std = CV_Data.std()
        CV_Mean = CV_Data.mean()
        CV_Data = pd.DataFrame(CV_Std / CV_Mean)
        CV_Data.columns = ['CV']
        CV_Data['Percent'] = CV_Data['CV'] * 100
        CV_Data['ID'] = Name
        Sub_Median = CV_Data['Percent'].median()
        Sub_Median = round(Sub_Median,2)
        Nu = Nu + 1
        if Nu in [3,6,9]:
            CV_Info = CV_Info + '\n'
        CV_Info = CV_Info + str(Name) + ' Median: ' + str(Sub_Median) + ','
        All_CV_Data = pd.concat([All_CV_Data,CV_Data])
    CV_Info = CV_Info[:-1]
    All_CV_Data.to_csv(Output_Dir + '\CV_Data.txt',sep = '\t')
    if len(Group_List) > 1:
        Pic = ggplot(All_CV_Data,aes('ID','Percent',fill = 'ID')) + geom_boxplot()  + theme_classic() + coord_cartesian(ylim = [0,150])
        Pic = Pic + theme(axis_text_x = element_text(angle = 45,hjust = 1,size = 10),axis_text = element_text(size = 13),axis_title_y = element_text(size = 13))
        Pic = Pic + labs(y = 'Distribution of Proteins CV (%)',x = 'Distribution of Proteins CV (%) (All Median: ' + str(CV_Median) + ',\n' + CV_Info + ')') + guides(fill = False)
        ggplot.save(Pic,filename = Output_Dir + '\Data_CV.pdf' ,width = 4,height = 4,path = Output_Dir)
        ggplot.save(Pic,filename = Output_Dir + '\Data_CV.jpg' ,width = 4,height = 4,path = Output_Dir,dpi = 500)
        Pic = ggplot(All_CV_Data,aes('ID','Percent',fill = 'ID')) + geom_violin()  + theme_classic() + coord_cartesian(ylim = [0,150])
        Pic = Pic + theme(axis_text_x = element_text(angle = 45,hjust = 1,size = 10),axis_text = element_text(size = 13),axis_title_y = element_text(size = 13))
        Pic = Pic + labs(y = 'Distribution of Proteins CV (%)',x = 'Distribution of Proteins CV (%) (All Median: ' + str(CV_Median) + ',\n' + CV_Info + ')') + guides(fill = False)
        ggplot.save(Pic,filename = Output_Dir + '\Data_CV_Violin.pdf' ,width = 4,height = 4,path = Output_Dir)
        ggplot.save(Pic,filename = Output_Dir + '\Data_CV_Violin.jpg' ,width = 4,height = 4,path = Output_Dir,dpi = 500)
        #CV_Data = All_CV_Data[All_CV_Data['Percent'] < 200]
        Pic = ggplot(All_CV_Data,aes('Percent',fill = 'ID')) + geom_histogram()  + theme_classic() + scale_x_continuous(limits = (0,200))
        Pic = Pic + theme(axis_text = element_text(size = 13),axis_title = element_text(size = 15)) + facet_wrap('ID')
        #CV_Info = 'TOF1 Median: ' + str(TOF1_Median) + ' ' + 'TOF2 Median: ' + str(TOF2_Median) + ' ' + 'TOF5 Median: ' + str(TOF5_Median) + ')'
        Pic = Pic + labs(x = 'Distribution of Proteins CV (%) (All Median: ' + str(CV_Median) + ',\n' + CV_Info + ')',y = 'Number of ProteinGroups')
        ggplot.save(Pic,filename = Output_Dir + '\Data_CV_Histogram.pdf' ,width = 7,height = 5,path = Output_Dir)
        ggplot.save(Pic,filename = Output_Dir + '\Data_CV_Histogram.jpg' ,width = 7,height = 5,path = Output_Dir,dpi = 500)
    else:
        Pic = ggplot(CV_Data,aes('ID','Percent')) + geom_boxplot(color = 'grey')  + theme_classic() + coord_cartesian(ylim = [0,150])
        Pic = Pic + theme(axis_text_x = element_text(angle = 45,hjust = 1,size = 10),axis_text = element_text(size = 13),axis_title_y = element_text(size = 13))
        Pic = Pic + labs(y = 'Distribution of Proteins CV (%)',x = 'Distribution of Proteins CV (%) (All Median: ' + str(CV_Median) + ')') + guides(fill = False)
        ggplot.save(Pic,filename = Output_Dir + '\Data_CV.pdf' ,width = 3,height = 3.5,path = Output_Dir)
        ggplot.save(Pic,filename = Output_Dir + '\Data_CV.jpg' ,width = 3,height = 3.5,path = Output_Dir,dpi = 500)
        Pic = ggplot(CV_Data,aes('ID','Percent')) + geom_violin(color = 'grey')  + theme_classic() + coord_cartesian(ylim = [0,150])
        Pic = Pic + theme(axis_text_x = element_text(angle = 45,hjust = 1,size = 10),axis_text = element_text(size = 13),axis_title_y = element_text(size = 13))
        Pic = Pic + labs(y = 'Distribution of Proteins CV (%)',x = 'Distribution of Proteins CV (%) (All Median: ' + str(CV_Median) + ')') + guides(fill = False)
        ggplot.save(Pic,filename = Output_Dir + '\Data_CV_Violin.pdf' ,width = 4,height = 4,path = Output_Dir)
        ggplot.save(Pic,filename = Output_Dir + '\Data_CV_Violin.jpg' ,width = 4,height = 4,path = Output_Dir,dpi = 500)
        #CV_Data = CV_Data[CV_Data['Percent'] < 200]
        Pic = ggplot(CV_Data,aes('Percent')) + geom_histogram(color = 'grey')  + theme_classic() + scale_x_continuous(limits = (0,200))
        Pic = Pic + theme(axis_text = element_text(size = 13),axis_title = element_text(size = 15))
        #CV_Info = 'TOF1 Median: ' + str(TOF1_Median) + ' ' + 'TOF2 Median: ' + str(TOF2_Median) + ' ' + 'TOF5 Median: ' + str(TOF5_Median) + ')'
        Pic = Pic + labs(x = 'Distribution of Proteins CV (%) (All Median: ' + str(CV_Median) + ')',y = 'Number of ProteinGroups')
        ggplot.save(Pic,filename = Output_Dir + '\Data_CV_Histogram.pdf' ,width = 5,height = 5,path = Output_Dir)
        ggplot.save(Pic,filename = Output_Dir + '\Data_CV_Histogram.jpg' ,width = 5,height = 5,path = Output_Dir,dpi = 500)
    
    
    ## 数据填充 Impute 可选项 minimum KNN 
    if Impute == 'Minimum':
        Value = Replace_minimum(Deal_Data,Exp_Name)
        Deal_Data = Deal_Data.replace(0,float(Value))
        #Deal_Data.to_csv(Output_Dir + r'\Normalized_Data_Impute_Min.txt',sep = '\t')
    
    if Impute == 'KNN':
        Deal_Data = Deal_Data.replace(0,'NaN')
        #Filter_Nu = len(Exp_Name) - Filter_Nu 
        #Imputer = KNNImputer(n_neighbors = int(Filter_Nu))
        Imputer = KNNImputer()
        Impute_Data = Imputer.fit_transform(Deal_Data)
        Deal_Data = pd.DataFrame(Impute_Data,index = Deal_Data.index,columns = Deal_Data.columns)
    
    if Impute == 'Quantile':
        Value = Replace_minimum(Deal_Data,Exp_Name)
        Deal_Data = Deal_Data.replace(0,float(Value))
        Deal_Data = GetQuantile(Deal_Data)
    
    Deal_Data.to_csv(Output_Dir + r'\Normalized_Impute_Data.txt',sep = '\t')
    # 填充数据后的初步展示 PCA Heatmap 考虑不同蛋白定量值的差距，将蛋白定量值进行标准化处理
    #Deal_Data = Deal_Data.apply(np.log2)
    
    scaler = StandardScaler()
    scaler.fit(Deal_Data.T)
    Data_Scale = pd.DataFrame(scaler.transform(Deal_Data.T),index = Deal_Data.T.index,columns = Deal_Data.T.columns)
    
    if Jiangwei == 'PCA':
        Fit_PCA = PCA()
        Fit_PCA.fit(Data_Scale)
        Data_PCA = pd.DataFrame(Fit_PCA.transform(Data_Scale),index = Data_Scale.index)
        Name = ['PC' +str(i) for i in range(1,Data_PCA.shape[1] + 1)]
        Data_PCA.columns = Name
        Data_Var = Data_PCA.var()
        Percent = np.around(100 * Data_Var / np.sum(Data_Var),decimals = 2)
        
        Percent_Data = pd.DataFrame({'PCA':Name,'Percent':list(Percent)})
        Percent_Data.to_csv(Output_Dir + r'\Plot_PCA_Percent.txt',sep = '\t',index = False)
        Data_PCA.to_csv(Output_Dir + r'\Plot_PCA_Data.txt',sep = '\t')
        PlotData = Data_PCA
    
    # T-SNE 样本数量少时不建议使用
    if Jiangwei == 'T-SNE':
        Fit_TSNE = TSNE()
        Data_TSNE = pd.DataFrame(Fit_TSNE.fit_transform(Data_Scale),index = Data_Scale.index)
        Name = ['TSNE-' +str(i) for i in range(1,Data_TSNE.shape[1] + 1)]
        Data_TSNE.columns = Name
        Data_TSNE.to_csv(Output_Dir + r'\Plot_TSNE_Data.txt',sep = '\t')
        PlotData = Data_TSNE
        #print(PlotData)
    
    if Jiangwei == 'UMAP':
        # 默认n_components = 2 min_dist = 0.1  n_neighbors = 15 metric 点与点之间的距离计算（选用euclidean）
        # n_neighbors 考虑做调整六分之一的数据，小于15默认15，希望例数在100例之上
        Fit_UMAP = umap.UMAP(metric = "euclidean",min_dist = 0.1,n_components = 2)
        Data_UMAP = pd.DataFrame(Fit_UMAP.fit_transform(Data_Scale),index = Data_Scale.index)
        Name = ['UMAP-' +str(i) for i in range(1,Data_UMAP.shape[1] + 1)]
        Data_UMAP.columns = Name
        Data_UMAP.to_csv(Output_Dir + r'\Plot_UMAP_Data.txt',sep = '\t')
        PlotData = Data_UMAP
    
    Info = list(Data_Scale.index)
    Info = [str(Dic_Group[i]) for i in Info]
    #print(Info)
    PlotData['Group'] = Info
    if Jiangwei == 'PCA':
        Pic = ggplot(PlotData,aes('PC1','PC2',color = 'Group')) + geom_point() + labs(x = 'PC1 ' + str(Percent[0]) + '%',y = 'PC2 ' + str(Percent[1]) + '%') + stat_ellipse(aes(fill = 'Group'))
        Pic2 = ggplot(PlotData,aes('PC1','PC2',color = 'Group')) + geom_point() + labs(x = 'PC1 ' + str(Percent[0]) + '%',y = 'PC2 ' + str(Percent[1]) + '%') + geom_label(aes(label = Data_Scale.index),size = 4) + guides(color = False)
        Pic3 = ggplot(PlotData,aes('PC1','PC2',color = 'Group')) + geom_point() + labs(x = 'PC1 ' + str(Percent[0]) + '%',y = 'PC2 ' + str(Percent[1]) + '%')
    
    if Jiangwei == 'T-SNE':
        Pic = ggplot(PlotData,aes('TSNE-1','TSNE-2',color = 'Group')) + geom_point() + stat_ellipse(aes(fill = 'Group'))
        Pic2 = ggplot(PlotData,aes('TSNE-1','TSNE-2',color = 'Group')) + geom_point() + geom_label(aes(label = Data_Scale.index),size = 4) + guides(color = False)
        Pic3 = ggplot(PlotData,aes('TSNE-1','TSNE-2',color = 'Group')) + geom_point()
    
    if Jiangwei == 'UMAP':
        Pic = ggplot(PlotData,aes('UMAP-1','UMAP-2',color = 'Group')) + geom_point() + stat_ellipse(aes(fill = 'Group'))
        Pic2 = ggplot(PlotData,aes('UMAP-1','UMAP-2',color = 'Group')) + geom_point() + geom_label(aes(label = Data_Scale.index),size = 4) + guides(color = False)
        Pic3 = ggplot(PlotData,aes('UMAP-1','UMAP-2',color = 'Group')) + geom_point()
    
    Pic = Pic + theme_classic() + theme(axis_text = element_text(size = 11),axis_title = element_text(size = 13))
    Pic2 = Pic2 + theme_classic() + theme(axis_text = element_text(size = 11),axis_title = element_text(size = 13))
    Pic3 = Pic3 + theme_classic() + theme(axis_text = element_text(size = 11),axis_title = element_text(size = 13))
    ggplot.save(Pic,filename = Output_Dir + '\Dim_Reduction_Group_' + Jiangwei + '.pdf',width = 4.2,height = 4,path = Output_Dir)
    ggplot.save(Pic,filename = Output_Dir + '\Dim_Reduction_Group_' + Jiangwei + '.jpg',width = 4.2,height = 4,path = Output_Dir,dpi = 500)
    ggplot.save(Pic2,filename = Output_Dir + '\Dim_Reduction_Info_' + Jiangwei + '.pdf',width = 6.2,height = 6,path = Output_Dir)
    ggplot.save(Pic2,filename = Output_Dir + '\Dim_Reduction_Info_' + Jiangwei + '.jpg',width = 6.2,height = 6,path = Output_Dir,dpi = 500)
    ggplot.save(Pic3,filename = Output_Dir + '\Dim_Reduction_' + Jiangwei + '.pdf',width = 4.2,height = 4,path = Output_Dir)
    ggplot.save(Pic3,filename = Output_Dir + '\Dim_Reduction_' + Jiangwei + '.jpg',width = 4.2,height = 4,path = Output_Dir,dpi = 500)
    # 相关性
    Deal_Data = Deal_Data + 1
    PlotData = Deal_Data.apply(np.log2)
    Corr_Matrix = PlotData.corr(method = 'spearman')
    Corr_Matrix.to_csv(Output_Dir + r'\Corr_Matrix_Spearman.txt',sep = '\t')
    fig = sns.clustermap(Corr_Matrix,cmap = 'OrRd',metric="euclidean",row_cluster = False,col_cluster = False,method = 'ward',figsize = (10,10),cbar_pos=(0.05, 0.2, 0.03, 0.4))
    fig.savefig(Output_Dir + r'\Corr_Matrix_Normal_Impute_Spearman.pdf')
    fig.savefig(Output_Dir + r'\Corr_Matrix_Normal_Impute_Spearman.jpg',dpi = 600)
    plt.close()
    Corr_Matrix = PlotData.corr(method = 'pearson')
    Corr_Matrix.to_csv(Output_Dir + r'\Corr_Matrix_Pearson.txt',sep = '\t')
    fig = sns.clustermap(Corr_Matrix,cmap = 'OrRd',metric="euclidean",row_cluster = False,col_cluster = False,method = 'ward',figsize = (10,10),cbar_pos=(0.05, 0.2, 0.03, 0.4))
    fig.savefig(Output_Dir + r'\Corr_Matrix_Normal_Impute_Pearson.pdf')
    fig.savefig(Output_Dir + r'\Corr_Matrix_Normal_Impute_Pearson.jpg',dpi = 600)
    plt.close()
    PlotData['Sum'] = PlotData.T.sum()
    PlotData = PlotData.sort_values(by = 'Sum',ascending = False)
    PlotData = PlotData.drop(columns = 'Sum')
    fig = sns.heatmap(PlotData,cmap = 'coolwarm',yticklabels = False)
    fig.set(ylabel = 'log2 (Intensity)')
    plt.figure(figsize = (8,8))
    heatmap = fig.get_figure()
    heatmap.savefig(Output_Dir + r'\Heatmap_Matrix_Normal_Impute.pdf',bbox_inches='tight')
    heatmap.savefig(Output_Dir + r'\Heatmap_Matrix_Normal_Impute.jpg',dpi = 600,bbox_inches='tight')
    plt.close()

'''
SoftWare = 'Matrix'
Work_Dir = r'I:\HuiYan_Project\P0035\Sample_86_250218\Sample\Input_Protein.csv'
Output_Dir = r'I:\HuiYan_Project\P0035\Sample_86_250218\Sample\Test'
Filter_Nu = 43
Normalize = 'Median'
Impute = 'KNN'
Jiangwei = 'PCA'
NameMapping = r'I:\HuiYan_Project\P0035\Sample_86_250218\Sample\Label.csv'
Header = 'Intensity'
Filter_Only_Identified_By_Site = 'True'
UniquePeptide = 1
ProbabilityMin = 0.99
Filter_Group = 0.7

RunMonitor(SoftWare,Work_Dir,Output_Dir,Filter_Nu,Normalize,Impute,Jiangwei,NameMapping,Header,Filter_Only_Identified_By_Site,UniquePeptide,ProbabilityMin,Filter_Group)
'''