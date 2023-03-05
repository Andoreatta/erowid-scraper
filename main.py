import requests
import requests_cache
from datetime import timedelta
from bs4 import BeautifulSoup
import psycopg2
import pandas as pd


requests_cache.install_cache('page_cache', expire_after=timedelta(hours=8))
response = requests.get('https://erowid.org/experiences/exp.cgi?ShowViews=0&Cellar=0&Start=0&Max=39281')

if response.from_cache:
    print('Response was returned from cache')
else:
    print('Response was not cached, a new request was made (slow)')

soupParser = BeautifulSoup(response.content, 'html.parser')
expRows = soupParser.select('tr[class=""]')
expPages = []

for item in expRows:
    expPage = item.select('td a')
    if expPage:
        href = expPage[0].get('href')
        url = f'https://erowid.org/experiences/{href}'
        response = requests.get(url)
        expPages.append(response)
