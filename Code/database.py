import numpy as np
import pandas as pd
import get_data as gd
import re

def get_URLS_titles_database(total_pages, file_name = r'zeefdrukken_data.csv', url_start = 'https://www.kunstveiling.nl/veilingopbrengsten/lijst?technique=silkscreen&offset='):
    """
    Get URLS and titles van veiling opbrengsten starting on first page.

    Parameters
    ----------
    total_pages : int
        total amount of pages (starting from first page)
    file_name : str
        name of file to save to, has to be .csv file.
    url_start : str
        what the URL starts with, should end with 'offset='
    """
    for page_start in np.arange(1, total_pages, 10):
        end_page = page_start+9 # Every 10 pages save data
        if end_page > total_pages:
            end_page = total_pages
        titles, urls = gd.get_items_url(url_start, end_page, 12, past_yields=True, page_start = page_start)

        df = pd.DataFrame()

        df['Title'] = titles
        df['URL'] = urls
        print(len(df['Title']))
        df.set_index('URL', inplace=True)

        with open(file_name, 'a') as f:
            df.to_csv(f, header=f.tell()==0)

def get_data_info_database(data_path = r'../data/zeefdrukken_data.csv', start = 0, stop = False):
    """
    Get additional data of item range of data frame extracted from .csv file.

    Parameters
    ----------
    data_path : str
        path were data is stored.
    start : int
        where to start in the data (index).
    stop : int
        where to stop in data (index, exlusive). False for end.
    """
    items_df = pd.read_csv(data_path)
    items_df.set_index('URL', inplace=True)

    urls = items_df.index.to_numpy()
    if stop != False:
        urls = urls[start:stop]
    else:
        urls = urls[start::]

    for url in urls:
        full_url = 'https://www.kunstveiling.nl' + url
        item_keys, item_values = gd.get_item_info(full_url)

        items_df.loc[url, item_keys] = item_values
        # Adding rows: https://stackoverflow.com/questions/45327069/convert-numpy-array-to-pandas-dataframe-column-wise-as-single-row
        start = start + 1
    items_df.to_csv(data_path)

def clean_and_save_data(data_path = r'../data/zeefdrukken_data.csv'):
    df = pd.read_csv(data_path)

    df = gd.clean_data(df)

    new_path = data_path[:-4] + '_cleaned.csv'
    df.to_csv(new_path)
    pass

def main(off_set = 6900):
    for start_at in np.arange(4)*50+off_set:
        get_data_info(start = start_at, stop = start_at+50)
        print('item: ', start_at+50)

if __name__ == "__main__":
    clean_and_save_data()
