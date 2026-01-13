import sqlite3
import bcrypt

class DatabaseSetup:
    def __init__(self, db_name='price_tracker.db'):
        self.db_name = db_name

    # Creates the tables if they dont exist
    def create_table(self):
        con = sqlite3.connect(self.db_name)
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
                    price REAL
                )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS SavedItems(
                    user_id INTEGER,
                    product_id INTEGER,
                    FOREIGN KEY(user_id) REFERENCES users(user_id),
                    FOREIGN KEY(product_id) REFERENCES products(product_id)
                )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS ProductSpecs(
                spec_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                attribute_name TEXT NOT NULL,
                attribute_value TEXT NOT NULL,
                FOREIGN KEY(product_id) REFERENCES products(product_id)
                )
        ''')

class UserManager:
    def __init__(self, db_name="price_tracker.db"):
        self.db_name = db_name

    # Creates a new user and adds them to the database, also hashing their password
    def create_user(self, username, password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        try:
            con = sqlite3.connect(self.db_name)
            cur = con.cursor()
            cur.execute('INSERT INTO Users (username, password_hash) VALUES (?, ?)', (username, hashed_password))
            con.commit()
            return True
        
        except sqlite3.IntegrityError:
            print("Username already exists.")
            return False
    
    # Checks whether the credentials are right or not
    def verify_user(self, username, password):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute('SELECT user_id, password_hash FROM Users WHERE username = ?', (username,))
        result = cur.fetchone()

        if result:
            user_id, password_hash = result
            if bcrypt.checkpw(password.encode('utf-8'), password_hash):
                return user_id
        
        return None