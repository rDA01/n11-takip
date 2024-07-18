import asyncio
import logging
import requests
from bs4 import BeautifulSoup
import threading

from data.entities.product import Product
from data.repositories.productRepository import ProductRepository
from service.productService import ProductService
from service.telegramService import TelegramService
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time

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
    def __init__(self, product_repo,url):
        self.base_url=url
        self.page_count=0
        self.item_count=0
        self.product_repo = product_repo

    async def gather_page_number(self, base_url):
        PATH = "C:\Program Files (x86)\chromedriver.exe"
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        cService = webdriver.ChromeService(executable_path=PATH)
        driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
        driver.get(base_url)
        time.sleep(5)
        
        

        flag = True
        while flag:
            counter = 0
            print("new itaration")             
                           
            try:
    
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight-100);")
                    
    
                time.sleep(2)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                divs = soup.find_all('li', class_='column')
    

                for div in divs:
                    try:
                        container = div.find('div',class_='priceContainer')
                        details = container.find('span',class_="oldPrice noLine cPoint priceEventClick hidden")
                        prc_span = details.get_text()
                          
                    except:
                        pass
    
                    if details and prc_span:
                        title = details['title']
                        href = details['data-href']     
                        item =  self.product_repo.get_product_by_link(href)
                        price_text = prc_span
                        price_text = price_text.replace('.', '').replace(',', '.')  # Replace comma with dot
                        price = float(''.join(filter(lambda x: x.isdigit() or x == '.', price_text)))                        
                        
                        if item is False:
                            product = Product(id=None,title=title, link=href, price=price)
                            self.product_repo.add_product(product)
            except Exception as err:
                print("Error occurred:", err)
                return False
            nextpage = 0
            pagination = driver.find_element(By.CLASS_NAME,"pagination")
            pages = pagination.find_elements(By.TAG_NAME,"a")
            for page in pages:
                try:
                    if page.get_attribute("class") == "active ":
                        
                        try:
                            nextpage = pages[counter+1]
                            time.sleep(2)
                            driver.execute_script("arguments[0].click();", nextpage)
                            break
                        except:
                            pass
                    elif page.get_attribute("class") == "active last":
                        print("end of pages")
                        flag = False
                        driver.quit()
                    else:
                       counter+=1 
                except: 
                       pass
  
                   
            

            
        return True

    async def gather_page_numbers(self):
        base_url = self.base_url
        
        await self.gather_page_number(base_url)

async def Main():
    product_repo = ProductRepository()

    smartphones = GatherPagesItems(product_repo,"https://www.n11.com/telefon-ve-aksesuarlari/cep-telefonu?pg=5")
    
    await smartphones.gather_page_numbers()

    
    telegram_service = TelegramService(bot_token='7393980187:AAGJHwoW6DY98jZOvTzdq0o7Ojt8X1VO28Q', chat_id='-1002203530212')

    productService = ProductService(product_repo, telegram_service)
    
    while True:
        await productService.updateProduct()
    

asyncio.run(Main())