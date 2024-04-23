import psycopg2
import uuid
from datetime import datetime

class Product:
    def __init__(self, title, link, price, created_at=None, updated_at=None, is_deleted=False):
        self.id = str(uuid.uuid4())
        self.title = title
        self.link = link
        self.price = price
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.is_deleted = is_deleted
