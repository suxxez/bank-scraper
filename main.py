import logging
import re
import time
from urllib.parse import urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup
from search_engine_parser.core.engines.yahoo import Search as YahooSearch
from search_engine_parser.core.engines.google import Search as GoogleSearch
from search_engine_parser.core.exceptions import NoResultsOrTrafficError
from nordvpn_switcher import initialize_VPN, rotate_VPN, terminate_VPN

import regex


def get_url_from_search(search_term):
    logging.info(f"Searching for {search_term}")

    search_args = (search_term, 1)
    results = perform_search(search_args)
    url = results[0]["links"]

    logging.info(f"Found URL {url}")
    return url


def perform_search(search_args):
    try:
        g_search = GoogleSearch()
        return g_search.search(*search_args, url="google.de")
    except NoResultsOrTrafficError:
        pass

    try:
        y_search = YahooSearch()
        return y_search.search(*search_args, url="yahoo.de")
    except NoResultsOrTrafficError:
        raise_not_found_exception(f"{search_args} not found on Google nor Yahoo")


def get_website(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    return soup


def find_url_by_key(base_url, site, key):
    for link in site.find_all("a"):
        if key in link.text:
            url = link.get("href")

            logging.info(f"Found site for {key} at {url}")

            if url.startswith("/"):
                url = f"https://{urlparse(base_url).netloc}{url}"
                logging.debug(f"Converted relative URL to {url}")

            return url
    raise_not_found_exception(f"No url for {key} found on {base_url}")


def get_email(site):
    text = site.get_text()
    emails = re.findall(pattern=regex.email, string=str(text))

    logging.info(f"Found emails {emails}")
    return emails[0]


def get_address(site):
    text = site.get_text()
    street = re.search(pattern=regex.street, string=str(text)).group(0)
    city = re.search(pattern=regex.city, string=str(text)).group(0)

    if not (street and city):
        raise_not_found_exception("Street or city not found")

    logging.info(f"Found address {street} {city}")
    return street, city


def get_banks():
    return pd.read_excel(
        "Bankenliste Deutschland_no_QS.xlsx", header=2, usecols="B", engine="openpyxl"
    ).squeeze("columns")


class NotFoundException(Exception):
    """Raise when something has not been found on the website"""


def raise_not_found_exception(error_msg):
    logging.error(error_msg)
    raise NotFoundException(error_msg)


def switch_vpn(settings):
    logging.debug("switching vpn")
    rotate_VPN(settings, google_check=1)


def log_progress(current, total, start_time):
    logging.info(f"-------- PROGRESS: {current}/{total} --------")
    logging.info(f"-------- TIME ELAPSED: {time.time() - start_time}s --------")


def main():
    logging.basicConfig(level=logging.INFO)

    settings = initialize_VPN(save=1, area_input=["germany"])

    banks = get_banks()
    banks_df = pd.DataFrame(columns=["name", "url", "email", "street", "city"])

    start_time = time.time()

    for index, bank in enumerate(banks):
        if index % 8 == 0:
            log_progress(index, banks.size, start_time)
            switch_vpn(settings)

        try:
            base_url = get_url_from_search(f"{bank} deutschland")
            homepage = get_website(base_url)
        except NotFoundException:
            banks_df.loc[index] = [bank, "", "", "", ""]
            continue

        try:
            impressum_url = find_url_by_key(base_url, homepage, key="Impressum")
            impressum = get_website(impressum_url)
            email = get_email(impressum)
            street, city = get_address(impressum)

            banks_df.loc[index] = [bank, base_url, email, street, city]
        except NotFoundException:
            banks_df.loc[index] = [bank, base_url, "", "", ""]

        if index == 4:
            break

    terminate_VPN(settings)

    banks_df.to_excel("banks.xlsx")
    logging.info("DONE - saved entries to excel")


if __name__ == "__main__":
    main()
