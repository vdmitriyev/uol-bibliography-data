### About

Fetching data related to the 'Hochschulbibliografie'(Universities Publication Bibliography) of UOL.

### Usage

Use command given below or provided 'run.bat' file.

```
python uolbibliography.py --urlfile=uolbibliography-test.txt --mergedata
```

Now you can also "clean" to some extend fetched data. Use command given below or provided 'run_cleaner.bat' file.
```
python uolbibliography_cleaner.py --input=generated/uolbibliography-merged.csv --output=uolbibliography-clean.csv
```

### Help
```
python uolbibliography.py --help
```

### Dependencies

Check 'requirements.txt' files for details or use following command to install dependencies.
```
pip install -r requirements.txt
```


#### Author

* Viktor Dmitriyev
