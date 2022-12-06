import logging
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup
from search_engine_parser.core.engines.yahoo import Search as YahooSearch
from search_engine_parser.core.engines.google import Search as GoogleSearch

from urllib.parse import urlparse

import regex


def get_url_from_search(search_term):
    search_args = (search_term, 1)
    gsearch = GoogleSearch()
    gresults = gsearch.search(*search_args, url="google.de")
    #ysearch = YahooSearch()
    #yresults = ysearch.search(*search_args, url="yahoo.de")

    url = gresults[0]['links']

    logging.info(f"Found URL {url}")
    return url


def get_website(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    return soup


def find_url_by_key(base_url, site, keys):
    for link in site.find_all('a'):
        for key in keys:
            if key in link.text:
                url = link.get('href')

                logging.info(f"Found site for {key} at {url}")

                if url.startswith("/"):
                    url = f"https://{urlparse(base_url).netloc}{url}"
                    logging.debug(f"Converted relative URL to {url}")

                return url


def get_email(site):
    text = site.get_text()
    emails = re.findall(pattern=regex.email, string=str(text))

    logging.info(f"Found emails {emails}")
    return emails[0]


def get_address(site):
    text = site.get_text()
    street = re.search(pattern=regex.street, string=str(text)).group(0)
    city = re.search(pattern=regex.city, string=str(text)).group(0)

    logging.info(f"Found address {street} {city}")
    return street, city


def get_banks():
    return pd.read_excel("Bankenliste Deutschland_no_QS.xlsx", header=2, usecols="B").squeeze("columns")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    banks = get_banks()
    banks_df = pd.DataFrame(columns = ['name','url','email', 'street', 'city'])

    for index, bank in enumerate(banks):
        logging.info(f"Searching for {bank}")

        base_url = get_url_from_search(f"{bank} deutschland")
        homepage = get_website(base_url)
        impressum_url = find_url_by_key(base_url, homepage, keys=["Impressum", "Imprint"])

        if impressum_url is None:
            banks_df.loc[index] = [bank, base_url, "", "", ""]
        else:
            impressum = get_website(impressum_url)
            email = get_email(impressum)
            street, city = get_address(impressum)

            banks_df.loc[index] = [bank, base_url, email, street, city]

        if index == 1:
            break

    banks_df.to_excel("banks.xlsx")
