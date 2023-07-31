# CdiscountScrapper

A simple web scrapper that fetches queries products from [www.cdiscount.com](https://www.cdiscount.com) and then stores them to csv files through a pandas dataframe.

Setup environment:
```
$ conda env create --name envname --file=environments.yml
```

Usage
```
$ python cdiscount_scrapper.py <search_terms> <max_pages> (optional) <headless> (optional) <fake_user_agent> (optional) <proxy_list> (optional)
```