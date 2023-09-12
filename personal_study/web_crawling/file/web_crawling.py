import requests
from bs4 import BeautifulSoup

url = "https://news.naver.com/"
res = requests.get(url)
res.raise_for_status()

soup = BeautifulSoup(res.text, 'lxml')

header_tag = soup.find("span", attrs = {"class":"Nitem_link_menu"})
a = header_tag.text_sbling

print(a)
print(header_tag.text)