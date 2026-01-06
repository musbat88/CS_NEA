import sqlite3

con = sqlite3.connect("databases.db")
cur = con.cursor()

import tkinter as tk
from tkinter import ttk, messagebox

# ==========================================
# PLACEHOLDER PAGE CLASSES
# These represent the different screens of your app.
# In a real app, these would likely be in separate files.
# ==========================================

class BasePage(tk.Frame):
    """ A generic page that all other pages inherit from. """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # 'controller' is the UIManager, allowing pages to trigger navigation
        self.controller = controller
        self.configure(bg='#f0f0f0', padx=20, pady=20)

class LoginPage(BasePage):
    def __init__(self, parent, controller, data=None):
        super().__init__(parent, controller)
        tk.Label(self, text="Login Screen", font=("Arial", 24)).pack(pady=20)
        # Example button triggering navigation via the controller
        ttk.Button(self, text="Simulate Successful Login", 
                   command=lambda: controller.go_to_search()).pack()

class SearchPage(BasePage):
    def __init__(self, parent, controller, data=None):
        super().__init__(parent, controller)
        tk.Label(self, text="Search Products", font=("Arial", 24)).pack(pady=20)
        
        search_var = tk.StringVar()
        entry = ttk.Entry(self, textvariable=search_var, width=30)
        entry.pack(pady=10)
        
        # Passing data (the search query) to the next page
        ttk.Button(self, text="Search", 
                   command=lambda: controller.go_to_results(search_var.get())).pack()

class ResultsPage(BasePage):
    def __init__(self, parent, controller, data=None):
        super().__init__(parent, controller)
        query = data if data else "Unknown"
        tk.Label(self, text=f"Results for: '{query}'", font=("Arial", 24)).pack(pady=20)
        tk.Label(self, text="(List of products would go here)").pack()

class DashboardPage(BasePage):
    def __init__(self, parent, controller, data=None):
        super().__init__(parent, controller)
        tk.Label(self, text="My Dashboard", font=("Arial", 24)).pack(pady=20)
        tk.Label(self, text="(Saved items list would go here)").pack()


# ==========================================
# THE UI MANAGER CLASS
# ==========================================

class UIManager:
    def __init__(self, auth_manager, product_manager):
        # 1. Setup Main Window
        self.root = tk.Tk()
        self.root.title("Python Price Tracker")
        self.root.geometry("800x600")
        # Use a modern theme
        style = ttk.Style()
        style.theme_use('clam') 

        # 2. Hold references to backend managers
        self.auth_manager = auth_manager
        self.product_manager = product_manager

        # 3. Navigation State
        self.container = tk.Frame(self.root) # The area where pages switch
        self.container.pack(side="top", fill="both", expand=True)
        self.current_frame = None
        
        # History Stack: Stores tuples of (PageClass, data_for_page)
        self.history_stack = []
        self.history_index = -1

        # 4. Build Permanent UI Elements (Navbar)
        self._build_navbar()

        # 5. Start at the Login Page
        self.go_to_login()

    def run(self):
        """ Starts the Tkinter event loop """
        self.root.mainloop()

    # --- CORE NAVIGATION LOGIC ---

    def _navigate_to(self, PageClass, data=None):
        """ Calling this adds a new page to the history stack. """
        # If we are in the middle of history stack and navigate to a new page,
        # we must cut off the "future" history (just like a browser).
        if self.history_index < len(self.history_stack) - 1:
            self.history_stack = self.history_stack[:self.history_index+1]

        # Add new page tuple to stack
        self.history_stack.append((PageClass, data))
        self.history_index += 1
        
        self._show_frame(PageClass, data)
        self._update_nav_buttons()

    def _show_frame(self, PageClass, data=None):
        """ Handles the actual destroying and creating of frames. """
        # 1. Destroy current page if it exists
        if self.current_frame:
            self.current_frame.destroy()

        # 2. Create new page instance
        # We pass 'self' as the controller so the page can call back to us
        self.current_frame = PageClass(parent=self.container, controller=self, data=data)
        
        # 3. Display it
        self.current_frame.pack(fill="both", expand=True)

    # --- PUBLIC NAVIGATION METHODS (Called by buttons) ---

    def go_to_login(self):
        # Clearing history on login prevent going "back" to a logged-in state later
        self.history_stack = [] 
        self.history_index = -1
        self._navigate_to(LoginPage)

    def go_to_search(self):
        self._navigate_to(SearchPage)

    def go_to_results(self, query):
        if not query:
           messagebox.showwarning("Warning", "Please enter a search term.")
           return
        self._navigate_to(ResultsPage, data=query)

    def go_to_dashboard(self):
        # In a real app, check auth first:
        # if not self.auth_manager.is_logged_in(): self.go_to_login() else: ...
        self._navigate_to(DashboardPage)

    # --- HISTORY METHODS (Back / Forward) ---

    def on_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            # Get class and data from older history entry
            PageClass, data = self.history_stack[self.history_index]
            # Show it without adding to stack
            self._show_frame(PageClass, data)
            self._update_nav_buttons()

    def on_forward(self):
        if self.history_index < len(self.history_stack) - 1:
            self.history_index += 1
            # Get class and data from newer history entry
            PageClass, data = self.history_stack[self.history_index]
            self._show_frame(PageClass, data)
            self._update_nav_buttons()

    # --- UI HELPERS ---

    def _build_navbar(self):
        """ Creates the top navigation bar persistent across pages """
        navbar = tk.Frame(self.root, bg="#ddd", height=40)
        navbar.pack(side="top", fill="x")

        # Navigation buttons
        self.btn_back = ttk.Button(navbar, text="< Back", command=self.on_back, state="disabled")
        self.btn_back.pack(side="left", padx=5, pady=5)
        
        self.btn_fwd = ttk.Button(navbar, text="Forward >", command=self.on_forward, state="disabled")
        self.btn_fwd.pack(side="left", padx=5, pady=5)

        # Quick Links
        ttk.Button(navbar, text="Dashboard", command=self.go_to_dashboard).pack(side="right", padx=5)
        ttk.Button(navbar, text="Search", command=self.go_to_search).pack(side="right", padx=5)
        ttk.Button(navbar, text="Logout", command=self.go_to_login).pack(side="right", padx=5)

    def _update_nav_buttons(self):
        """ Enables/Disables Back/Forward buttons based on history stack state """
        # Can we go back?
        if self.history_index > 0:
            self.btn_back.config(state="normal")
        else:
            self.btn_back.config(state="disabled")

        # Can we go forward?
        if self.history_index < len(self.history_stack) - 1:
            self.btn_fwd.config(state="normal")
        else:
            self.btn_fwd.config(state="disabled")


# ==========================================
# DUMMY MAIN FOR TESTING
# Run this script directly to test the navigation.
# ==========================================
if __name__ == "__main__":
    # Pass None for managers just for UI testing
    app = UIManager(auth_manager=None, product_manager=None)
    app.run()