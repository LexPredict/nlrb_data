# NLRB Data Scraper (by LexPredict)
Software package for scraping data from the National Labor Relations Board.

* LexPredict: https://lexpredict.com/
* NLRB: https://nlrb.gov/
* Contact: contact@lexpredict.com

![Logo](https://www.lexpredict.com/wp-content/uploads/2014/08/lexpredict_logo_horizontal_1.png)

## Licensing
This software is freely available under the Apache License, Version 2.0.  LexPredict is proud to sponsor open source software in legal!

## Usage
### Installation
```
$ git clone https://github.com/LexPredict/nlrb_data.git
$ cd nlrb_data
$ pip install -e .
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

