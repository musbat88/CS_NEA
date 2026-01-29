import requests
from bs4 import BeautifulSoup

class Scraper:
    def __init__(self):
        # Uses a user agent to not get blocked, user agent found by searching up what is my user agent
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
        }

    # Scrapes the website scan.co.uk
    def scrape_scan(self, query):
        # Adds the search to the url
        url = f'https://www.scan.co.uk/search?q={query.replace(' ', '+')}'
        # Sends a request to the website using the header
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Finds the <li> tags in the html with the class product, this takes the box each item is stored in
        product_boxes = soup.find_all('li', class_='product')
        products = []

        # Formats the name, price and link for the product from the html code
        for i in product_boxes:
            name_tag = i.find('span', class_='description')
            product_name = name_tag.text.strip() if name_tag else "No name"
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