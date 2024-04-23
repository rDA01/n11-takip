from data.repositories.productRepository import ProductRepository
from data.entities.product import Product

import requests
from bs4 import BeautifulSoup
import re

from service.telegramService import TelegramService

class ProductService:
    def __init__(self, repository: ProductRepository, telegram_service: TelegramService):
        self.repository = repository
        self.telegram_service = telegram_service
        self.base_url = "https://trendyol.com"
    async def updateProduct(self):
        links = self.repository.get_all_product_links()

        for link in links:
            print("searched link: ", link)
            response = requests.get(str(self.base_url) + str(link))
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                product_detail_div = soup.find('div', class_='product-detail-wrapper')

                if product_detail_div:
                    price_span = product_detail_div.find('span', class_='prc-dsc')

                    if price_span:
                        price_text = price_span.text.strip()
                        price_numeric = float(''.join(filter(str.isdigit, price_text)))
                        product = self.repository.get_product_by_link(link)

                        if product:
                            if product.price != price_numeric:
                                print("existing price: ", product.price, '\n', "new price: ", price_numeric)
                                old_price = product.price
                                product.price = price_numeric
                                self.repository.update_product(product)
                                 # Send message to Telegram group
                                #message = f"Price of {product.title} has been updated. New price: {price_numeric}"
                                message = f"{str(self.base_url) + str(link)} linkli, {product.title} başlıklı ürünün fiyatı değişmiştir. Önceki fiyat: {old_price}, Yeni fiyat: {price_numeric}"

                                await self.telegram_service.send_message(message)
                            else:
                                print("Product price is remaining the same")
                        else:
                            print("Product not found in the database:", link)
                    else:
                        print("No price span found.")
                else:
                    print("Price box not found on the page:", link)
            else:
                print("Failed to retrieve page:", response.status_code)

        