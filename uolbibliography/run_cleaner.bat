@echo off
REM @author Viktor Dmitriyev
call D:\tmp\python\globvenv\Scripts\activate.bat
REM python uolbibliography_cleaner.py --input=generated/uolbibliography-merged.csv --output=uolbibliography-clean.csv
REM python  uolbibliography_cleaner.py --input=generated/uolbibliography-2008-2015-merged.csv --output=uolbibliography-2008-2015-merged-cleaned.csv
REM python uolbibliography_cleaner.py --input=generated/uolbibliography-2008-2016-merged.csv --output=uolbibliography-2008-2016-merged-cleaned.csv
REM python uolbibliography_cleaner.py --input="generated/uol-bibliography-data-2008-2015-v3/raw/Hochschulbibliografie 2009-2011 Fakultt 2 - Informatik Wirtschafts- und Rechtswissenschaften Department fr Informatik.csv" --output=uolbibliography-2009-2011-merged-cleaned-informatik.csv
python uolbibliography_cleaner.py --input=generated-2018/uolbibliography-2008-2017-merged.csv --output=uolbibliography-2008-2017-merged-cleaned.csv
pause