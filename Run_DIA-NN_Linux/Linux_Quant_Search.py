import os
import sys

ParamFile = sys.argv[1]
Dir  = sys.argv[2]

for Line in open(ParamFile):
    if Line.startswith('Exe_Path'):
        Exe_Script = Line.split(':')[1].strip()
    if Line.startswith('Port'):
        Port = Line.split(':')[1].strip()
    if Line.startswith('Received_Dir'):
        Received_Dir = Line.split(':')[1].strip()
    if Line.startswith('Result_Dir'):
        Result_Dir = Line.split(':')[1].strip()
    if Line.startswith('Sample_Num'):
        Sample_Num = Line.split(':')[1].strip()
    if Line.startswith('Fasta'):
        Fasta = Line.split(':')[1].strip()
    if Line.startswith('ThermoRawFileParser_Path'):
        ThermoRawFileParser = Line.split(':')[1].strip()

Supp_Param = ' --fasta-search --min-fr-mz 200 --max-fr-mz 1800 --met-excision --cut K*,R* --missed-cleavages 2 --min-pep-len 7 --max-pep-len 30 --min-pr-mz 300 --max-pr-mz 1800 --min-pr-charge 1 --max-pr-charge 4 --unimod4 --var-mods 5 --var-mod UniMod:35,15.994915,M --var-mod UniMod:1,42.010565,*n --monitor-mod UniMod:1 --reanalyse --relaxed-prot-inf --smart-profiling --peak-center --no-ifs-removal --use-quant'

Output = open(os.path.join(Result_Dir,'DIA-NN_Quant_Search.sh'),'w')
Output.write(str(Exe_Script))
for Name in os.listdir(Dir):
    RawQuant = os.path.join(Dir,Name,Name + '.quant')
    DFile = os.path.join(Dir,Name,Name + '.d')
    if os.path.exists(RawQuant) or os.path.exists(DFile):
        if os.path.exists(RawQuant):
            DealFile = str(RawQuant).replace('.mzML.quant','.mzML')
        else:
            DealFile = DFile
        #print(DealFile)
        Output.write(' --f ' + DealFile)

ResultFile = os.path.join(Result_Dir,'Report.tsv')
LibFile = os.path.join(Result_Dir,'report-lib.tsv')
Output.write(' --lib '+ '""' + ' --threads 60 --verbose 1 --out ' + str(ResultFile) + ' --out-lib ' + str(LibFile) + ' --gen-spec-lib --qvalue 0.01 --matrices --predictor --fasta ' + str(Fasta) + str(Supp_Param))

Output.close()
