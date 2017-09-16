"""Scraper unit test coverage
"""

# Project imports
import datetime
import time

from nose.tools import assert_equal

from nlrb_data.scraper import get_case_list_url, get_page_count, get_case_list, get_case, SLEEP_INTERVAL


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


def test_get_case():
    """
    Test case detail on real queries.
    :return:
    """
    # Check single page result
    case_info = get_case("01-CA-104714")
    assert_equal(case_info["docket"].shape[0], 4)
    assert_equal(case_info["participants"].shape[0], 3)
    assert_equal(case_info["city"], "MEDFIELD, MA")


def test_scrape():
    """
    Test realistic scrape across company/date.
    :return:
    """
    # Get case list
    case_list = get_case_list(dates=(datetime.date(2010, 1, 1), datetime.date(2010, 2, 1)), company="Acme")
    assert_equal(len(case_list), 5)
    for case in case_list:
        case_info = get_case(case["case_number"])
        time.sleep(SLEEP_INTERVAL)

    assert_equal(case_info["participants"].shape[0], 3)


def test_get_case_no_docket():
    """
    Test case detail without docket info.
    :return:
    """
    case_info = get_case("21-CA-037931")
    assert_equal(case_info["docket"].shape[0], 0)


def test_get_case_no_allegations():
    """
    Test case detail without allegation info.
    :return:
    """
    case_info = get_case("02-RC-023360")
    assert_equal(len(case_info["allegations"]), 0)


def test_get_case_elections():
    """
    Test case detail with election data.
    :return:
    """
    case_info = get_case("01-RC-186442")
    assert_equal(case_info["elections"].shape[0], 5)


def test_get_case_no_elections():
    """
    Test case detail with election data.
    :return:
    """
    case_info = get_case("21-CA-037931")
    assert_equal(case_info["elections"].shape[0], 0)


def test_error_case_2():
    """
    Test observed error case.
    :return:
    """
    case_info = get_case("29-CA-014566")