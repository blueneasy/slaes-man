import pandas as pd
import xlrd
import bs4
import requests
from datetime import date
from MoreleScraper import Scraper
import numpy as np
import functools

class Analyser:

    # functions:
    # 1) get product name and prices from c.pl.
    # note: Only one container displays for products without recommendation.

    def test1stlink(self, cpage_soup):
        cview = self.testview(cpage_soup)
        if cview == 'list':
            links = cpage_soup.findAll('div', class_='cat-prod-row js_category-list-item js_clickHashData js_man-track-event')
            i = 0
            while i < 3:
                if '/Click/Offer' in links[i].div.div.a.attrs['href'] or 'row_promotion' in links[i].div.div.a.attrs['href']:
                    i += 1
                    if i == 2:
                        fitem = '0 results'
                        return fitem
                elif links[i].div.div.a.attrs['href'][0] != '/':
                    fitem = '/' + links[i].attrs['data-pid']
                    return fitem
                else:
                    fitem = links[i].div.div.a.attrs['href']
                    return fitem
        elif cview == 'boxed':
            try:
                cpage_soup.find('div', class_='grid-item grid-item--1x2 js_grid-item js_category-list-item js_man-track-event').attrs['data-pid']
            except AttributeError:
                try:
                    link = cpage_soup.find('div', class_='category-item-box js_category-list-item js_clickHashData js_man-track-event').attrs['data-pid']
                    fitem = '/' + link
                    return fitem
                except AttributeError:
                    fitem = '0 results'
                    return fitem
            else:
                link = cpage_soup.find('div', class_='grid-item grid-item--1x2 js_grid-item js_category-list-item js_man-track-event').attrs['data-pid']
                fitem = '/' + link
                return fitem
        elif cview == 'boxed_2nd_type':
            try:
                cpage_soup.find('div', class_='grid-item grid-item--1x1 js_grid-item js_category-list-item js_man-track-event').attrs['data-pid']
            except AttributeError:
                try:
                    link = cpage_soup.find('div', class_='category-item-box js_category-list-item js_clickHashData js_man-track-event').attrs['data-pid']
                    fitem = '/' + link
                    return fitem
                except AttributeError:
                    fitem = '0 results'
                    return fitem
            else:
                link = cpage_soup.find('div', class_='grid-item grid-item--1x1 js_grid-item js_category-list-item js_man-track-event').attrs['data-pid']
                fitem = '/' + link
                return fitem

    @staticmethod
    def testview(cpage_soup):
        try:
            cpage_soup.find('ul', {'class': 'category-list-type-switcher'}).li.a.attrs['class'][2]
        except IndexError:
            view = 'boxed'
            return view
        except AttributeError:
            view = 'boxed_2nd_type'
            return view
        else:
            view = 'list'
            return view

    @staticmethod
    def scrapceneo(mdpage_soup):
        boxes = mdpage_soup.findAll('section', {'class': 'product-offers-group'})
        try:
            ceneoname = mdpage_soup.find('section', {'class': 'product-offers-group'}).table.tbody.tr.attrs['data-gaproductname']
        except KeyError:
            ceneoname = 'n/a'
        print(ceneoname)

        try:
            cena1 = mdpage_soup.find('section', {'class': 'product-offers-group'}).table.tbody.tr.attrs['data-price']
        except KeyError:
            cena1 = 'n/a'
        print(cena1)

        if len(boxes) > 1:
            try:
                cena2 = boxes[1].table.tbody.tr.attrs['data-price']
            except KeyError:
                cena2 = 'n/a'
            print(cena2)
        else:
            cena2 = 'n/a'

        return ceneoname, cena1, cena2

    def analyse(self, filename):

        morele_df = pd.read_excel(filename, index_col=0)

        new_row_list = []

        for nm in morele_df['Produkt'].values:

            print(nm)
            myurl = 'https://www.ceneo.pl/;szukaj-' + nm.replace(' ', '+')
            print(myurl)
            ceneopage = requests.get(myurl, timeout=5)
            cpage_html = ceneopage.text
            ceneopage.close()

            cpage_soup = bs4.BeautifulSoup(cpage_html, 'html.parser')

            best_match = self.test1stlink(cpage_soup)
            if best_match == '0 results':
                ceneoname = cena1 = cena2 = 'n/a'
            else:
                mydetailedurl = 'https://www.ceneo.pl' + best_match
                ceneodet = requests.get(mydetailedurl, timeout=5)
                cdpage_html = ceneodet.text
                ceneodet.close()

                mdpage_soup = bs4.BeautifulSoup(cdpage_html, 'html.parser')

                # grab best prices
                ceneoname, cena1, cena2 = self.scrapceneo(mdpage_soup)

            new_single_row = {}
            new_single_row.update({'ceneo': ceneoname, 'cena1': cena1, 'cena2': cena2})
            new_row_list.append(new_single_row)

        ceneo_df = pd.DataFrame(new_row_list, columns=['ceneo', 'cena1', 'cena2'])

        output_df = pd.concat([morele_df.reset_index(drop=True), ceneo_df], axis=1)

        # CALCULATED FIELDS
        # minimum c price
        output_df['min'] = output_df[['cena1', 'cena2']].min(axis=1)
        # var3 - variance between c min price and new morele price
        output_df['real discount'] = output_df['Nowa cena'] - output_df['min']
        # real discount percentage
        output_df['real discount %'] = output_df['real discount'] / output_df['min']

        # FILTERS
        # filtering top discounts

        # is var > 0
        output_df['condition1'] = output_df['real discount'] > 0
        # eliminate discounts greater than 65%
        output_df['condition2'] = output_df['real discount %'] < -0.65
        # eliminate discounts less than 100 PLN
        output_df['condition3'] = output_df['real discount'] > -100

        print(output_df.head())

        output_df.to_excel('Analysed ' + Scraper.file_name(), float_format='%.2f')

        # output with filters applied

        # print(output_df[output_df.condition1 == 'False'])


        #output_filters_df.to_excel('Filtered ' + Scraper.file_name(), float_format='%.2f')
