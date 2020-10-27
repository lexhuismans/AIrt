import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup

import numpy as np
import re
import math

number_of_items = 6899
number_of_pages = 571
offset = np.arange(number_of_pages)*12

titles = []
hrefs = []

zeefdruk_pages_URLs = []
for page_number in offset:
    zeefdruk_pages_URLs.append('https://www.kunstveiling.nl/veilingopbrengsten/lijst?technique=silkscreen&offset=' + str(page_number))

session = HTMLSession()
page = 0
for zeefdruk_page_URL in zeefdruk_pages_URLs:
    zeefdruk_pages = session.get(zeefdruk_page_URL)

    # Render JavaScript
    zeefdruk_pages.html.render() # Als deze niet werkt naar de Python(3) folder gaan en install certificates command runnen

    soup = BeautifulSoup(zeefdruk_pages.html.html, 'html.parser')

    # Vind alle items
    # class='row ng-star-inserted' has all the items
    # All items have id=item#
    items = soup.find_all('li', id=re.compile('^item'))

    # Extract title and link from page
    for item in items:
        title = item.find('h3').find('a', href=True)
        title_text = title.text
        titles.append(title_text)

        href = title['href']
        hrefs.append(href)
    print(page)
    page = page+1
