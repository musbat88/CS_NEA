import tkinter as tk
import sqlite3

con = sqlite3.connect("databases.db")
cur = con.cursor()
cur.execute("CREATE TABLE users(user_id, username, password_hash)")