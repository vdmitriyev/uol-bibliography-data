### About

Crawling, cleaning and visualizing data related to the 'Hochschulbibliografie'(University Publication Bibliography) of UOL.

### Usage

Use command given below or provided 'run_crawler.bat' file.

```
python uolbibliography.py --urlfile=uolbibliography-test.txt --mergedata
```

Now you can also "clean" to some extend fetched data. Use command given below or provided 'run_cleaner.bat' file.
```
python uolbibliography_cleaner.py --input=generated/uolbibliography-merged.csv --output=uolbibliography-clean.csv
```

### Help

* Crawl
```
python uolbibliography.py --help
```
* Clean
```
python uolbibliography_cleaner.py --help
```
* Visualize
```
python uolbibliography_plotter.py --help
```

### Dependencies

Check 'requirements.txt' files for details or use following command to install dependencies.
```
pip install -r requirements.txt
```


#### Author

* Viktor Dmitriyev

