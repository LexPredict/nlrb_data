"""NLRB data scraper.

This module contains methods for the retrieval of data from the National Labor Relations Board (NLRB) public
website.
"""

# Standard imports
import datetime
import pandas
import time
import urllib
import urllib.parse

# third-party package imports
import lxml.html
import requests

# Project imports
# https://www.nlrb.gov/search/cases?page=1&f[0]=date%3A01/01/2017%20to%2008/24/2017&retain-filters=1

BASE_URL = "https://www.nlrb.gov/search/cases"


def get_case_list_url(dates=None, company=None, page_number=None):
    """
    Get the case list URL for a search based on
    date and/or company name.
    :param dates:
    :param company:
    :param page_number:
    :return:
    """

    # Handle date case
    filter_number = 0
    url = "{base_url}/".format(base_url=BASE_URL)

    if company:
        url += urllib.parse.quote(company)

    # Add query separator
    url += "?"

    if dates:
        # Get date strings
        start_date = dates[0].strftime("%m/%d/%Y")
        end_date = dates[1].strftime("%m/%d/%Y")
        url += "&f[{filter_number}]=date%3A{start_date}%20to%20{end_date}".format(filter_number=filter_number,
                                                                                  start_date=start_date,
                                                                                  end_date=end_date)
        filter_number += 1

    if page_number:
        url += "&page={page_number}".format(page_number=page_number)

    return url


def get_page_count(url, session=None):
    """
    Get the page count from a given URL.
    :param url:
    :param session:
    :return:
    """
    # Create session if not provided
    if not session:
        s = requests.Session()

    # Execute query
    response = s.get(url)
    buffer = response.text
    time.sleep(1)

    # Find last "?page=" occurrence.
    pos0 = buffer.rfind("?page=")
    pos1 = buffer.find("&", pos0)
    page_number = int(buffer[(pos0 + 6):pos1])
    return page_number


def parse_case_list_li(li):
    """
    Parse a case list <li> item.
    :param li:
    :return:
    """
    # Setup a case result object
    case_result = dict()

    # Parse title and URL
    try:
        title_h3 = li.find_class("title").pop()
        case_result["title"] = lxml.html.tostring(title_h3, method="text", encoding="utf-8").decode("utf-8").strip()
        case_result["url"] = title_h3.xpath(".//a").pop().attrib["href"]
    except IndexError:
        case_result["title"] = None
        case_result["url"] = None

    # Parse case info inside snippet
    for label in li.xpath(".//span[contains(@class, 'label')]"):
        label_text = label.text.replace(":", "").replace(" ", "_").strip().lower()
        label_value = lxml.html.tostring(label.getparent(), method="text", encoding="utf-8").decode("utf-8") \
            .split(":", 1).pop().strip()
        case_result[label_text] = label_value

    return case_result


def parse_case_list(buffer):
    """
    Parse a case list document.
    :param buffer:
    :return:
    """
    # Setup return structure
    cases = []

    # Parse to document
    document = lxml.html.fromstring(buffer)
    for li in document.xpath("//li[contains(@class, 'search-result')]"):
        cases.append(parse_case_list_li(li))

    return cases


def get_case_list(dates=None, company=None):
    """
    Get the list of cases matching a given query
    on date or company.
    :param dates:
    :param company:
    :return:
    """

    # Setup return structure
    cases = []

    # Initial URL
    initial_url = get_case_list_url(dates, company, page_number=0)
    max_page_count = get_page_count(initial_url)

    # Iterate through all page requests
    with requests.Session() as s:
        for page_number in range(1, max_page_count + 1):
            # Get URL and response
            page_url = get_case_list_url(dates, company, page_number=page_number)
            response = s.get(page_url)

            # Parse result and sleep
            cases.extend(parse_case_list(response.text))
            time.sleep(1)

    # Return list of cases
    return cases

if __name__ == "__main__":
    print(get_case_list_url(dates=(datetime.date(2010, 1, 1),
                                   datetime.date(2010, 2, 1))))
    print(get_case_list_url(dates=(datetime.date(2010, 1, 1),
                                   datetime.date(2010, 2, 1)),
                            page_number=5))
    u = (get_case_list_url(company="Hospital", dates=(datetime.date(2017, 1, 1),
                                                      datetime.date(2017, 2, 1))))

    cases = get_case_list(company="Kaiser", dates=(datetime.date(2010, 1, 1),
                                                   datetime.date(2010, 2, 1)))
    print(cases)
    case_df = pandas.DataFrame(cases)
    print(case_df)
    print(case_df.shape)