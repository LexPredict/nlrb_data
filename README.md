[![Build Status](https://travis-ci.org/LexPredict/nlrb_data.svg?branch=master)](https://travis-ci.org/LexPredict/nlrb_data) [![Coverage Status](https://coveralls.io/repos/github/LexPredict/nlrb_data/badge.svg?branch=master)](https://coveralls.io/github/LexPredict/nlrb_data?branch=master)

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
from nlrb_data.scraper import get_case_list, get_case

# Get case list
case_list = get_case_list(dates=(datetime.date(2010, 1, 1), datetime.date(2010, 2, 1)), company="Acme")
print(case_list[0])

# Iterate through results, retrieving detailed info
for case in case_list:
    case_info = get_case(case["case_number"])
    print(case_info)
```

**Designed for use with pandas**:
```
import datetime
import pandas
from nlrb_data.scraper import get_case_list

case_list_df = pandas.DataFrame(get_case_list(dates=(datetime.date(2010, 1, 1), datetime.date(2010, 2, 1))))
```

**Example Result**:
```
>>> from nlrb_data.scraper import get_case_list
>>> get_case("01-CA-104714")
{'docket':          Date                              Document Issued/Filed By
0  06/13/2013  Letter Approving Withdrawal Request*       NLRB - GC
1  05/13/2013     Initial Letter to Charging Party*       NLRB - GC
2  05/13/2013      Initial Letter to Charged Party*       NLRB - GC
3  05/08/2013       Signed Charge Against Employer*  Charging Party, 
'allegations': 
  ['8(a)(1) Weingarten'],
'status': 'Closed on 06/11/2013',
'case_number': '01-CA-104714',
'date_filed': '05/08/2013',
'region': 'Region 01, Boston, Massachusetts',
'city': 'MEDFIELD, MA',
'close_reason': 'Withdrawal Adjusted',
'participants':                                          Participant  \
0  Charged Party / Respondent Employer  ACE & ACM...
1  Charging Party Additional Service  Internation...
2  Charging Party Union  INTERNATIONAL BROTHERHOO...

                     Address  Phone
0    Medfield, MA 02052-1528    NaN
1  Washington, DC 20001-2130    NaN
2      BOSTON, MA 02129-1109    NaN  }
```
