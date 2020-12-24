from requests_html import AsyncHTMLSession, HTMLSession
from bs4 import BeautifulSoup

import numpy as np
import pandas as pd
import re
import math
import time
import asyncio

def get_items_url(URL, end_page, items_per_page, past_yields = False, page_start = 1):
    """
    Retreives the URLs from all the items of every page.

    Parameters
    ----------
    URL : str
        URL of the first page. Should end with "&offset=".
    end_page : int
        The total number of pages required.
    items_per_page : int
        Number of items per page.
    past_yields : boolean
        True if pages with past yields. False if current offers.
    page_start : int
        On what page to start.

    Returns
    -------
    item_urls : str
        array of strings with the url to every item.
    titles : str
        array of string with the title of every item.
    """
    offset = (np.arange(end_page-(page_start-1))+page_start-1)*items_per_page
    titles = []
    item_urls = []

    page_URLs = []
    for page_number in offset:
        page_URLs.append(URL + str(page_number))

    session = HTMLSession()
    page = page_start
    for URL in page_URLs:
        items_page = session.get(URL)

        # Render JavaScript
        items_page.html.render(sleep = 1) # Als deze niet werkt naar de Python(3) folder gaan en install certificates command runnen

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
    Retreives all the data of the specified item.

    Parameters
    ----------
    item_url : str
        String of the URL to specified item.

    Returns
    -------
    info_label_key : str
        numpy array of type of value.
    info_label_value : str
        numpy array with the values. Index corresponding to info_label_key.
    """
    info_label_key = np.array(['Artist', 'Price', 'Date'])
    info_label_value = np.array([None, None, None])
    with HTMLSession() as session:
        item_page = session.get(item_url)

        # Render JavaScript
        item_page.html.render(timeout = 0, sleep=4)
        soup = BeautifulSoup(item_page.html.html, 'html.parser')

        # Extra render time
        if soup.find('item-artist-name') == None:
            print('Extra render')
            item_page.html.render(timeout = 0, sleep=8)
            soup = BeautifulSoup(item_page.html.html, 'html.parser')

        #item_page.html.browser.quit()
        #item_page.session.quit()
        #item_page.quit()
        #time.sleep(1)
        # Maybe sleep here
        # https://github.com/psf/requests-html/issues/321

    # Extract artist
    try:
        artist = soup.find('item-artist-name').find('a').text
        info_label_value[0] = artist
    except:
        print('Not rendered properly')

    # Extract price and date
    try:
        bid_column = soup.find('div', class_='bid-column')
        price = bid_column.find(text=re.compile('€'))
        price = float(re.findall(r'\b\d+\b', price)[0])
        info_label_value[1] = price
        date = bid_column.find(text=re.compile('om'))
        info_label_value[2] = date
    except:
        print('Bid column not properly rendered')

    try:
        # Extracting additional info
        info_table = soup.find('info-table')
        info_table_content = info_table.find_all('tr')
        info_label_key = np.append(info_label_key, [label.find(class_='key').text for label in info_table_content])
        info_label_value = np.append(info_label_value, [label.find(class_='value').text for label in info_table_content])
    except:
        print('Info table not properly rendered')

    return info_label_key, info_label_value

def clean_data(df):
    def get_sizes(size):
        if type(size) == str:
            dimensions = re.findall(r'[+-]?\d*\.\d+|\d+', size)
            height = float(dimensions[0])
            width = float(dimensions[1])
            # print('Height: ', height, '    Width: ', width, '    Datatypes: ', type(height), '  ', type(width))
            return np.array([height, width])
        else:
            return np.array([None, None])

    def get_artist_year(value):
        if type(value) == str:
            words = re.findall(r'(\w[ \w]+\w+)', value)
            name = words[0]
            try:
                birth = int(words[1])
            except:
                birth = None
            try:
                death = int(words[2])
            except:
                death = None
        else:
            name = None
            birth = None
            death = None
        return name, birth, death

    def get_title(value):
        title = re.findall(r'(?<=- )[\.\w:'' ,\+()]+(?<=-)?', value)
        try:
            return title[0].lower()
        except:
            return None

    # Check of ingelijst
    df['Ingelijst'] = df['Ingelijst'].apply(lambda x : 1 if x == 'Ingelijst' else 0)
    # Afmetingen
    df[['Hoogte', 'Breedte']] = pd.DataFrame(df['Afmetingen'].apply(get_sizes).iloc[:].to_list(), index=df.index)
    # Jaartal
    df['Jaartal'] = pd.to_numeric(df['Jaartal'])
    # Naam, geboorte en dood schilder schilder
    df[['Artist', 'Birth', 'Death']] = pd.DataFrame(df['Artist'].apply(get_artist_year).to_list(), index=df.index)
    # Title schilderij
    df[['Title']] = df['Title'].apply(get_title)

    # Add extra features
    df['Area'] = df['Hoogte']*df['Breedte']
    return df

def get_current_offer(url_start = 'https://www.kunstveiling.nl/items?technique=silkscreen&offset='):
    titles, urls = get_items_url(url_start, 1, 50, past_yields=False, page_start = 1)

    df = pd.DataFrame()
    df['Title'] = titles[:20]
    df['URL'] = urls[:20]
    df.set_index('URL', inplace=True)

    urls = df.index.to_numpy()

    for url in urls:
        full_url = 'https://www.kunstveiling.nl' + url
        item_keys, item_values = get_item_info(full_url)

        df.loc[url, item_keys] = item_values

    df = clean_data(df)
    return df

"""
# Test get_items_url
zeefdruk_url = 'https://www.kunstveiling.nl/veilingopbrengsten/lijst?technique=silkscreen&offset='
nieuw_binnen_url = 'https://www.kunstveiling.nl/items?sort=startdate,d&select=first&offset='
titles, urls = get_items_url(zeefdruk_url, 3, 12, True)
print(titles)
print(urls)
"""

"""
# Test get_item_info
test_item = "https://www.kunstveiling.nl/items/eduardo-paolozzi-lots-of-pictures-lots-of-fun/321631"
test_item_sold = "https://www.kunstveiling.nl/items/vera-tummers-van-hasselt-brons-sculptuur-gesigneerd-mariken-van-nieumeghenmariken-van-nimwegen/316675"
get_item_info(test_item)
"""
