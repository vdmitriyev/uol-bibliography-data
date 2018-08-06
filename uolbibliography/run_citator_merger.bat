@echo off
REM @author Viktor Dmitriyev
call D:\tmp\python\globvenv\Scripts\activate.bat
REM PATH = c:\Soft\Anaconda3\;%PATH%
REM SET PATH=C:\Soft\Anaconda3;C:\Soft\Anaconda3\Scripts;C:\Soft\Anaconda3\Library\bin;%PATH%
REM conda create -n tests python=3.6 
REM call activate tests
python uolbibliography_citator.py --input=generated-2018/uolbibliography-2008-2017-merged-cleaned.csv --action=MERGE
pause