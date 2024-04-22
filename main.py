import logging
import requests
from bs4 import BeautifulSoup
import psycopg2
from psycopg2 import Error
import os

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

class GatherData(LoggingConfigurator):
    def __init__(self):
        self.base_url="https://www.trendyol.com/akilli-cep-telefonu-x-c109460?pi="


    def GatherPageNumber(self) -> int :
        while True:
            try:
                response = requests.get(self.url)
                self.logger.error("Gathered the url for updating items getting sold")
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    items = soup.find_all('div', class_='item')  # Adjust class name accordingly
                    self.logger.error("Gathered the url for updating items getting sold , total count on page")
                else:
                    print("Failed to retrieve page:", response.status_code)
                    return None
            except Exception as err:
                self.logger.error("An error occured while collecting the page items , skipping the page")

def get_pages():
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a')
        for link in links:
            print(link.get('href'))
    else:
        print('Failed to retrieve webpage. Status code:', response.status_code)

def Main():
    client=DBClient()
    print(client)

Main()