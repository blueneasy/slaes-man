import pandas as pd
import xlrd
import bs4
import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

# selenium settings

option = Options()
option.add_argument("==disable-infobars")
option.add_argument("==start-maximized")
option.add_argument("--disable-extensions")
option.add_experimental_option("prefs", {
    "profile.default_content_setting_values.notifications": 2})
driver = webdriver.Chrome(ChromeDriverManager().install(), options=option)

# functions:

# 1) get product name and prices from c.pl.
# note: Only one container displays for products without recommendation.


def test1stlink():
    links = cpage_soup.findAll('div', {'class:': 'cat-prod-row js_category-list-item js_clickHashData js_man-track-event'})

    # fitem = cpage_soup.find('div', {'class': 'cat-prod-row-body'}).div.a.attrs['href']
    i = 0
    while i < 3:
        if '/Click/Offer' in links[0].div.div.a.attrs['href']:
            i += 1
        else:
            fitem = links.div.div.a.attrs['href']
            print(fitem)
            return fitem


def scrapceneo():
    boxes = mdpage_soup.findAll('section', {'class': 'product-offers-group'})
    ceneoname = mdpage_soup.find('section', {'class': 'product-offers-group'}).table.tbody.tr.attrs[
        'data-gaproductname']
    print(ceneoname)
    cena1 = mdpage_soup.find('section', {'class': 'product-offers-group'}).table.tbody.tr.attrs['data-price']
    print(cena1)
    if len(boxes) > 1:
        cena2 = boxes[1].table.tbody.tr.attrs['data-price']
        print(cena2)
    else:
        cena2 = 0

    return ceneoname, cena1, cena2


db = pd.read_excel('Products 2019-06-23.xlsx', index_col=0)

new_row_list = []

for nm in db['Produkt'].values:

    print(nm)
    myurl = 'https://www.ceneo.pl/;szukaj-' + nm.replace(' ', '+')
    print(myurl)
    ceneopage = requests.get(myurl)
    cpage_html = ceneopage.text
    ceneopage.close()

    cpage_soup = bs4.BeautifulSoup(cpage_html, 'html.parser')

    # grab 1st product's link

    test1stlink()

    mydetailedurl = 'https://www.ceneo.pl' + fitem
    ceneodet = requests.get(mydetailedurl)
    cdpage_html = ceneodet.text
    ceneodet.close()

    mdpage_soup = bs4.BeautifulSoup(cdpage_html, 'html.parser')

    # grab best prices
    ceneoname, cena1, cena2 = scrapceneo()

    new_single_row = {}
    new_single_row.update({'ceneo': ceneoname, 'cena1': cena1, 'cena2': cena2})
    new_row_list.append(new_single_row)

ndf = pd.DataFrame(new_row_list, columns=['ceneo', 'cena1', 'cena2'])
print(ndf.head())

