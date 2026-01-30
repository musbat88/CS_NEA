import sqlite3
import bcrypt
from Scraper import Scraper

class DatabaseSetup:
    def __init__(self, db_name='price_tracker.db'):
        self.db_name = db_name

    # Creates the tables if they dont exist
    def create_table(self):
        with sqlite3.connect(self.db_name) as con:
            cur = con.cursor()

            cur.execute('''
                CREATE TABLE IF NOT EXISTS Users(
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                )
            ''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS Products(
                    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_url TEXT UNIQUE NOT NULL,
                    product_name TEXT,
                    product_website TEXT,
                    price REAL
                )
            ''')

            cur.execute('''
            CREATE TABLE IF NOT EXISTS SavedItems(
                user_id INTEGER,
                product_id INTEGER,
                PRIMARY KEY(user_id, product_id),
                FOREIGN KEY(user_id) REFERENCES Users(user_id),
                FOREIGN KEY(product_id) REFERENCES Products(product_id)
            )
        ''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS ProductSpecs(
                    product_id INTEGER NOT NULL,
                    attribute_name TEXT NOT NULL,
                    attribute_value TEXT NOT NULL,
                    FOREIGN KEY(product_id) REFERENCES Products(product_id),
                    PRIMARY KEY(product_id, attribute_name)
                )
            ''')

class UserManager:
    def __init__(self, db_name="price_tracker.db"):
        self.db_name = db_name

    # Creates a new user and adds them to the database, also hashing their password
    def create_user(self, username, password):
        # Hashes the password using bcrypt
        hash = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(hash, salt)

        try:
            with sqlite3.connect(self.db_name) as con:
                cur = con.cursor()
                cur.execute('INSERT INTO Users (username, password_hash) VALUES (?, ?)', (username, hashed_password))
                con.commit()
                return True
        except sqlite3.IntegrityError:
            print("Username already exists.")
            return False
    
    # Checks whether the credentials are right or not
    def verify_user(self, username, password):
        with sqlite3.connect(self.db_name) as con:
            cur = con.cursor()
            cur.execute('SELECT user_id, password_hash FROM Users WHERE username = ?', (username,))
            result = cur.fetchone()
            if result:
                # Unhashes the password and checks it against the password input
                user_id, password_hash = result
                if bcrypt.checkpw(password.encode('utf-8'), password_hash):
                    return user_id
            return None
    
class ProductManager:
    def __init__(self, db_name="price_tracker.db"):
        self.db_name = db_name

    # Updates the database and displays the products that you searched for
    def update_and_search(self, query, sort_by='product_id ASC'):
        scraper = Scraper()
        scan_results = scraper.scrape_scan(query)
        amazon_results = scraper.scrape_amazon(query)
        all_results = scan_results + amazon_results

        for i in all_results:
            self.add_product(i['url'], i['name'], i['website'], i['price'])
        return self.search_products(query, sort_by)

    # Adds a product to the database along with its relevant info
    def add_product(self, product_url, product_name, product_website, price):
        with sqlite3.connect(self.db_name) as con:
            cur = con.cursor()
            cur.execute('''
                INSERT INTO Products (product_url, product_name, product_website, price)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(product_url) DO UPDATE SET
                    price = excluded.price,
                    product_name = excluded.product_name
            ''', (product_url, product_name, product_website, price))
            con.commit()
            return cur.lastrowid
    
    # Searches for a product in the Products table
    def search_products(self, query, sort_by='product_id ASC'):
        with sqlite3.connect(self.db_name) as con:
            cur = con.cursor()
            cur.execute(f'SELECT * FROM Products WHERE product_name LIKE ? ORDER BY {sort_by}', (f'%{query}%',))
            return cur.fetchall()
        
    # Saves a product into the Products table
    def save_product(self, user_id, product_id):
        try:
            with sqlite3.connect(self.db_name) as con:
                cur = con.cursor()
                cur.execute('INSERT INTO SavedItems (user_id, product_id) VALUES (?, ?)', (user_id, product_id))
                con.commit()
                return True
        except:
            print(f"Product {product_id} is already saved for User {user_id}.")
            return False
    
    # Returns all the items that the user has bookmarked
    def get_user_dashboard(self, user_id):
        with sqlite3.connect(self.db_name) as con:
            cur = con.cursor()
            cur.execute('''
                SELECT Products.* FROM Products, SavedItems
                WHERE Products.product_id = SavedItems.product_id
                AND SavedItems.user_id = ?
            ''', (user_id,))
            return cur.fetchall()
    
    # Adds a specification of the product into the table
    def add_spec(self, product_id, attribute_name, attribute_value):
        with sqlite3.connect(self.db_name) as con:
            cur = con.cursor()
            cur.execute('''
                INSERT INTO ProductSpecs (product_id, attribute_name, attribute_value)
                VALUES (?, ?, ?)
            ''', (product_id, attribute_name, attribute_value))
            con.commit()
        
    # Returns the specifications of a product
    def get_specs(self, product_id):
        with sqlite3.connect(self.db_name) as con:
            cur = con.cursor()
            cur.execute('''
                SELECT attribute_name, attribute_value FROM ProductSpecs
                WHERE product_id = ?
            ''', (product_id,))
            return cur.fetchall()
        
    # Removes the product from the dashboard
    def remove_saved_product(self, user_id, product_id):
        with sqlite3.connect(self.db_name) as con:
            cur = con.cursor()
            cur.execute('''
                DELETE FROM SavedItems 
                WHERE user_id = ? AND product_id = ?
            ''', (user_id, product_id))
            con.commit()
            return True