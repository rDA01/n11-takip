import psycopg2
import uuid
from datetime import datetime

class ProductRepository:
    def __init__(self):
        db_params = {
            'host': 'localhost',
            'database': 'trendyol-takip',
            'user': 'trendyol',
            'password': 'trendyol-bot-1234321'
        }

        self.conn = psycopg2.connect(**db_params)
        self.cursor = self.conn.cursor()
        self._create_table_if_not_exists()

    def _create_table_if_not_exists(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Products (
                                Id TEXT PRIMARY KEY,
                                Title TEXT,
                                Link TEXT,
                                Price DECIMAL,
                                CreatedAt TIMESTAMP,
                                UpdatedAt TIMESTAMP,
                                IsDeleted BOOLEAN
                            )''')
        self.conn.commit()

    def add_product(self, product):
        self.cursor.execute('''INSERT INTO Products (Id, Title, Link, Price, CreatedAt, UpdatedAt, IsDeleted)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                            (product.id, product.title, product.link, product.price,
                             product.created_at, product.updated_at, product.is_deleted))

        print("new item added")
        self.conn.commit()

    def get_product_by_id(self, product_id):
        self.cursor.execute("SELECT * FROM Products WHERE Id=%s", (product_id,))
        row = self.cursor.fetchone()
        if row:
            return self._row_to_product(row)
        else:
            return None

    def update_product(self, product):
        self.cursor.execute('''UPDATE Products SET Title=%s, Link=%s, Price=%s, UpdatedAt=%s, IsDeleted=%s
                                WHERE Id=%s''',
                            (product.title, product.link, product.price, datetime.now(),
                             product.is_deleted, product.id))
        self.conn.commit()

    def delete_product(self, product_id):
        self.cursor.execute("DELETE FROM Products WHERE Id=%s", (product_id,))
        self.conn.commit()

    def _row_to_product(self, row):
        return Product(row[1], row[2], row[3], row[4], row[5], row[6])

    def close(self):
        self.conn.close()