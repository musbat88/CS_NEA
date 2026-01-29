import tkinter as tk
from tkinter import ttk, messagebox

class BasePage(tk.Frame):
    """ A generic page that all other pages inherit from. """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # controller is essentially the UI manager
        self.controller = controller
        self.configure(bg='#f0f0f0', padx=20, pady=20)

class LoginPage(BasePage):
    def __init__(self, parent, controller, data=None):
        super().__init__(parent, controller)
        
        tk.Label(self, text="Login to Price Tracker", font=("Arial", 24), bg='#f0f0f0').pack(pady=20)

        tk.Label(self, text="Username", bg='#f0f0f0').pack()
        self.username_entry = ttk.Entry(self, width=30)
        self.username_entry.pack(pady=5)

        tk.Label(self, text="Password", bg='#f0f0f0').pack()
        self.password_entry = ttk.Entry(self, show="*", width=30)
        self.password_entry.pack(pady=5)

        button_container = tk.Frame(self, bg='#f0f0f0')
        button_container.pack(pady=20)

        ttk.Button(button_container, text="Login", command=self.handle_login).pack(side="left", padx=5)
        ttk.Button(button_container, text="Register", command=self.handle_register).pack(side="left", padx=5)

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        user_id = self.controller.auth_manager.verify_user(username, password)
        
        if user_id is not None: 
            messagebox.showinfo("Login Success", f"Welcome back, {username}!")
            self.controller.login_success(user_id, username) 
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def handle_register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both a username and password.")
            return

        success = self.controller.auth_manager.create_user(username, password)
        
        if success:
            messagebox.showinfo("Registration Success", "Account created! You can now log in.")
        else:
            messagebox.showerror("Error", "Username already exists.")

class SearchPage(BasePage):
    def __init__(self, parent, controller, data=None):
        super().__init__(parent, controller)
        tk.Label(self, text="Search Products", font=("Arial", 24)).pack(pady=20)
        
        search_var = tk.StringVar()
        entry = ttk.Entry(self, textvariable=search_var, width=30)
        entry.pack(pady=10)
        
        ttk.Button(self, text="Search", 
                   command=lambda: controller.go_to_results(search_var.get())).pack()

class ResultsPage(BasePage):
    def __init__(self, parent, controller, data=None):
        super().__init__(parent, controller)
        self.query = data if data else ""
        
        tk.Label(self, text=f"Results for: '{self.query}'", font=("Arial", 22), bg='#f0f0f0').pack(pady=10)

        self.canvas = tk.Canvas(self, bg='#f0f0f0', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#f0f0f0')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.display_results()

    def display_results(self):
        results = self.controller.product_manager.update_and_search(self.query)

        if not results:
            tk.Label(self.scrollable_frame, text="No products found in database.", 
                     font=("Arial", 12), bg='#f0f0f0').pack(pady=20)
            return

        for product in results:
            name, website, price, url = product[2], product[3], product[4], product[1]

            card = tk.Frame(self.scrollable_frame, bd=1, relief="solid", bg="white", padx=15, pady=10)
            card.pack(fill="x", pady=5, padx=10)

            tk.Label(card, text=name, font=("Arial", 12, "bold"), bg="white", wraplength=500, justify="left").pack(anchor="w")
            tk.Label(card, text=f"Store: {website} | Price: £{price:.2f}", font=("Arial", 10), bg="white").pack(anchor="w")

            button_frame = tk.Frame(card, bg="white")
            button_frame.pack(side="right")

            ttk.Button(button_frame, text="Save", 
                       command=lambda p_id=product[0]: self.save_item(p_id)).pack(side="top", pady=2)
            
            ttk.Button(button_frame, text="View URL", 
                       command=lambda u=url: print(f"Link: {u}")).pack(side="top", pady=2)
            
    def save_item(self, product_id):
        user_id = self.controller.current_user_id
        if user_id is None:
            messagebox.showerror("Error", "You must be logged in to save items.")
            return
            
        success = self.controller.product_manager.save_product(user_id, product_id)
        if success:
            messagebox.showinfo("Saved", "Item added to your Dashboard!")
        else:
            messagebox.showinfo("Info", "You have already saved this item.")

class DashboardPage(BasePage):
    def __init__(self, parent, controller, data=None):
        super().__init__(parent, controller)
        tk.Label(self, text="My Saved Items", font=("Arial", 24), bg='#f0f0f0').pack(pady=20)

        self.list_frame = tk.Frame(self, bg='#f0f0f0')
        self.list_frame.pack(fill="both", expand=True)
        
        self.load_dashboard()

    def load_dashboard(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        user_id = self.controller.current_user_id
        saved_items = self.controller.product_manager.get_user_dashboard(user_id)

        if not saved_items:
            tk.Label(self.list_frame, text="You haven't saved any items yet.", bg='#f0f0f0').pack(pady=20)
        else:
            for item in saved_items:
                p_id, url, name, website, price = item[0], item[1], item[2], item[3], item[4]
                
                card = tk.Frame(self.list_frame, bd=1, relief="solid", bg="white", padx=10, pady=5)
                card.pack(fill="x", pady=5, padx=20)
                
                tk.Label(card, text=name, font=("Arial", 11, "bold"), bg="white", wraplength=400, justify="left").pack(side="left", padx=5)
                tk.Label(card, text=f"£{price:.2f}", font=("Arial", 11), fg="green", bg="white").pack(side="left", padx=5)

                btn_frame = tk.Frame(card, bg="white")
                btn_frame.pack(side="right")

                ttk.Button(btn_frame, text="Remove", 
                           command=lambda id=p_id: self.handle_remove(id)).pack(side="right", padx=2)
                
                ttk.Button(btn_frame, text="Link", 
                           command=lambda u=url: print(f"Opening: {u}")).pack(side="right", padx=2)
        
    def handle_remove(self, product_id):
        user_id = self.controller.current_user_id
        if self.controller.product_manager.remove_saved_product(user_id, product_id):
            self.load_dashboard()

class UIManager:
    def __init__(self, auth_manager, product_manager):
        self.root = tk.Tk()
        self.root.title("Python Price Tracker")
        self.root.geometry("800x600")
        style = ttk.Style()
        style.theme_use('clam') 

        self.auth_manager = auth_manager
        self.product_manager = product_manager
        self.current_user_id = None
        self.current_username = None

        self.container = tk.Frame(self.root)
        self.container.pack(side="top", fill="both", expand=True)
        self.current_frame = None
        
        self.history_stack = []
        self.history_index = -1

        self._build_navbar()

        self.go_to_login()

    def run(self):
        """ Starts the Tkinter event loop """
        self.root.mainloop()

    def _navigate_to(self, PageClass, data=None):
        if self.history_index < len(self.history_stack) - 1:
            self.history_stack = self.history_stack[:self.history_index+1]

        self.history_stack.append((PageClass, data))
        self.history_index += 1
        
        self._show_frame(PageClass, data)
        self._update_nav_buttons()

    def _show_frame(self, PageClass, data=None):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = PageClass(parent=self.container, controller=self, data=data)
        
        self.current_frame.pack(fill="both", expand=True)

    def go_to_login(self):
        
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
        if self.current_user_id is None:
            messagebox.showwarning("Access Denied", "Please login to view your dashboard.")
            self.go_to_login()
        else:
            self._navigate_to(DashboardPage)

    
    def on_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            PageClass, data = self.history_stack[self.history_index]
            self._show_frame(PageClass, data)
            self._update_nav_buttons()

    def on_forward(self):
        if self.history_index < len(self.history_stack) - 1:
            self.history_index += 1
            PageClass, data = self.history_stack[self.history_index]
            self._show_frame(PageClass, data)
            self._update_nav_buttons()

    def _build_navbar(self):
        """ Creates the top navigation bar persistent across pages """
        navbar = tk.Frame(self.root, bg="#ddd", height=40)
        navbar.pack(side="top", fill="x")

        self.btn_back = ttk.Button(navbar, text="< Back", command=self.on_back, state="disabled")
        self.btn_back.pack(side="left", padx=5, pady=5)
        
        self.btn_fwd = ttk.Button(navbar, text="Forward >", command=self.on_forward, state="disabled")
        self.btn_fwd.pack(side="left", padx=5, pady=5)

        self.user_label = tk.Label(navbar, text="Not Logged In", bg="#ddd", fg="#555")
        self.user_label.pack(side="left", padx=20)

        ttk.Button(navbar, text="Dashboard", command=self.go_to_dashboard).pack(side="right", padx=5)
        ttk.Button(navbar, text="Search", command=self.go_to_search).pack(side="right", padx=5)
        ttk.Button(navbar, text="Logout", command=self.logout).pack(side="right", padx=5)

    def _update_nav_buttons(self):
        if self.history_index > 0:
            self.btn_back.config(state="normal")
        else:
            self.btn_back.config(state="disabled")

        if self.history_index < len(self.history_stack) - 1:
            self.btn_fwd.config(state="normal")
        else:
            self.btn_fwd.config(state="disabled")

    def login_success(self, user_id, username):
        self.current_user_id = user_id
        self.current_username = username
        
        self.user_label.config(text=f"Logged in as: {username}", fg="green")
        
        self.history_stack = []
        self.history_index = -1
        
        self._navigate_to(SearchPage)

    def logout(self):
        self.current_user_id = None
        self.current_username = None
        
        self.user_label.config(text="Not Logged In", fg="#555")
        
        self.go_to_login()