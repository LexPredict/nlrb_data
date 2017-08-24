"""Scraper unit test coverage
"""

# Project imports
import datetime

from nose.tools import assert_equal

from nlrb_data.scraper import get_case_list_url, get_page_count, get_case_list


def test_case_list_url():
    """
    Test basic case list URL.
    :return:
    """
    # Test a variety of simple cases
    assert_equal(get_case_list_url(company="Acme"),
                 "https://www.nlrb.gov/search/cases/Acme?")

    assert_equal(get_case_list_url(company="Acme", page_number=2),
                 "https://www.nlrb.gov/search/cases/Acme?&page=2")

    assert_equal(get_case_list_url(dates=(datetime.date(2010, 1, 1),
                                          datetime.date(2010, 2, 1))),
                 "https://www.nlrb.gov/search/cases/?&f[0]=date%3A01/01/2010%20to%2002/01/2010")

    assert_equal(get_case_list_url(company="Acme", dates=(datetime.date(2010, 1, 1),
                                                          datetime.date(2010, 2, 1))),
                 "https://www.nlrb.gov/search/cases/Acme?&f[0]=date%3A01/01/2010%20to%2002/01/2010")


def test_get_page_count():
    """
    Test page count for real queries.
    :return:
    """
    # Check single page result
    url = get_case_list_url(company="Acme", dates=(datetime.date(2010, 1, 1),
                                                   datetime.date(2010, 2, 1)))
    assert_equal(get_page_count(url), 1)

    # Check real page result
    url = get_case_list_url(company="Services", dates=(datetime.date(2010, 1, 1),
                                                       datetime.date(2010, 2, 1)))
    assert_equal(get_page_count(url), 86)


def test_get_case_list():
    """
    Test page count for real queries.
    :return:
    """
    # Check single page result
    case_list = get_case_list(company="Acme", dates=(datetime.date(2010, 1, 1),
                                                     datetime.date(2010, 1, 20)))
    assert_equal(len(case_list), 2)

    # Check real page result
    assert_equal(case_list[0]["title"], "ACME Markets")
