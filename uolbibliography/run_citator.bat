@echo off
REM @author Viktor Dmitriyev
PATH = c:\Soft\Anaconda3\;%PATH%
python uolbibliography_citator.py --input=generated-2018/uolbibliography-2008-2017-merged-cleaned.csv
pause