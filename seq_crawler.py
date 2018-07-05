import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from collections import defaultdict

class yCrawler():

    def __init__(self, url):
        self.url = url
        self.result = defaultdict(dict)
        self.seenCat = set()

    def parse_main(self):
        resp = requests.get(self.url)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")

            for i, menuTag in enumerate(soup.select('#category > li.menuitem')):
                menuName = menuTag.get('data-desc')
                print('Searching URLs on Menu {}...'.format(menuName))
                self.parse_menu(menuTag, menuName)
            
    def parse_menu(self, tag, catKey):

        # Iterate menu categories
        for catTag in tag.select('a.menulink'):
            self.add_category(catTag, catKey)

        # Iterate popup categories
        for popup in tag.select('div.popup'):
            self.parse_popup(popup, catKey)
        print('\n')

    def parse_popup(self, popup, catKey):

        content = ''.join(popup.contents[1])
        popupSoup = BeautifulSoup(content, "html.parser")
        catRows = popupSoup.select('div.menu > div.catList.column > div.catRow')
        
        for row in catRows:
            catTag = row.select('div.catLevel2 > a.catLink')[0]
            self.add_category(catTag, catKey)

            subCatTags = row.select('div.catLevel3 > a.catLink')
            for subCatTag in subCatTags:
                self.add_category(subCatTag, catKey)


    def add_category(self, tag, menuName):

        catName = tag.string
        url = tag.get('href')
        catProducts = self.parse_products(url, catName)

        pair = (menuName, url)
        if url and pair not in self.seenCat and catProducts:
            self.seenCat.add(pair)
            self.result[menuName][catName] = {}
            self.result[menuName][catName]['url'] = url
            self.result[menuName][catName]['products'] = catProducts


    # Parse the products page
    def parse_products(self, url, category):

        if 'z=' not in url and 'sub=' not in url:
            return []
        
        print('{}/'.format(category), end=' ')
        products = []
        resp = requests.get(url)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            productTags = soup.select('#cl-hotrank > div.brand > ul.pdset')
            
            if productTags:
                for tag in productTags:
                    try:
                        info = tag.select('div.text > a')[0].string
                        priceText = tag.select('div.pd-price > span.red-price > a')[0].string
                        if priceText and priceText.isdecimal():
                            price = int(priceText)
                        else:
                            price = None
                        products.append([info, price])
                    except Exception as e:
                        print(type(e), str(e))
        return products