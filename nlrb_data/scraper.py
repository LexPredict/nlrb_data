"""NLRB data scraper.

This module contains methods for the retrieval of data from the National Labor Relations Board (NLRB) public
website.
"""

# Standard imports
import string
import time
import urllib
import urllib.parse

# third-party package imports
import dateutil.parser
import lxml.html
import pandas
import requests

# Project imports
# https://www.nlrb.gov/search/cases?page=1&f[0]=date%3A01/01/2017%20to%2008/24/2017&retain-filters=1

# Constants
BASE_SEARCH_URL = "https://www.nlrb.gov/search/cases"
BASE_URL = "https://www.nlrb.gov"
SLEEP_INTERVAL = 1


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
    url = "{base_url}/".format(base_url=BASE_SEARCH_URL)

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
        session = requests.Session()

    # Execute query
    response = session.get(url)
    buffer = response.text
    time.sleep(SLEEP_INTERVAL)

    # Find last "?page=" occurrence.
    pos0 = pos1 = buffer.rfind("?page=")
    if pos0 == -1:
        return 1
    else:
        pos0 += 6
        pos1 = pos0

    next_char = buffer[pos1]
    while next_char in string.digits:
        pos1 += 1
        next_char = buffer[pos1]

    page_number = int(buffer[pos0:pos1])
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
    title_h3 = li.find_class("title").pop()
    case_result["title"] = lxml.html.tostring(title_h3, method="text", encoding="utf-8").decode("utf-8").strip()
    case_result["url"] = title_h3.xpath(".//a").pop().attrib["href"]

    # Parse case info inside snippet
    for label in li.xpath(".//span[contains(@class, 'label')]"):
        # Get label text
        label_text = label.text.replace(":", "").replace(" ", "_").strip().lower()

        # Get label value and clean
        label_value = lxml.html.tostring(label.getparent(), method="text", encoding="utf-8").decode("utf-8") \
            .split(":", 1).pop().strip()
        case_result[label_text] = label_value

    # Augment status fields
    if "status" in case_result:
        # Set status type and date
        pos0 = case_result["status"].rfind(" on ")
        if pos0 > 0:
            case_result["status_type"] = case_result["status"][0:pos0].strip()
            case_result["status_date"] = dateutil.parser.parse(case_result["status"][(pos0 + 4):]).date()

    # Augment region fields
    if "region_assigned" in case_result:
        # Parse region separately
        pos0 = case_result["region_assigned"].find(",")
        case_result["region_number"] = case_result["region_assigned"][0:pos0].strip()
        case_result["region_city"] = case_result["region_assigned"][(pos0 + 1):].strip()

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


def get_case_list(dates=None, company=None, session=None):
    """
    Get the list of cases matching a given query
    on date or company.
    :param dates:
    :param company:
    :return:
    """

    # Create session if not provided
    if not session:
        session = requests.Session()

    # Setup return structure
    cases = []

    # Initial URL
    initial_url = get_case_list_url(dates, company, page_number=0)
    max_page_count = get_page_count(initial_url)

    # Iterate through all page requests
    for page_number in range(0, max_page_count):
        # Get URL and response
        page_url = get_case_list_url(dates, company, page_number=page_number)
        response = session.get(page_url)

        # Parse result and sleep
        cases.extend(parse_case_list(response.text))
        time.sleep(SLEEP_INTERVAL)

    # Return list of cases
    return cases


def get_docket_data(document):
    """
    Parse an lxml document for docket activity and return a dataframe.
    :param document:
    :return:
    """
    # Find docket element
    case_docket_table = document.find_class("view-docket-activity").pop()

    # Parse with pandas or return empty
    try:
        case_docket_df = pandas.read_html(lxml.html.tostring(case_docket_table)).pop()
    except ValueError:
        case_docket_df = pandas.DataFrame()

    return case_docket_df


def get_allegation_data(document):
    """
    Parse an lxml document for allegations and return a list.
    :param document:
    :return:
    """

    # Setup return structure
    allegation_list = []

    try:
        # Find element and parse <li>s
        allegation_div = document.find_class("view-allegations").pop()
        for li in allegation_div.find_class("field-content"):
            allegation_list.append(li.text)
    except IndexError:
        pass

    return allegation_list


def get_party_data(document):
    """
    Parse an lxml document for participants data and return a dataframe.
    :param document:
    :return:
    """
    # Find the HTML element
    try:
        case_party_table = document.find_class("view-participants").pop()
    except IndexError:
        return pandas.DataFrame()

    try:
        # Get table header
        table_header = case_party_table.xpath(".//thead").pop()
        table_header_columns = [lxml.html.tostring(th, method="text", encoding="utf-8").strip().decode("utf-8")
                                for th in table_header.xpath(".//th")]

        # Get table rows
        table_data = []
        for tr in case_party_table.xpath(".//tr")[1:]:
            row = {}
            i = 0
            for td in tr.xpath(".//td"):
                td_text = lxml.html.tostring(td, method="text", encoding="utf-8").strip().decode("utf-8")

                # Handle field types
                if table_header_columns[i] == "Participant":
                    # Parse participant types
                    td_lines = [line.strip() for line in td_text.splitlines()]
                    if len(td_lines) == 3:
                        row["party_role"] = td_lines[0]
                        row["party_type"] = td_lines[1]
                        row["party_name"] = td_lines[2]
                    elif len(td_lines) == 4:
                        row["party_role"] = td_lines[0]
                        row["party_type"] = td_lines[1]
                        row["party_name"] = td_lines[2]
                        row["party_firm"] = td_lines[3]
                    elif len(td_lines) > 1:
                        row["party_role"] = td_lines[0]
                        row["party_name"] = "\n".join(td_lines[1:])
                    else:
                        pass
                elif table_header_columns[i] == "Address":
                    row["party_address"] = td_text
                elif table_header_columns[i] == "Phone":
                    row["party_phone"] = td_text

                i += 1

            table_data.append(row)

        return pandas.DataFrame(table_data)
    except ValueError:
        return pandas.DataFrame()


def get_election_data(document):
    """
    Parse lxml document for election data and return dataframe.
    :param document:
    :return:
    """
    try:
        election_div = document.find_class("view-elections").pop()
        election_rows = []
        for row_div in election_div.find_class("views-row"):
            row = {}
            for field_div in row_div.find_class("views-field"):
                if len(field_div.getchildren()) == 1:
                    continue
                field_label = lxml.html.tostring(field_div.xpath(".//div")[0], method="text",
                                                 encoding="utf-8").strip().decode("utf-8")
                field_label = field_label.strip(":").replace(" ", "_").lower()
                field_value = lxml.html.tostring(field_div.xpath(".//div")[1], method="text",
                                                 encoding="utf-8").strip().decode("utf-8")
                row[field_label] = field_value

            if len(row) > 0:
                election_rows.append(row)

        election_data = pandas.DataFrame(election_rows)
    except IndexError:
        election_data = pandas.DataFrame()

    return election_data


def get_case(case_id, session=None):
    """
    Get case data from a case ID.
    :param case_id:
    :param session:
    :return:
    """
    # Create session if not provided
    if not session:
        session = requests.Session()

    # Get case URL and parse response
    case_url = "{base_url}/case/{case_id}".format(base_url=BASE_URL, case_id=case_id)
    response = session.get(case_url)
    document = lxml.html.fromstring(response.text)

    # Get case fields
    case_number_span = document.find_class("views-label-case").pop()
    case_number = case_number_span.getnext().text

    case_city_span = document.find_class("views-label-city").pop()
    case_city = case_city_span.getnext().text

    case_date_filed_span = document.find_class("views-label-date-filed").pop()
    case_date_filed = case_date_filed_span.getnext().text

    case_region_span = document.find_class("views-label-dispute-region").pop()
    case_region = case_region_span.getnext().text

    case_status_span = document.find_class("views-label-status").pop()
    case_status = case_status_span.getnext().text

    try:
        case_close_span = document.find_class("views-label-close-method").pop()
        case_close = case_close_span.getnext().text
    except IndexError:
        case_close = None

    # Parse docket table with pandas
    case_docket_df = get_docket_data(document)

    # Parse allegation list
    allegation_list = get_allegation_data(document)

    # Parse election block if present
    election_data = get_election_data(document)

    # Parse participant list
    case_party_df = get_party_data(document)

    # Create return dictionary
    return {"case_number": case_number,
            "city": case_city,
            "date_filed": case_date_filed,
            "elections": election_data,
            "region": case_region,
            "status": case_status,
            "close_reason": case_close,
            "docket": case_docket_df,
            "allegations": allegation_list,
            "participants": case_party_df}
