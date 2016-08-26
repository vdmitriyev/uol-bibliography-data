@echo off
REM @author Viktor Dmitriyev
REM python uolbibliography_cleaner.py --input=generated/uolbibliography-merged.csv --output=uolbibliography-clean.csv
REM uolbibliography_cleaner.py --input=generated/uolbibliography-2008-2015-merged.csv --output=uolbibliography-2008-2015-merged-cleaned.csv
python uolbibliography_cleaner.py --input=generated/uolbibliography-2008-2015-merged.csv --output=uolbibliography-2008-2015-merged-cleaned-unique.csv
pause