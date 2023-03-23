import requests
from bs4 import BeautifulSoup, Comment

url = 'https://erowid.org/experiences/exp.php?ID=86160'
response = requests.get(url)
html_content = response.text

soup = BeautifulSoup(html_content, 'html.parser')

start_comment = soup.find(string=lambda string: isinstance(string, Comment) and 'Start Body' in string)
end_comment = soup.find(string=lambda string: isinstance(string, Comment) and 'End Body' in string)

content = start_comment.find_all_next(string=True)
content_until_end = content[:content.index(end_comment)]
content_report = BeautifulSoup(''.join(content_until_end), 'html.parser')
print(content_report)
