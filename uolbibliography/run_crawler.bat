@echo off
REM @author Viktor Dmitriyev
call D:\tmp\python\globvenv\Scripts\activate.bat
REM python uolbibliography.py --urlfile=uolbibliography-test.txt --mergedata
python uolbibliography.py --urlfile=uolbibliography-full.txt --mergedata
pause