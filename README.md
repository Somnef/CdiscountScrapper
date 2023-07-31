# CdiscountScrapper

A simple web scrapper that fetches queries products from [www.cdiscount.com](https://www.cdiscount.com) and then stores them to csv files through a pandas dataframe.

<u>Setup environment:</u>
```
$ conda env create --name envname --file=environments.yml
```

<u>Usage:</u>
```
$ python cdiscount_scrapper.py <search_terms> <max_pages> (optional) <headless> (optional) <fake_user_agent> (optional) <proxy_list> (optional)
```

<u>Output:</u> </br>CSV files sorted in corresponding directories under ```./cdiscount/ ``` folder.

<u>NOTE:</u> Also requires ChromeDriver to be in ```PATH```.