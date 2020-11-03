import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup

import numpy as np
import re
import math

def get_items_url(URL, number_of_pages, items_per_page, past_yields = False):
    """
    Retreives the URLs from all the items of every page.

    Parameters
    ----------
    URL : str
        URL of the first page. Should end with "&offset=".
    number_of_pages : int
        The total number of pages required.
    items_per_page : int
        Number of items per page.
    past_yields : boolean
        True if pages with past yields. False if current offers. 

    Returns
    -------
    item_urls : str
        array of strings with the url to every item.
    titles : str
        array of string with the title of every item.
    """
    number_of_items = 6899
    offset = np.arange(number_of_pages)*items_per_page

    titles = []
    item_urls = []

    page_URLs = []
    for page_number in offset:
        page_URLs.append(URL + str(page_number))

    session = HTMLSession()
    page = 0
    for URL in page_URLs:
        items_page = session.get(URL)

        # Render JavaScript
        items_page.html.render() # Als deze niet werkt naar de Python(3) folder gaan en install certificates command runnen

        soup = BeautifulSoup(items_page.html.html, 'html.parser')

        # Vind alle items
        # All items have id=item#
        items = soup.find_all(id=re.compile('^item'))

        # Extract title and link of item
        for item in items:
            if past_yields:
                title = item.find('h3').find('a', href=True)
            else:
                title = item.find('h2').find('a', href=True)
            title_text = title.text
            titles.append(title_text)

            href = title['href']
            item_urls.append(href)
        print(page)
        page = page+1

    return np.array(titles), np.array(item_urls)

def get_item_info(item_url):
    """
    Retreives all the data of the specified item

    Parameters
    ----------
    item_url : string
        String of the URL to specified item

    Returns
    -------

    """
    session = HTMLSession()

    item_page = session.get(item_url)

    # Render JavaScript
    item_page.html.render(sleep=1)

    soup = BeautifulSoup(item_page.html.html, 'html.parser')

    info_table = soup.find('info-table')
    print(info_table)

"""
zeefdruk_url = 'https://www.kunstveiling.nl/veilingopbrengsten/lijst?technique=silkscreen&offset='
nieuw_binnen_url = 'https://www.kunstveiling.nl/items?sort=startdate,d&select=first&offset='
titles, urls = get_items_url(zeefdruk_url, 3, 12, True)
print(titles)
print(urls)
"""

test_item = "https://www.kunstveiling.nl/items/eduardo-paolozzi-lots-of-pictures-lots-of-fun/321631"
get_item_info(test_item)
