import asyncio
from bs4 import BeautifulSoup, Comment
import requests
import httpx
import random

r = requests.get("https://erowid.org/experiences/exp.php?ID=115030").content

bs = BeautifulSoup(r,'html.parser')

p = bs.select('table[class="footdata"] > tr ')

sss = p[3].text
print(sss[sss.index(":")+1:sss.index("Views")])