from DatabaseManagement import DatabaseSetup, UserManager, ProductManager
from UserInterface import UIManager

# Runs the application
def main():
    db_file = "price_tracker.db"
    db_setup = DatabaseSetup(db_file)
    db_setup.create_table()
    auth_manager = UserManager(db_file)
    product_manager = ProductManager(db_file)
    app = UIManager(auth_manager=auth_manager, product_manager=product_manager)
    app.run()

if __name__ == "__main__":
    main()