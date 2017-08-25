# NLRB Data Scraper (by LexPredict)
Software package for scraping data from the National Labor Relations Board.

* LexPredict: https://lexpredict.com/
* NLRB: https://nlrb.gov/

## Licensing
This software is freely available under the Apache License, Version 2.0.  LexPredict is proud to sponsor open source software in legal!

## Usage

### Installation
```
$ pip install https://github.com/LexPredict/nlrb_data/archive/master.zip
```

### Example
```
import datetime
import nlrb_data

# Get case list
case_list = nlrb_data.get_case_list(dates=(datetime.date(2010, 1, 1), datetime.date(2010, 2, 1)), company="Acme")
print(case_list[0])

# Iterate through results, retrieving detailed info
for case in case_list:
    case_info = nlrb_data.get_case(case["case_number"])
    print(case_info)
```

**Designed for use with pandas**:
```
import datetime
import nlrb_data
import pandas

case_list_df = pandas.DataFrame(nlrb_data.get_case_list(dates=(datetime.date(2010, 1, 1), datetime.date(2010, 2, 1))))
```
