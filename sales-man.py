from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import requests


myurl = 'https://www.morele.net/alarmcenowy/'

# opening up connection, grabbing the page
# uClient = uReq(myurl)
uClient = requests.get(myurl)
page_html = uClient.text
uClient.close()

#html parsing
page_soup = soup(page_html, "html.parser")

# print(page_soup.h1)
# print(page_soup.p.b.text)

# grabs each product
containers = page_soup.findAll("div", {"class": "owl-item"})

filename = "products.csv"
f = open(filename, "w")
headers = "produkt|komentarze|stara cena|nowa cena\n"
f.write(headers)

for container in containers:
    produkt = container.div.find('a', class_="link-bottom").span.text[:37].strip()
    komentarze = ""
    ktest = container.find('div', class_='row').div.div.span
    komentarze = ktest.text if ktest else "(0)"
    #TODO: remove "zł"
    scena = container.find('div', class_='product-slider-price text-right').span.text
    ncena = container.find('div', class_='product-slider-price text-right').findChildren()[1].text
    print("produkt: " + produkt)
    print("komentarze: " + komentarze)
    print("stara cena: " + scena)
    print("nowa cena: " + ncena)
    #TODO: change output to dataframe and analyse
    #TODO: add calculated fields
    # TODO: change formatting
    f.write(produkt + '|' + komentarze + '|' + scena + '|' + ncena + "\n")

f.close()
