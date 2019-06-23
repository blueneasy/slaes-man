import pandas as pd
import xlrd
import bs4
import requests


db = pd.read_excel('Products 2019-06-23.xlsx', index_col=0)

new_row_list = []

for nm in db['Produkt'].values:

    print(nm)
    myurl = 'https://www.ceneo.pl/;szukaj-' + nm.replace(' ', '+')
    morele = requests.get(myurl)
    mpage_html = morele.text
    morele.close()

    mpage_soup = bs4.BeautifulSoup(mpage_html, 'html.parser')

    # grab 1st product's link
    fitem = mpage_soup.find('div', {'class': 'cat-prod-row-body'}).div.a.attrs['href']
    print(fitem)

    mydetailedurl = 'https://www.ceneo.pl' + fitem
    moreledet = requests.get(mydetailedurl)
    mdpage_html = moreledet.text
    moreledet.close()

    mdpage_soup = bs4.BeautifulSoup(mdpage_html, 'html.parser')

    # grab best prices
    ceneoname = mdpage_soup.find('h1', {'class': 'product-name js_product-h1-link js_product-force-scroll js_searchInGoogleTooltip default-cursor'}).text
    print(ceneoname)
    cena1 = mdpage_soup.find('table', {'class': 'product-offers js_product-offers'}).tbody.tr.attrs['data-price']
    print(cena1)
    cena2 = mdpage_soup.find('table', {'class': 'product-offers js_product-offers js_normal-offers'}).tbody.tr.attrs['data-price']
    print(cena2)

    new_single_row = {}
    new_single_row.update({'ceneo': ceneoname, 'cena1': cena1, 'cena2': cena2})
    new_row_list.append(new_single_row)

ndf = pd.DataFrame(new_row_list, columns=['ceneo', 'cena1', 'cena2'])
print(ndf.head())

