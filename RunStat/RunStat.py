import os
import sys
import SP_DataDeal_IRT,MQ_DataDeal_IRT,PD_DataDeal_NoIRT,MS_DataDeal_NoIRT

InputFile = sys.argv[1]
Output = sys.argv[2]
IRT_Add = sys.argv[3] 
Label = sys.argv[4]
QC = sys.argv[5]
Name = sys.argv[6]

if Label == 'SP':
    NameLabel = SP_DataDeal_IRT.SP_Extract(InputFile,Output,IRT_Add,QC)
elif Label == 'MQ':
    NameLabel = MQ_DataDeal_IRT.MQ_Extract(InputFile,Output,IRT_Add,QC)
elif Label == 'PD':
    NameLabel = PD_DataDeal_NoIRT.PD_Extract(InputFile,str(Name),Output,QC)
elif Label == 'MS':
    NameLabel = MS_DataDeal_NoIRT.PD_Extract(InputFile,Output)


