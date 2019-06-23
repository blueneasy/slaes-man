from bs4 import BeautifulSoup as soup
import requests
from datetime import date
import pandas as pd

myurl = 'https://www.morele.net/alarmcenowy/'

# opening up connection, grabbing the page
uClient = requests.get(myurl)
page_html = uClient.text
uClient.close()

#html parsing
page_soup = soup(page_html, "html.parser")

# print(page_soup.h1)
# print(page_soup.p.b.text)

# grabs each product
containers = page_soup.findAll("div", {"class": "owl-item"})

row_list = []

for container in containers:
    produkt = container.div.find('a', class_="link-bottom").span.text[:37].strip()
    komentarze = ""
    ktest = container.find('div', class_='row').div.div.span
    komentarze = ktest.text if ktest else "0"
    komentarze = komentarze.strip('()')

    scena = float(''.join(container.find('div', class_='product-slider-price text-right').span.text.strip("zł").split()).replace(',', '.'))
    ncena = float(''.join(container.find('div', class_='product-slider-price text-right').findChildren()[1].text.strip("zł").split()).replace(',', '.'))

    single_row = {}
    single_row.update({'Produkt': produkt, '#komentarze': komentarze, 'Stara cena': scena, 'Nowa cena': ncena})
    row_list.append(single_row)

df = pd.DataFrame(row_list, columns=['Produkt', '#komentarze', 'Stara cena', 'Nowa cena', 'var', 'var2'])

df['var'] = df['Stara cena'] - df['Nowa cena']
df['var2'] = df['var'] / df['Stara cena']

df.index += 1
df.index.name = 'id'
df.sort_values(by='var2', ascending='False')
df.to_excel('Products ' + str(date.today()) + '.xlsx', float_format='%.2f')

print(df.head())