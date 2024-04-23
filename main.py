import logging
import requests
from bs4 import BeautifulSoup
import psycopg2
from psycopg2 import Error
import os
import threading

class LoggingConfigurator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        handler = logging.FileHandler('application.log')
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

class DBClient(LoggingConfigurator):
    def __init__(self):
        super().__init__()
        self.DB_HOST = os.environ.get('DB_HOST')
        self.DB_USER = os.environ.get('DB_USER')
        self.DB_PASSWORD = os.environ.get('DB_PASSWORD')
        self.DB_NAME = os.environ.get('DB_NAME')
        self.DB_PORT = os.environ.get('DB_PORT')

        if not all([self.DB_HOST, self.DB_USER, self.DB_PASSWORD, self.DB_NAME, self.DB_PORT]):
            self.logger.error("One or more required environment variables are not set.")
            raise ValueError("One or more required environment variables are not set.")
        try:
            self.logger.info("Connection to PostgreSQL established")
            self.connection = psycopg2.connect(
                    user=self.DB_USER,
                    password=self.DB_PASSWORD,
                    host=self.DB_HOST,
                    port=self.DB_PORT,
                    database=self.DB_NAME
            )
        except (Exception, Error) as error:
            self.logger.error("Error while connecting to PostgreSQL", exc_info=True)

class GatherPagesItems(LoggingConfigurator):
    def __init__(self):
        self.base_url="https://www.trendyol.com/akilli-cep-telefonu-x-c109460?pi="
        self.page_count=0
        self.item_count=0
        item_info={}

    def gather_page_number(self,base_url, i):
        try:
            response = requests.get(base_url + str(i))
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                div_count = len(soup.find_all('div', class_='p-card-chldrn-cntnr card-border'))
                divs = soup.find_all('div', class_='p-card-chldrn-cntnr card-border')
                print("Number of div elements with class 'p-card-chldrn-cntnr card-border':", div_count)
                for div in divs:
                    h3 = div.find('h3', class_='prdct-desc-cntnr-ttl-w two-line-text')
                    a = div.find('a', href=True)
                    prc_box_dscntd= div.find('div',class_='class="prc-box-dscntd"')
                    if h3 and a:
                        title = h3.get_text(strip=True)
                        href = a['href']
                        print("Title:", title)
                        print("Href:", href)
                        print("price", prc_box_dscntd.get_text(strip=True))
                    else:
                        print("Either h3 or a tag not found within this div.")
                if div_count != 24:
                    self.item_count=(i*24)+div_count
                    self.page_count=i
                    return False
            else:
                print("Failed to retrieve page:", response.status_code)
                return False
        except Exception as err:
            print(err)
        return True

    def gather_page_numbers(self):
        base_url=self.base_url
        loop_var = True
        i = 1
        while loop_var:
            threads = []
            for _ in range(50):
                t = threading.Thread(target=self.gather_page_number, args=(base_url, i))
                t.start()
                threads.append(t)
                i += 1
            for t in threads:
                t.join()
            loop_var = all(self.gather_page_number(base_url, i) for i in range(i, i + 50))

class InsertData(LoggingConfigurator):
    def __init__(GatherPages):
        pass

def Main():
    #client=DBClient()
    #print(client)
    new=GatherPagesItems()
    new.gather_page_numbers()

Main()