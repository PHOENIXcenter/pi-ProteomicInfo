import os
import sys

ParamFile = sys.argv[1]
Dir  = sys.argv[2]

print(Dir)
# 参数读入-可变参数
for Line in open(ParamFile):
    if Line.startswith('Received_Dir'):
        Received_Dir = Line.split(':')[1].strip()
    if Line.startswith('Result_Dir'):
        Result_Dir = Line.split(':')[1].strip()
    if Line.startswith('Sample_Num'):
        Sample_Num = Line.split(':')[1].strip()
    if Line.startswith('Fasta'):
        Fasta = Line.split(':')[1].strip()
        Fasta_Label = str(Fasta).split('/')[-1]

# 固定参数
Supp_Param = ' --fasta-search --min-fr-mz 200 --max-fr-mz 1800 --met-excision --cut K*,R* --missed-cleavages 2 --min-pep-len 7 --max-pep-len 30 --min-pr-mz 300 --max-pr-mz 1800 --min-pr-charge 1 --max-pr-charge 4 --unimod4 --var-mods 5 --var-mod UniMod:35,15.994915,M --var-mod UniMod:1,42.010565,*n --monitor-mod UniMod:1 --reanalyse --relaxed-prot-inf --smart-profiling --peak-center --no-ifs-removal --use-quant --no-norm'
Exe_Script = '/usr/diann/1.8.1/diann-1.8.1'
ResultFile = '/data/Report.tsv'
LibFile = '/data/report-lib.tsv'
Fasta = '/Fasta/' + Fasta_Label

Output = open(os.path.join(Result_Dir,'DIA-NN_Quant_Search.job'),'w')
Output.write('#!/bin/bash' + '\n')
Output.write('#SBATCH --job-name=All_Merge_Run_DIA-NN:' + str(Result_Dir) + '\n')
Output.write('#SBATCH -N 1' + '\n' + '#SBATCH -n 50' + '\n' + '#SBATCH -o ' + str(Result_Dir) + '/DIA-NN_Quant_Search_normal.log' + '\n' + '#SBATCH -e ' + str(Result_Dir) + '/DIA-NN_Quant_Search_error.log' + '\n')
Output.write('\n')

Output.write('docker run --cpus=50 -v ' + str(Received_Dir) + ':/data -v /public/home/chuanxi/Docker/Fasta:/Fasta run-diann ' + str(Exe_Script))
for Name in os.listdir(Dir):
    RawQuant = os.path.join(Dir,Name,Name + '.mzML.quant')
    DFile = os.path.join(Dir,Name,Name + '.d')
    if os.path.exists(RawQuant) or os.path.exists(DFile):
        if os.path.exists(RawQuant):
            DealFile = str(RawQuant).replace('.mzML.quant','.mzML')
            Output.write(' --f ' + os.path.join('/data',Name,Name + '.mzML'))
        else:
            Output.write(' --f ' + os.path.join('/data',Name,Name + '.d'))

#Output.write(' --lib '+ '""' + ' --threads 95 --verbose 1 --out ' + str(ResultFile) + ' --out-lib ' + str(LibFile) + ' --gen-spec-lib --qvalue 0.01 --matrices --predictor --fasta ' + str(Fasta) + str(Supp_Param))
Output.write(' --lib '+ '""' + ' --threads 95 --verbose 1 --out ' + str(ResultFile) + ' --out-lib ' + str(LibFile) + ' --gen-spec-lib --qvalue 0.01 --matrices --predictor --fasta ' + str(Fasta) + str(Supp_Param))
Output.close()

MergeScript = os.path.join(Result_Dir,'DIA-NN_Quant_Search.job')
os.system('sbatch '  + str(MergeScript))

