import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod

# Abstract class and method used so that every class has to have the scrape method inside it
class Scraper(ABC):
    def __init__(self):
        # Uses a user agent to not get blocked, user agent found by searching up what is my user agent
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
        }

    @abstractmethod
    def scrape(self, query):
        pass

class ScanScraper(Scraper):
    def scrape(self, query):
        # Adds the search to the url
        url = f'https://www.scan.co.uk/search?q={query.replace(' ', '+')}'
        # Sends a request to the website using the header
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Finds the <li> tags in the html with the class product, this takes the box each item is stored in
        product_boxes = soup.find_all('li', class_='product')
        products = []

        # Formats the name, price and link for the product from the html code
        for i in product_boxes[:5]:
            name_tag = i.find('span', class_='description')
            product_name = name_tag.text.strip()
            price_tag = i.find('span', class_='price')

            # Strips the price from random characters, spaces and the pound symbol so that it can be added to the database as the database uses a float to store price
            if price_tag:
                raw_price = price_tag.text.replace('£', '').replace(',', '').strip()
                product_price = float(raw_price)
            else:
                product_price = 0.0     

            url_tag = i.find('a')
            product_url = "https://www.scan.co.uk" + url_tag['href']
            
            # Adds the products to a dictionary
            products.append({
                'name': product_name,
                'price': product_price,
                'url': product_url,
                'website': 'Scan.co.uk'
            })
        return products

class AmazonScraper(Scraper):
    def scrape(self, query):
        url = f'https://www.amazon.co.uk/s?k={query.replace(' ', '+')}'
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        product_boxes = soup.find_all('div', class_='a-section a-spacing-small a-spacing-top-small')
        products = []
        for i in product_boxes[:5]:
            name_tag = i.find('h2')
            product_name = name_tag.text.strip()
            price_tag = i.find('span', class_='a-offscreen')
            if price_tag:
                raw_price = price_tag.text.replace('£', '').replace(',', '').strip()
                product_price = float(raw_price)
            else:
                product_price = 0.0 

            url_tag = i.find('a', class_='a-link-normal s-line-clamp-2 puis-line-clamp-3-for-col-4-and-8 s-link-style a-text-normal')
            product_url = "https://www.amazon.co.uk" + url_tag['href']
            products.append({
                'name': product_name,
                'price': product_price,
                'url': product_url,
                'website': 'amazon.co.uk'
            })
        return products
    
class EbuyerScraper(Scraper):
    def scrape(self, query):
        url = f'https://www.ebuyer.com/searchresults?descriptionfilter={query.replace(" ", "+")}'
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        product_boxes = soup.find_all('li', attrs={'li-name': True})
        products = []
        for i in product_boxes[:5]:
            product_name = i.get('li-name')
            raw_price = i.get('li-price')
            product_price = float(raw_price)
            url = i.get('li-url')

            
            products.append({
                'name': product_name,
                'price': product_price,
                'url': "https://www.ebuyer.com" + url,
                'website': 'ebuyer.com'
            })
        return products