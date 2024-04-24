import asyncio
import logging
import requests
from bs4 import BeautifulSoup
import threading

from data.entities.product import Product
from data.repositories.productRepository import ProductRepository
from service.productService import ProductService
from service.telegramService import TelegramService

class LoggingConfigurator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        handler = logging.FileHandler('application.log')
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

class GatherPagesItems(LoggingConfigurator):
    def __init__(self, product_repo):
        self.base_url="https://www.trendyol.com/akilli-cep-telefonu-x-c109460?pi="
        self.page_count=0
        self.item_count=0
        self.product_repo = product_repo

    async def gather_page_number(self, base_url, i):
        try:
            response = requests.get(base_url + str(i))
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                divs = soup.find_all('div', class_='p-card-chldrn-cntnr card-border')

                for div in divs:
                    h3 = div.find('h3', class_='prdct-desc-cntnr-ttl-w two-line-text')
                    a = div.find('a', href=True)
                    prc_box_dscntd = div.find('div', class_='prc-box-dscntd')
                    
                    if h3 and a and prc_box_dscntd:
                        title = h3.get_text(strip=True)
                        href = a['href']

                        item =  self.product_repo.get_product_by_link(href)
                        if item is False:
                            price_text = prc_box_dscntd.text.strip()
                            price = float(''.join(filter(str.isdigit, price_text)))

                            product = Product(title=title, link=href, price=price)
                            
                            self.product_repo.add_product(product)
                        else:
                            # Product already exists in the database
                            print("Item exists.")
                    else:
                        print("Incomplete data found in div, skipping.")
                
                div_count = len(divs)
                if div_count != 24:
                    self.item_count = (i * 24) + div_count
                    self.page_count = i
                    return False
            else:
                print("Failed to retrieve page:", response.status_code)
                return False
        except Exception as err:
            print("Error occurred:", err)
            return False
        
        return True

    async def gather_page_numbers(self):
        base_url = self.base_url
        loop_var = True
        i = 1
        while loop_var:
            #threads = []
            #for _ in range(50):
            #    t = threading.Thread(target=self.gather_page_number, args=(base_url, i))
            #    t.start()
            #    threads.append(t)
            #    i += 1
            #for t in threads:
            #    t.join()

            loop_var = await self.gather_page_number(base_url, i)
            i = i + 1

async def Main():
    product_repo = ProductRepository()

    new = GatherPagesItems(product_repo)
    
    await new.gather_page_numbers()

    telegram_service = TelegramService(bot_token='7043445528:AAF6FuY4eOBOVVOyZRhfK24pXb2E7yiK7r8', chat_id='-1002119312673')

    productService = ProductService(product_repo, telegram_service)

    while True:
        await productService.updateProduct()

asyncio.run(Main())