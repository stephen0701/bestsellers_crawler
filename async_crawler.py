import requests
import asyncio
import aiohttp
import pandas as pd
from bs4 import BeautifulSoup
from collections import defaultdict
import json

class yCrawler():
    """
    An asyncronous crawler
    """
    def __init__(self, url, max_tasks=10):
        self.url = url
        self.result = defaultdict(dict)
        self.catMap = {}
        self.max_tasks = max_tasks

    def parse_main(self):
        """
        Parse the category menu on homepage
        """
        resp = requests.get(self.url)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")

            for i, menuTag in enumerate(soup.select('#category > li.menuitem')):
                menuKey = menuTag.get('data-desc')
                print('Searching URLs on Menu {}...'.format(menuKey))
                self.parse_menu(menuTag, menuKey)

    def parse_menu(self, tag, menuName):
        """
        Find category links on each category
        """
        for catTag in tag.select('a.menulink'):
            self.add_catUrl(catTag, menuName)

        # Parse the content in popup menu
        for popup in tag.select('div.popup'):
            self.parse_popup(popup, menuName)

    def parse_popup(self, popup, menuName):
        """
        Find category links on popup menus
        """
        content = ''.join(popup.contents[1])
        popupSoup = BeautifulSoup(content, "html.parser")
        catRows = popupSoup.select('div.menu > div.catList.column > div.catRow')
        
        for row in catRows:
            catTag = row.select('div.catLevel2 > a.catLink')[0]
            self.add_catUrl(catTag, menuName)

            subCatTags = row.select('div.catLevel3 > a.catLink')
            for subCatTag in subCatTags:
                self.add_catUrl(subCatTag, menuName)

    def add_catUrl(self, tag, menuName):        
        """
        Add the valid category links.
        """
        catName = tag.string
        url = tag.get('href')
        pair = (menuName, url)

        if 'z=' in url or 'sub=' in url and pair not in self.catMap.keys():
            self.catMap[pair] = catName

    async def get_body(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                assert response.status == 200
                html = await response.read()
                return html

    async def get_products(self, menuName, catName, catUrl):
        """
        Fetch the Bestsellers info in the category page
        """
        print('{}/{}'.format(menuName, catName))
        html = await self.get_body(catUrl)
        soup = BeautifulSoup(html, "html.parser")
        productTags = soup.select('#cl-hotrank > div.brand > ul.pdset')
        
        products = []
        for tag in productTags:
            try:
                info = tag.select('div.text > a')[0].string
                priceText = tag.select('div.pd-price > span.red-price > a')[0].string
                if priceText and priceText.isdecimal():
                    price = int(priceText)
                else:
                    price = None
                products.append((info, price))
            except Exception as e:
                print(type(e), str(e))
        
        # Store the result in a dict structure
        if len(products) > 0:
            self.result[menuName][catName] = {'url': catUrl, 'products': products}

    async def work_task(self, task_id, work_queue):
        while not work_queue.empty():
            catName, catId, catUrl = await work_queue.get()
            await self.get_products(catName, catId, catUrl)

    def parse_products(self):
        """
        Parse the links asychronously
        """
        # Initialize a task queue
        q = asyncio.Queue()
        for catPair, catName in self.catMap.items():
            menuName = catPair[0]
            catUrl = catPair[1]
            q.put_nowait((menuName, catName, catUrl))
        
        # Initialize a event pool
        loop = asyncio.get_event_loop()

        # Generate workers to handle the tasks
        tasks = [self.work_task(task_id, q) for task_id in range(self.max_tasks)]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()