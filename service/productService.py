from decimal import Decimal
from data.repositories.productRepository import ProductRepository
from data.entities.product import Product

import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
from service.telegramService import TelegramService

class ProductService:
    def __init__(self, repository: ProductRepository, telegram_service: TelegramService):
        self.repository = repository
        self.telegram_service = telegram_service
        self.base_url = "https://www.n11.com/"
    async def updateProduct(self):
        PATH = "C:\Program Files (x86)\chromedriver.exe"
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        cService = webdriver.ChromeService(executable_path=PATH)
        driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
        
        links = self.repository.get_all_product_links()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
        for link in links:
            time.sleep(1)
            response = driver.get(link)
            if isBrowserAlive(driver):
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                try: 
                    price_cover = soup.find('div', class_='price-cover')
                    price_details = price_cover.find('div',class_="priceDetail")
                    price_div = price_details.find('div',class_="newPrice")
                except:
                    print(str(link))
                    print("couldnt find price")
                    pass
                
                if price_div:
                    ins = price_div.find('ins')
                    
                    
                    if ins:
                        
                        price_text = ins.text.strip()
                        print(price_text)
                        price_text = price_text.replace('.', '').replace(',', '.')  # Replace comma with dot
                        price_numeric = float(''.join(filter(lambda x: x.isdigit() or x == '.', price_text)))
                        price_numeric = Decimal(price_numeric)
                        print(price_numeric)
                        product = self.repository.get_product_by_link(link)
                        
                        
                        if product:
                            if product.price != price_numeric:
                                print("existing price: ", product.price, '\n', "new price: ", price_numeric)
                                
                                old_price = Decimal(product.price)
                                
                                price_numeric = Decimal(price_numeric)
                                 
                                
                                product.price = Decimal(price_numeric)
                                self.repository.update_product(product)
                                isInstallment = Decimal(price_numeric) <= Decimal(old_price) * Decimal(0.92) 
                                if(isInstallment):
                                    print("installment catched, product link: ", product.link)
                                    installment_rate = ((old_price - Decimal(price_numeric)) / old_price) * 100
                                    old_price = "{:.2f}".format(old_price) 
                                    price_numeric = "{:.2f}".format(price_numeric)
                                    installment_rate = "{:.1f}".format(installment_rate)
                                    message = f"{str(link)} linkli, {product.title} başlıklı ürünün fiyatında indirim oldu. Önceki fiyat: {old_price}, Yeni fiyat: {price_numeric}. İndirim oranı: %{installment_rate}"

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
                print("Failed to retrieve page")
        driver.quit()        

def isBrowserAlive(driver):
   try:
      driver.current_url
      return True
   except:
      return False        