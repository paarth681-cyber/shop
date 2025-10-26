"""
Shop Manager Pro — Enterprise Edition
A complete business management solution
"""

import os
import sqlite3
import csv
import json
import logging
from datetime import datetime, date
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from PIL import Image, ImageTk
import qrcode
import babel.numbers
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

# Constants
DB_FILE = "shop.db"
BACKUP_DIR = "backups"
LOG_FILE = "shop.log"
REPORT_DIR = "reports"
CURRENCY = "USD"

def money(v):
    try:
        v_float = float(v or 0.0)
    except Exception:
        v_float = 0.0
    return f"${v_float:,.2f}"

def get_conn():
    return sqlite3.connect(DB_FILE)

def log_activity(user_id, action, details):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO audit_log (date, user_id, action, details)
            VALUES (?, ?, ?, ?)
        """, (datetime.now().isoformat(), user_id, action, details))
        conn.commit()
    except Exception as ex:
        logging.error(f"Failed to log activity: {ex}")
    finally:
        conn.close()

def generate_barcode(text):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(text)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

class ModernTheme:
    THEMES = {
        "Blue": {"bg": "#EAF2FF", "accent": "#2B6CB0", "fg": "#1F2937"},
        "Dark": {"bg": "#1A202C", "accent": "#4299E1", "fg": "#FFFFFF"},
        "Light": {"bg": "#FFFFFF", "accent": "#3182CE", "fg": "#1A202C"},
        "Corporate": {"bg": "#F7FAFC", "accent": "#2C5282", "fg": "#2D3748"}
    }
    
    @staticmethod
    def apply(widget, theme):
        # Apply modern styling to widgets
        pass

class ShopApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Shop Manager Pro")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # Initialize logging
        logging.basicConfig(filename=LOG_FILE, level=logging.INFO)
        
        # Setup UI
        self._setup_styles()
        self._setup_login()
        
        # Auto backup
        self._schedule_backup()

    def _setup_styles(self):
        # Modern ttk styling
        style = ttk.Style(self)
        style.configure("Modern.TButton",
                       padding=10,
                       relief="flat",
                       background="#2B6CB0")

    def apply_theme(self, theme_name):
        theme = self.THEMES.get(theme_name)
        if not theme:
            return
        
        style = self.style
        style.configure(".", background=theme["bg"], foreground=theme["fg"])
        style.configure("TButton", background=theme["accent"], foreground="white")
        style.configure("Accent.TButton", background=theme["accent"], foreground="white")
        style.configure("TNotebook", background=theme["bg"])
        style.configure("TFrame", background=theme["bg"])
        style.configure("TopBar.TFrame", background=theme["accent"])
        
        self.current_theme = theme_name
        self.configure(bg=theme["bg"])

    def _setup_login(self):
        for w in self.winfo_children(): 
            w.destroy()
        
        frm = ttk.Frame(self, padding=20)
        frm.pack(expand=True)
        
        # Logo and title
        logo_frame = ttk.Frame(frm)
        logo_frame.grid(row=0, column=0, columnspan=2, pady=(0,20))
        ttk.Label(logo_frame, text="Shop Manager Pro", 
                 font=("Segoe UI", 24, "bold")).pack()
        ttk.Label(logo_frame, text="Enterprise Edition", 
                 font=("Segoe UI", 12)).pack()
        
        # Login fields
        ttk.Label(frm, text="Username:").grid(row=1, column=0, 
                                            sticky="e", padx=5, pady=5)
        uentry = ttk.Entry(frm)
        uentry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(frm, text="Password:").grid(row=2, column=0, 
                                            sticky="e", padx=5, pady=5)
        pentry = ttk.Entry(frm, show="*")
        pentry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        def attempt_login():
            user = uentry.get().strip()
            pw = pentry.get().strip()
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("SELECT id, role FROM users WHERE username=? AND password=?", 
                       (user, pw))
            r = cur.fetchone()
            conn.close()
            
            if r:
                self.user_id = r[0]
                self.username = user
                self.user_role = r[1]
                logging.info(f"User logged in: {user} ({r[1]})")
                self._setup_main()
            else:
                messagebox.showerror("Login Failed", 
                                   "Invalid credentials. Try 'admin'/'admin'.")
        
        login_btn = ttk.Button(frm, text="Login", command=attempt_login, 
                              style="Accent.TButton")
        login_btn.grid(row=3, column=0, columnspan=2, pady=15)
        
        # Version info
        ttk.Label(frm, text="Version 2.0", font=("Segoe UI", 8)).grid(
            row=4, column=0, columnspan=2, pady=(20,0))
        
        # Bind Enter key
        self.bind('<Return>', lambda e: attempt_login())
        uentry.focus()
    def _setup_main(self):
        for w in self.winfo_children(): 
            w.destroy()
        
        # Top bar
        topbar = ttk.Frame(self, style="TopBar.TFrame")
        topbar.pack(fill="x")
        
        # Left side - Title and user info
        title_frame = ttk.Frame(topbar)
        title_frame.pack(side="left", padx=10)
        ttk.Label(title_frame, text="Shop Manager Pro", 
                 font=("Segoe UI", 16, "bold")).pack(side="left", padx=10)
        ttk.Label(title_frame, 
                 text=f"User: {self.username} ({self.user_role})", 
                 font=("Segoe UI", 10)).pack(side="left")
        
        # Right side - Controls
        controls = ttk.Frame(topbar)
        controls.pack(side="right", padx=10)
        
        # Theme selector
        ttk.Label(controls, text="Theme:").pack(side="left", padx=(6,2))
        theme_cb = ttk.Combobox(controls, values=list(ModernTheme.THEMES.keys()), 
                               state="readonly", width=10)
        theme_cb.set("Light")  # Default theme
        theme_cb.pack(side="left", padx=4)
        theme_cb.bind("<<ComboboxSelected>>", 
                     lambda e: self.apply_theme(theme_cb.get()))
        
        # Other controls
        ttk.Button(controls, text="Backup", 
                  command=self._manual_backup).pack(side="left", padx=4)
        ttk.Button(controls, text="Logout", 
                  command=self._setup_login).pack(side="left", padx=4)
        
        # Main notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initialize tabs
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.pos_tab = ttk.Frame(self.notebook)
        self.inventory_tab = ttk.Frame(self.notebook)
        self.customers_tab = ttk.Frame(self.notebook)
        self.suppliers_tab = ttk.Frame(self.notebook)
        self.orders_tab = ttk.Frame(self.notebook)
        self.expenses_tab = ttk.Frame(self.notebook)
        self.reports_tab = ttk.Frame(self.notebook)
        
        # Add tabs based on role
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.pos_tab, text="Point of Sale")
        self.notebook.add(self.inventory_tab, text="Inventory")
        self.notebook.add(self.customers_tab, text="Customers")
        
        if self.user_role == "admin":
            self.notebook.add(self.suppliers_tab, text="Suppliers")
            self.notebook.add(self.orders_tab, text="Orders")
            self.notebook.add(self.expenses_tab, text="Expenses")
            self.notebook.add(self.reports_tab, text="Reports")
        
        # Build each tab
        self._build_dashboard()
        self._build_pos()
        self._build_inventory()
        self._build_customers()
        
        if self.user_role == "admin":
            self._build_suppliers()
            self._build_orders()
            self._build_expenses()
            self._build_reports()
    
        
        # Build each tab
        self._build_dashboard()
    def _build_pos(self):
        frm = self.pos_tab
        for w in frm.winfo_children(): 
            w.destroy()
        
        # Split into left (cart) and right (products) panels
        left_panel = ttk.Frame(frm)
        left_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        right_panel = ttk.Frame(frm)
        right_panel.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Left panel - Cart
        cart_frame = ttk.LabelFrame(left_panel, text="Shopping Cart")
        cart_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Cart tree
        self.cart_tree = ttk.Treeview(cart_frame, 
            columns=("id", "name", "qty", "price", "total"),
            show="headings",
            height=10)
        
        self.cart_tree.heading("id", text="ID")
        self.cart_tree.heading("name", text="Product")
        self.cart_tree.heading("qty", text="Quantity")
        self.cart_tree.heading("price", text="Price")
        self.cart_tree.heading("total", text="Total")
        
        self.cart_tree.column("id", width=50)
        self.cart_tree.column("name", width=200)
        self.cart_tree.column("qty", width=70)
        self.cart_tree.column("price", width=100)
        self.cart_tree.column("total", width=100)
        
        self.cart_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Cart controls
        cart_controls = ttk.Frame(cart_frame)
        cart_controls.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(cart_controls, text="Remove Item", 
                  command=self._remove_cart_item).pack(side="left", padx=2)
        ttk.Button(cart_controls, text="Clear Cart", 
                  command=self._clear_cart).pack(side="left", padx=2)
        
        # Cart summary
        summary = ttk.Frame(left_panel)
        summary.pack(fill="x", padx=5, pady=5)
        
        # Customer selection
        cust_frame = ttk.Frame(summary)
        cust_frame.pack(fill="x", pady=5)
        ttk.Label(cust_frame, text="Customer:").pack(side="left", padx=5)
        self.customer_cb = ttk.Combobox(cust_frame, width=30)
        self.customer_cb.pack(side="left", padx=5)
        
        # Load customers
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM customers ORDER BY name")
        self.customers = {f"{id}: {name}": id for id, name in cur.fetchall()}
        self.customer_cb['values'] = list(self.customers.keys())
        self.customer_cb.set("1: Walk-in Customer")
        conn.close()
        
        # Totals
        totals_frame = ttk.Frame(summary)
        totals_frame.pack(fill="x", pady=5)
        
        self.subtotal_var = tk.StringVar(value="$0.00")
        self.tax_var = tk.StringVar(value="$0.00")
        self.total_var = tk.StringVar(value="$0.00")
        
        ttk.Label(totals_frame, text="Subtotal:").pack(side="left", padx=5)
        ttk.Label(totals_frame, textvariable=self.subtotal_var).pack(side="left", padx=5)
        ttk.Label(totals_frame, text="Tax:").pack(side="left", padx=5)
        ttk.Label(totals_frame, textvariable=self.tax_var).pack(side="left", padx=5)
        ttk.Label(totals_frame, text="Total:").pack(side="left", padx=5)
        ttk.Label(totals_frame, textvariable=self.total_var, 
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=5)
        
        # Payment button
        ttk.Button(summary, text="Complete Sale", 
                  command=self._complete_sale).pack(fill="x", pady=10)
        
        # Right panel - Products
        # Search frame
        search_frame = ttk.Frame(right_panel)
        search_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self._filter_products())
        ttk.Entry(search_frame, textvariable=self.search_var).pack(
            side="left", fill="x", expand=True, padx=5)
        
        # Products tree
        self.products_tree = ttk.Treeview(right_panel,
            columns=("id", "sku", "name", "price", "stock"),
            show="headings",
            height=20)
        
        self.products_tree.heading("id", text="ID")
        self.products_tree.heading("sku", text="SKU")
        self.products_tree.heading("name", text="Product")
        self.products_tree.heading("price", text="Price")
        self.products_tree.heading("stock", text="Stock")
        
        self.products_tree.column("id", width=50)
        self.products_tree.column("sku", width=100)
        self.products_tree.column("name", width=200)
        self.products_tree.column("price", width=100)
        self.products_tree.column("stock", width=70)
        
        self.products_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Double click to add to cart
        self.products_tree.bind("<Double-1>", self._add_to_cart)
        
        # Load initial products
        self._load_products()

    def _load_products(self):
        self.products_tree.delete(*self.products_tree.get_children())
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, sku, name, sell_price, quantity 
            FROM products 
            ORDER BY name
        """)
        for row in cur.fetchall():
            self.products_tree.insert("", "end", values=row)
        conn.close()
    
    def _filter_products(self):
        search = self.search_var.get().lower()
        self.products_tree.delete(*self.products_tree.get_children())
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, sku, name, sell_price, quantity 
            FROM products 
            WHERE LOWER(name) LIKE ? OR LOWER(sku) LIKE ?
            ORDER BY name
        """, (f"%{search}%", f"%{search}%"))
        for row in cur.fetchall():
            self.products_tree.insert("", "end", values=row)
        conn.close()
    
    def _add_to_cart(self, event=None):
        selection = self.products_tree.selection()
        if not selection:
            return
        
        item = self.products_tree.item(selection[0])
        values = item['values']
        
        # Check stock
        if values[4] <= 0:
            messagebox.showwarning("Out of Stock", 
                                 "This product is out of stock!")
            return
        
        # Ask quantity
        qty = simpledialog.askinteger("Quantity", 
                                     "Enter quantity:", 
                                     minvalue=1, 
                                     maxvalue=values[4])
        if not qty:
            return
        
        # Calculate total
        price = float(values[3])
        total = price * qty
        
        # Add to cart
        self.cart_tree.insert("", "end", 
                           values=(values[0], values[2], qty, 
                                  money(price), money(total)))
        self._update_totals()
    
    def _remove_cart_item(self):
        selection = self.cart_tree.selection()
        if selection:
            self.cart_tree.delete(selection[0])
            self._update_totals()
    
    def _clear_cart(self):
        self.cart_tree.delete(*self.cart_tree.get_children())
        self._update_totals()
    
    def _update_totals(self):
        subtotal = 0
        for item in self.cart_tree.get_children():
            values = self.cart_tree.item(item)['values']
            subtotal += float(values[4].replace('$', '').replace(',', ''))
        
        tax = subtotal * 0.1  # 10% tax
        total = subtotal + tax
        
        self.subtotal_var.set(money(subtotal))
        self.tax_var.set(money(tax))
        self.total_var.set(money(total))
    
    def _complete_sale(self):
        if not self.cart_tree.get_children():
            messagebox.showwarning("Empty Cart", 
                                 "Please add items to cart first!")
            return
        
        # Get customer ID
        customer_selection = self.customer_cb.get()
        customer_id = self.customers[customer_selection]
        
        # Calculate totals
        subtotal = float(self.subtotal_var.get().replace('$', '').replace(',', ''))
        tax = float(self.tax_var.get().replace('$', '').replace(',', ''))
        total = float(self.total_var.get().replace('$', '').replace(',', ''))
        
        # Validate stock levels first
        conn = get_conn()
        cur = conn.cursor()
        try:
            for item in self.cart_tree.get_children():
                values = self.cart_tree.item(item)['values']
                product_id = values[0]
                qty = int(values[2])
                
                cur.execute("SELECT quantity FROM products WHERE id = ?", (product_id,))
                current_stock = cur.fetchone()[0]
                
                if current_stock < qty:
                    messagebox.showerror("Insufficient Stock", 
                                       f"Not enough stock for product ID {product_id}. Available: {current_stock}")
                    return
            
            # Begin transaction
            # Insert sale
            cur.execute("""
                INSERT INTO sales (date, customer_id, total_amount, 
                                 tax_amount, paid_amount, payment_method, 
                                 user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(), customer_id, total, 
                    tax, total, "cash", self.user_id))
            
            sale_id = cur.lastrowid
            
            # Insert sale lines and update stock
            for item in self.cart_tree.get_children():
                values = self.cart_tree.item(item)['values']
                product_id = values[0]
                qty = int(values[2])
                price = float(values[3].replace('$', '').replace(',', ''))
                line_total = float(values[4].replace('$', '').replace(',', ''))
                
                cur.execute("""
                    INSERT INTO sale_lines (sale_id, product_id, qty, 
                                          price, line_total)
                    VALUES (?, ?, ?, ?, ?)
                """, (sale_id, product_id, qty, price, line_total))
                
                # Update stock with proper locking
                cur.execute("""
                    UPDATE products 
                    SET quantity = quantity - ? 
                    WHERE id = ? AND quantity >= ?
                """, (qty, product_id, qty))
                
                if cur.rowcount == 0:
                    raise Exception(f"Stock update failed for product {product_id}")
            
            conn.commit()
            messagebox.showinfo("Success", 
                              f"Sale #{sale_id} completed successfully!\n\nTotal Amount: {money(total)}")
            
            # Log activity
            log_activity(self.user_id, "sale_completed", 
                        f"Sale #{sale_id} for {money(total)}")
            
            # Clear cart and reload products
            self._clear_cart()
            self._load_products()
            
        except Exception as ex:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to complete sale: {ex}")
            logging.error(f"Sale failed: {ex}")
        finally:
            conn.close()
    def _build_inventory(self):
        frm = self.inventory_tab
        for w in frm.winfo_children():
            w.destroy()
        
            # Top controls
            top = ttk.Frame(frm, padding=6)
            top.pack("x")
            ttk.Button(top, text="Add Product", command=self._add_product).pack(side="left", padx=4)
            ttk.Button(top, text="Edit Product", command=self._edit_product).pack(side="left", padx=4)
            ttk.Button(top, text="Delete Product", command=self._delete_product).pack(side="left", padx=4)
            ttk.Button(top, text="Export CSV", command=self._export_products_csv).pack(side="left", padx=4)
        
            # Products list
            tree = ttk.Treeview(frm, columns=("id", "sku", "name", "category", "quantity", "min_quantity", "sell_price", "supplier"), show="headings")
            tree.heading("id", text="ID")
            tree.heading("sku", text="SKU")
            tree.heading("name", text="Name")
            tree.heading("category", text="Category")
            tree.heading("quantity", text="Qty")
            tree.heading("min_quantity", text="Min Qty")
            tree.heading("sell_price", text="Sell Price")
            tree.heading("supplier", text="Supplier")
            tree.column("id", width=50)
            tree.column("sku", width=100)
            tree.column("name", width=180)
            tree.column("category", width=120)
            tree.column("quantity", width=70)
            tree.column("min_quantity", width=70)
            tree.column("sell_price", width=100)
            tree.column("supplier", width=120)
            tree.pack(fill="both", expand=True, padx=8, pady=8)
            self.inventory_tree = tree
            self._refresh_inventory()
        
        def _refresh_inventory(self):
            self.inventory_tree.delete(*self.inventory_tree.get_children())
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""
                SELECT p.id, p.sku, p.name, p.category, p.quantity, p.min_quantity, p.sell_price, s.name
                FROM products p
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                ORDER BY p.name
            """)
            for row in cur.fetchall():
                self.inventory_tree.insert("", "end", values=row)
            conn.close()
        
        def _add_product(self):
            dialog = tk.Toplevel(self)
            dialog.title("Add Product")
            dialog.geometry("400x400")
            dialog.transient(self)
            dialog.grab_set()
        
            fields = [
                ("SKU", tk.StringVar()),
                ("Name", tk.StringVar()),
                ("Description", tk.StringVar()),
                ("Category", tk.StringVar()),
                ("Quantity", tk.IntVar(value=0)),
                ("Min Quantity", tk.IntVar(value=5)),
                ("Cost Price", tk.DoubleVar(value=0.0)),
                ("Sell Price", tk.DoubleVar(value=0.0)),
                ("Supplier ID", tk.IntVar(value=1)),
            ]
            entries = {}
            for i, (label, var) in enumerate(fields):
                ttk.Label(dialog, text=label + ":").grid(row=i, column=0, sticky="e", padx=5, pady=5)
                entry = ttk.Entry(dialog, textvariable=var)
                entry.grid(row=i, column=1, sticky="w", padx=5, pady=5)
                entries[label] = var
        
            def save():
                conn = get_conn()
                cur = conn.cursor()
                try:
                    cur.execute("""
                        INSERT INTO products (sku, name, description, category, quantity, min_quantity, cost_price, sell_price, supplier_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        entries["SKU"].get(),
                        entries["Name"].get(),
                        entries["Description"].get(),
                        entries["Category"].get(),
                        entries["Quantity"].get(),
                        entries["Min Quantity"].get(),
                        entries["Cost Price"].get(),
                        entries["Sell Price"].get(),
                        entries["Supplier ID"].get(),
                    ))
                    conn.commit()
                    self._refresh_inventory()
                    dialog.destroy()
                except Exception as ex:
                    messagebox.showerror("Error", f"Failed to add product: {ex}")
                    conn.rollback()
                finally:
                    conn.close()
        
            ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=10)
        
        def _edit_product(self):
            selection = self.inventory_tree.selection()
            if not selection:
                messagebox.showwarning("Select Product", "Please select a product to edit.")
                return
            item = self.inventory_tree.item(selection[0])
            values = item['values']
        
            dialog = tk.Toplevel(self)
            dialog.title("Edit Product")
            dialog.geometry("400x400")
            dialog.transient(self)
            dialog.grab_set()
        
            fields = [
                ("SKU", tk.StringVar(value=values[1])),
                ("Name", tk.StringVar(value=values[2])),
                ("Description", tk.StringVar()),
                ("Category", tk.StringVar(value=values[3])),
                ("Quantity", tk.IntVar(value=values[4])),
                ("Min Quantity", tk.IntVar(value=values[5])),
                ("Cost Price", tk.DoubleVar()),
                ("Sell Price", tk.DoubleVar(value=values[6])),
                ("Supplier ID", tk.IntVar()),
            ]
            entries = {}
            for i, (label, var) in enumerate(fields):
                ttk.Label(dialog, text=label + ":").grid(row=i, column=0, sticky="e", padx=5, pady=5)
                entry = ttk.Entry(dialog, textvariable=var)
                entry.grid(row=i, column=1, sticky="w", padx=5, pady=5)
                entries[label] = var
        
            def save():
                conn = get_conn()
                cur = conn.cursor()
                try:
                    cur.execute("""
                        UPDATE products SET sku=?, name=?, description=?, category=?, quantity=?, min_quantity=?, cost_price=?, sell_price=?, supplier_id=?
                        WHERE id=?
                    """, (
                        entries["SKU"].get(),
                        entries["Name"].get(),
                        entries["Description"].get(),
                        entries["Category"].get(),
                        entries["Quantity"].get(),
                        entries["Min Quantity"].get(),
                        entries["Cost Price"].get(),
                        entries["Sell Price"].get(),
                        entries["Supplier ID"].get(),
                        values[0]
                    ))
                    conn.commit()
                    self._refresh_inventory()
                    dialog.destroy()
                except Exception as ex:
                    messagebox.showerror("Error", f"Failed to edit product: {ex}")
                    conn.rollback()
                finally:
                    conn.close()
        
            ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=10)
        
        def _delete_product(self):
            selection = self.inventory_tree.selection()
            if not selection:
                messagebox.showwarning("Select Product", "Please select a product to delete.")
                return
            item = self.inventory_tree.item(selection[0])
            product_id = item['values'][0]
            if messagebox.askyesno("Delete Product", "Are you sure you want to delete this product?"):
                conn = get_conn()
                cur = conn.cursor()
                try:
                    cur.execute("DELETE FROM products WHERE id=?", (product_id,))
                    conn.commit()
                    self._refresh_inventory()
                except Exception as ex:
                    messagebox.showerror("Error", f"Failed to delete product: {ex}")
                    conn.rollback()
                finally:
                    conn.close()
        
        def _export_products_csv(self):
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if not file_path:
                return
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""
                SELECT p.id, p.sku, p.name, p.category, p.quantity, p.min_quantity, p.sell_price, s.name
                FROM products p
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                ORDER BY p.name
            """)
            rows = cur.fetchall()
            conn.close()
            try:
                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "SKU", "Name", "Category", "Quantity", "Min Quantity", "Sell Price", "Supplier"])
                    writer.writerows(rows)
                messagebox.showinfo("Export Successful", f"Products exported to {file_path}")
            except Exception as ex:
                messagebox.showerror("Export Failed", f"Failed to export products: {ex}")

    def _build_customers(self):
        frm = self.customers_tab
        for w in frm.winfo_children():
            w.destroy()
    
        # Top controls
        top = ttk.Frame(frm, padding=6)
        top.pack(fill="x")
        ttk.Button(top, text="Add Customer", command=self._add_customer).pack(side="left", padx=4)
        ttk.Button(top, text="Edit Customer", command=self._edit_customer).pack(side="left", padx=4)
        ttk.Button(top, text="Delete Customer", command=self._delete_customer).pack(side="left", padx=4)
        ttk.Button(top, text="Export CSV", command=self._export_customers_csv).pack(side="left", padx=4)
    
        # Customers list
        tree = ttk.Treeview(frm, columns=("id", "name", "phone", "email", "address", "loyalty"), show="headings")
        tree.heading("id", text="ID")
        tree.heading("name", text="Name")
        tree.heading("phone", text="Phone")
        tree.heading("email", text="Email")
        tree.heading("address", text="Address")
        tree.heading("loyalty", text="Loyalty Points")
        tree.column("id", width=50)
        tree.column("name", width=180)
        tree.column("phone", width=120)
        tree.column("email", width=180)
        tree.column("address", width=180)
        tree.column("loyalty", width=100)
        tree.pack(fill="both", expand=True, padx=8, pady=8)
        self.customers_tree = tree
        self._refresh_customers()
    
    def _refresh_customers(self):
        self.customers_tree.delete(*self.customers_tree.get_children())
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT c.id, c.name, c.phone, c.email, c.address, COALESCE(lp.points, 0)
            FROM customers c
            LEFT JOIN loyalty_points lp ON c.id = lp.customer_id
            ORDER BY c.name
        """)
        for row in cur.fetchall():
            self.customers_tree.insert("", "end", values=row)
        conn.close()
    
    def _add_customer(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add Customer")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
    
        fields = [
            ("Name", tk.StringVar()),
            ("Phone", tk.StringVar()),
            ("Email", tk.StringVar()),
            ("Address", tk.StringVar()),
        ]
        entries = {}
        for i, (label, var) in enumerate(fields):
            ttk.Label(dialog, text=label + ":").grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entry = ttk.Entry(dialog, textvariable=var)
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=5)
            entries[label] = var
    
        def save():
            conn = get_conn()
            cur = conn.cursor()
            try:
                cur.execute("""
                    INSERT INTO customers (name, phone, email, address)
                    VALUES (?, ?, ?, ?)
                """, (
                    entries["Name"].get(),
                    entries["Phone"].get(),
                    entries["Email"].get(),
                    entries["Address"].get(),
                ))
                conn.commit()
                self._refresh_customers()
                dialog.destroy()
            except Exception as ex:
                messagebox.showerror("Error", f"Failed to add customer: {ex}")
                conn.rollback()
            finally:
                conn.close()
    
        ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=10)
    
    def _edit_customer(self):
        selection = self.customers_tree.selection()
        if not selection:
            messagebox.showwarning("Select Customer", "Please select a customer to edit.")
            return
        item = self.customers_tree.item(selection[0])
        values = item['values']
    
        dialog = tk.Toplevel(self)
        dialog.title("Edit Customer")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
    
        fields = [
            ("Name", tk.StringVar(value=values[1])),
            ("Phone", tk.StringVar(value=values[2])),
            ("Email", tk.StringVar(value=values[3])),
            ("Address", tk.StringVar(value=values[4])),
        ]
        entries = {}
        for i, (label, var) in enumerate(fields):
            ttk.Label(dialog, text=label + ":").grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entry = ttk.Entry(dialog, textvariable=var)
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=5)
            entries[label] = var
    
        def save():
            conn = get_conn()
            cur = conn.cursor()
            try:
                cur.execute("""
                    UPDATE customers SET name=?, phone=?, email=?, address=?
                    WHERE id=?
                """, (
                    entries["Name"].get(),
                    entries["Phone"].get(),
                    entries["Email"].get(),
                    entries["Address"].get(),
                    values[0]
                ))
                conn.commit()
                self._refresh_customers()
                dialog.destroy()
            except Exception as ex:
                messagebox.showerror("Error", f"Failed to edit customer: {ex}")
                conn.rollback()
            finally:
                conn.close()
    
        ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=10)
    
    def _delete_customer(self):
        selection = self.customers_tree.selection()
        if not selection:
            messagebox.showwarning("Select Customer", "Please select a customer to delete.")
            return
        item = self.customers_tree.item(selection[0])
        customer_id = item['values'][0]
        if messagebox.askyesno("Delete Customer", "Are you sure you want to delete this customer?"):
            conn = get_conn()
            cur = conn.cursor()
            try:
                cur.execute("DELETE FROM customers WHERE id=?", (customer_id,))
                conn.commit()
                self._refresh_customers()
            except Exception as ex:
                messagebox.showerror("Error", f"Failed to delete customer: {ex}")
                conn.rollback()
            finally:
                conn.close()
    
    def _export_customers_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT c.id, c.name, c.phone, c.email, c.address, COALESCE(lp.points, 0)
            FROM customers c
            LEFT JOIN loyalty_points lp ON c.id = lp.customer_id
            ORDER BY c.name
        """)
        rows = cur.fetchall()
        conn.close()
        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Name", "Phone", "Email", "Address", "Loyalty Points"])
                writer.writerows(rows)
            messagebox.showinfo("Export Successful", f"Customers exported to {file_path}")
        except Exception as ex:
            messagebox.showerror("Export Failed", f"Failed to export customers: {ex}")

    def _build_suppliers(self):
        frm = self.suppliers_tab
        for w in frm.winfo_children():
            w.destroy()

        # Top controls
        top = ttk.Frame(frm, padding=6)
        top.pack(fill="x")
        ttk.Button(top, text="Add Supplier", command=self._add_supplier).pack(side="left", padx=4)
        ttk.Button(top, text="Edit Supplier", command=self._edit_supplier).pack(side="left", padx=4)
        ttk.Button(top, text="Delete Supplier", command=self._delete_supplier).pack(side="left", padx=4)
        ttk.Button(top, text="Export CSV", command=self._export_suppliers_csv).pack(side="left", padx=4)

        # Suppliers list
        tree = ttk.Treeview(frm, columns=("id", "name", "contact", "phone", "email", "address"), show="headings")
        tree.heading("id", text="ID")
        tree.heading("name", text="Name")
        tree.heading("contact", text="Contact Person")
        tree.heading("phone", text="Phone")
        tree.heading("email", text="Email")
        tree.heading("address", text="Address")
        tree.column("id", width=50)
        tree.column("name", width=180)
        tree.column("contact", width=120)
        tree.column("phone", width=120)
        tree.column("email", width=180)
        tree.column("address", width=180)
        tree.pack(fill="both", expand=True, padx=8, pady=8)
        self.suppliers_tree = tree
        self._refresh_suppliers()

    def _refresh_suppliers(self):
        self.suppliers_tree.delete(*self.suppliers_tree.get_children())
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, contact_person, phone, email, address
            FROM suppliers
            ORDER BY name
        """)
        for row in cur.fetchall():
            self.suppliers_tree.insert("", "end", values=row)
        conn.close()

    def _add_supplier(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add Supplier")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()

        fields = [
            ("Name", tk.StringVar()),
            ("Contact Person", tk.StringVar()),
            ("Phone", tk.StringVar()),
            ("Email", tk.StringVar()),
            ("Address", tk.StringVar()),
        ]
        entries = {}
        for i, (label, var) in enumerate(fields):
            ttk.Label(dialog, text=label + ":").grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entry = ttk.Entry(dialog, textvariable=var)
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=5)
            entries[label] = var

        def save():
            conn = get_conn()
            cur = conn.cursor()
            try:
                cur.execute("""
                    INSERT INTO suppliers (name, contact_person, phone, email, address)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    entries["Name"].get(),
                    entries["Contact Person"].get(),
                    entries["Phone"].get(),
                    entries["Email"].get(),
                    entries["Address"].get(),
                ))
                conn.commit()
                self._refresh_suppliers()
                dialog.destroy()
            except Exception as ex:
                messagebox.showerror("Error", f"Failed to add supplier: {ex}")
                conn.rollback()
            finally:
                conn.close()

        ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def _edit_supplier(self):
        selection = self.suppliers_tree.selection()
        if not selection:
            messagebox.showwarning("Select Supplier", "Please select a supplier to edit.")
            return
        item = self.suppliers_tree.item(selection[0])
        values = item['values']

        dialog = tk.Toplevel(self)
        dialog.title("Edit Supplier")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()

        fields = [
            ("Name", tk.StringVar(value=values[1])),
            ("Contact Person", tk.StringVar(value=values[2])),
            ("Phone", tk.StringVar(value=values[3])),
            ("Email", tk.StringVar(value=values[4])),
            ("Address", tk.StringVar(value=values[5])),
        ]
        entries = {}
        for i, (label, var) in enumerate(fields):
            ttk.Label(dialog, text=label + ":").grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entry = ttk.Entry(dialog, textvariable=var)
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=5)
            entries[label] = var

        def save():
            conn = get_conn()
            cur = conn.cursor()
            try:
                cur.execute("""
                    UPDATE suppliers SET name=?, contact_person=?, phone=?, email=?, address=?
                    WHERE id=?
                """, (
                    entries["Name"].get(),
                    entries["Contact Person"].get(),
                    entries["Phone"].get(),
                    entries["Email"].get(),
                    entries["Address"].get(),
                    values[0]
                ))
                conn.commit()
                self._refresh_suppliers()
                dialog.destroy()
            except Exception as ex:
                messagebox.showerror("Error", f"Failed to edit supplier: {ex}")
                conn.rollback()
            finally:
                conn.close()

        ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def _delete_supplier(self):
        selection = self.suppliers_tree.selection()
        if not selection:
            messagebox.showwarning("Select Supplier", "Please select a supplier to delete.")
            return
        item = self.suppliers_tree.item(selection[0])
        supplier_id = item['values'][0]
        if messagebox.askyesno("Delete Supplier", "Are you sure you want to delete this supplier?"):
            conn = get_conn()
            cur = conn.cursor()
            try:
                cur.execute("DELETE FROM suppliers WHERE id=?", (supplier_id,))
                conn.commit()
                self._refresh_suppliers()
            except Exception as ex:
                messagebox.showerror("Error", f"Failed to delete supplier: {ex}")
                conn.rollback()
            finally:
                conn.close()

    def _export_suppliers_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, contact_person, phone, email, address
            FROM suppliers
            ORDER BY name
        """)
        rows = cur.fetchall()
        conn.close()
        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Name", "Contact Person", "Phone", "Email", "Address"])
                writer.writerows(rows)
            messagebox.showinfo("Export Successful", f"Suppliers exported to {file_path}")
        except Exception as ex:
            messagebox.showerror("Export Failed", f"Failed to export suppliers: {ex}")
    def _build_orders(self):
        frm = self.orders_tab
        for w in frm.winfo_children():
            w.destroy()

        # Top controls
        top = ttk.Frame(frm, padding=6)
        top.pack(fill="x")
        ttk.Button(top, text="Add Order", command=self._add_order).pack(side="left", padx=4)
        ttk.Button(top, text="Edit Order", command=self._edit_order).pack(side="left", padx=4)
        ttk.Button(top, text="Delete Order", command=self._delete_order).pack(side="left", padx=4)
        ttk.Button(top, text="Export CSV", command=self._export_orders_csv).pack(side="left", padx=4)

        # Orders list
        tree = ttk.Treeview(frm, columns=("id", "date", "supplier", "total", "status"), show="headings")
        tree.heading("id", text="ID")
        tree.heading("date", text="Date")
        tree.heading("supplier", text="Supplier")
        tree.heading("total", text="Total Amount")
        tree.heading("status", text="Status")
        tree.column("id", width=50)
        tree.column("date", width=120)
        tree.column("supplier", width=180)
        tree.column("total", width=120)
        tree.column("status", width=100)
        tree.pack(fill="both", expand=True, padx=8, pady=8)
        self.orders_tree = tree
        self._refresh_orders()

    def _refresh_orders(self):
        self.orders_tree.delete(*self.orders_tree.get_children())
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT o.id, o.date, s.name, o.total_amount, o.status
            FROM orders o
            LEFT JOIN suppliers s ON o.supplier_id = s.id
            ORDER BY o.date DESC
        """)
        for row in cur.fetchall():
            self.orders_tree.insert("", "end", values=row)
        conn.close()

    def _add_order(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add Order")
        dialog.geometry("400x350")
        dialog.transient(self)
        dialog.grab_set()

        # Supplier selection
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM suppliers ORDER BY name")
        suppliers = {f"{id}: {name}": id for id, name in cur.fetchall()}
        conn.close()

        supplier_var = tk.StringVar()
        total_var = tk.DoubleVar(value=0.0)
        status_var = tk.StringVar(value="Pending")

        ttk.Label(dialog, text="Supplier:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        supplier_cb = ttk.Combobox(dialog, values=list(suppliers.keys()), textvariable=supplier_var, width=30)
        supplier_cb.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(dialog, text="Total Amount:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(dialog, textvariable=total_var).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(dialog, text="Status:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        status_cb = ttk.Combobox(dialog, values=["Pending", "Received", "Cancelled"], textvariable=status_var, width=15)
        status_cb.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        def save():
            conn = get_conn()
            cur = conn.cursor()
            try:
                cur.execute("""
                    INSERT INTO orders (date, supplier_id, total_amount, status)
                    VALUES (?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    suppliers[supplier_var.get()],
                    total_var.get(),
                    status_var.get(),
                ))
                conn.commit()
                self._refresh_orders()
                dialog.destroy()
            except Exception as ex:
                messagebox.showerror("Error", f"Failed to add order: {ex}")
                conn.rollback()
            finally:
                conn.close()

        ttk.Button(dialog, text="Save", command=save).grid(row=3, column=0, columnspan=2, pady=10)

    def _edit_order(self):
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("Select Order", "Please select an order to edit.")
            return
        item = self.orders_tree.item(selection[0])
        values = item['values']

        dialog = tk.Toplevel(self)
        dialog.title("Edit Order")
        dialog.geometry("400x350")
        dialog.transient(self)
        dialog.grab_set()

        # Supplier selection
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM suppliers ORDER BY name")
        suppliers = {f"{id}: {name}": id for id, name in cur.fetchall()}
        conn.close()

        supplier_var = tk.StringVar(value=values[2])
        total_var = tk.DoubleVar(value=values[3])
        status_var = tk.StringVar(value=values[4])

        ttk.Label(dialog, text="Supplier:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        supplier_cb = ttk.Combobox(dialog, values=list(suppliers.keys()), textvariable=supplier_var, width=30)
        supplier_cb.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(dialog, text="Total Amount:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(dialog, textvariable=total_var).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(dialog, text="Status:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        status_cb = ttk.Combobox(dialog, values=["Pending", "Received", "Cancelled"], textvariable=status_var, width=15)
        status_cb.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        def save():
            conn = get_conn()
            cur = conn.cursor()
            try:
                cur.execute("""
                    UPDATE orders SET supplier_id=?, total_amount=?, status=?
                    WHERE id=?
                """, (
                    suppliers[supplier_var.get()],
                    total_var.get(),
                    status_var.get(),
                    values[0]
                ))
                conn.commit()
                self._refresh_orders()
                dialog.destroy()
            except Exception as ex:
                messagebox.showerror("Error", f"Failed to edit order: {ex}")
                conn.rollback()
            finally:
                conn.close()

        ttk.Button(dialog, text="Save", command=save).grid(row=3, column=0, columnspan=2, pady=10)

    def _delete_order(self):
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("Select Order", "Please select an order to delete.")
            return
        item = self.orders_tree.item(selection[0])
        order_id = item['values'][0]
        if messagebox.askyesno("Delete Order", "Are you sure you want to delete this order?"):
            conn = get_conn()
            cur = conn.cursor()
            try:
                cur.execute("DELETE FROM orders WHERE id=?", (order_id,))
                conn.commit()
                self._refresh_orders()
            except Exception as ex:
                messagebox.showerror("Error", f"Failed to delete order: {ex}")
                conn.rollback()
            finally:
                conn.close()

    def _export_orders_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT o.id, o.date, s.name, o.total_amount, o.status
            FROM orders o
            LEFT JOIN suppliers s ON o.supplier_id = s.id
            ORDER BY o.date DESC
        """)
        rows = cur.fetchall()
        conn.close()
        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Date", "Supplier", "Total Amount", "Status"])
                writer.writerows(rows)
            messagebox.showinfo("Export Successful", f"Orders exported to {file_path}")
        except Exception as ex:
            messagebox.showerror("Export Failed", f"Failed to export orders: {ex}")
    def _build_expenses(self):
        frm = self.expenses_tab
        for w in frm.winfo_children():
            w.destroy()

        # Top controls
        top = ttk.Frame(frm, padding=6)
        top.pack(fill="x")
        ttk.Button(top, text="Add Expense", command=self._add_expense).pack(side="left", padx=4)
        ttk.Button(top, text="Edit Expense", command=self._edit_expense).pack(side="left", padx=4)
        ttk.Button(top, text="Delete Expense", command=self._delete_expense).pack(side="left", padx=4)
        ttk.Button(top, text="Export CSV", command=self._export_expenses_csv).pack(side="left", padx=4)

        # Expenses list
        tree = ttk.Treeview(frm, columns=("id", "date", "category", "amount", "description", "user"), show="headings")
        tree.heading("id", text="ID")
        tree.heading("date", text="Date")
        tree.heading("category", text="Category")
        tree.heading("amount", text="Amount")
        tree.heading("description", text="Description")
        tree.heading("user", text="User")
        tree.column("id", width=50)
        tree.column("date", width=120)
        tree.column("category", width=120)
        tree.column("amount", width=100)
        tree.column("description", width=200)
        tree.column("user", width=120)
        tree.pack(fill="both", expand=True, padx=8, pady=8)
        self.expenses_tree = tree
        self._refresh_expenses()

    def _refresh_expenses(self):
        self.expenses_tree.delete(*self.expenses_tree.get_children())
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT e.id, e.date, e.category, e.amount, e.description, u.username
            FROM expenses e
            LEFT JOIN users u ON e.user_id = u.id
            ORDER BY e.date DESC
        """)
        for row in cur.fetchall():
            self.expenses_tree.insert("", "end", values=row)
        conn.close()

    def _add_expense(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add Expense")
        dialog.geometry("400x350")
        dialog.transient(self)
        dialog.grab_set()

        category_var = tk.StringVar()
        amount_var = tk.DoubleVar(value=0.0)
        desc_var = tk.StringVar()

        ttk.Label(dialog, text="Category:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(dialog, textvariable=category_var).grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(dialog, text="Amount:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(dialog, textvariable=amount_var).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(dialog, text="Description:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(dialog, textvariable=desc_var).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        def save():
            conn = get_conn()
            cur = conn.cursor()
            try:
                cur.execute("""
                    INSERT INTO expenses (date, category, amount, description, user_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    category_var.get(),
                    amount_var.get(),
                    desc_var.get(),
                    self.user_id
                ))
                conn.commit()
                self._refresh_expenses()
                dialog.destroy()
            except Exception as ex:
                messagebox.showerror("Error", f"Failed to add expense: {ex}")
                conn.rollback()
            finally:
                conn.close()

        ttk.Button(dialog, text="Save", command=save).grid(row=3, column=0, columnspan=2, pady=10)

    def _edit_expense(self):
        selection = self.expenses_tree.selection()
        if not selection:
            messagebox.showwarning("Select Expense", "Please select an expense to edit.")
            return
        item = self.expenses_tree.item(selection[0])
        values = item['values']

        dialog = tk.Toplevel(self)
        dialog.title("Edit Expense")
        dialog.geometry("400x350")
        dialog.transient(self)
        dialog.grab_set()

        category_var = tk.StringVar(value=values[2])
        amount_var = tk.DoubleVar(value=values[3])
        desc_var = tk.StringVar(value=values[4])

        ttk.Label(dialog, text="Category:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(dialog, textvariable=category_var).grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(dialog, text="Amount:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(dialog, textvariable=amount_var).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(dialog, text="Description:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(dialog, textvariable=desc_var).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        def save():
            conn = get_conn()
            cur = conn.cursor()
            try:
                cur.execute("""
                    UPDATE expenses SET category=?, amount=?, description=?
                    WHERE id=?
                """, (
                    category_var.get(),
                    amount_var.get(),
                    desc_var.get(),
                    values[0]
                ))
                conn.commit()
                self._refresh_expenses()
                dialog.destroy()
            except Exception as ex:
                messagebox.showerror("Error", f"Failed to edit expense: {ex}")
                conn.rollback()
            finally:
                conn.close()

        ttk.Button(dialog, text="Save", command=save).grid(row=3, column=0, columnspan=2, pady=10)

    def _delete_expense(self):
        selection = self.expenses_tree.selection()
        if not selection:
            messagebox.showwarning("Select Expense", "Please select an expense to delete.")
            return
        item = self.expenses_tree.item(selection[0])
        expense_id = item['values'][0]
        if messagebox.askyesno("Delete Expense", "Are you sure you want to delete this expense?"):
            conn = get_conn()
            cur = conn.cursor()
            try:
                cur.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
                conn.commit()
                self._refresh_expenses()
            except Exception as ex:
                messagebox.showerror("Error", f"Failed to delete expense: {ex}")
                conn.rollback()
            finally:
                conn.close()

    def _export_expenses_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT e.id, e.date, e.category, e.amount, e.description, u.username
            FROM expenses e
            LEFT JOIN users u ON e.user_id = u.id
            ORDER BY e.date DESC
        """)
        rows = cur.fetchall()
        conn.close()
        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Date", "Category", "Amount", "Description", "User"])
                writer.writerows(rows)
            messagebox.showinfo("Export Successful", f"Expenses exported to {file_path}")
        except Exception as ex:
            messagebox.showerror("Export Failed", f"Failed to export expenses: {ex}")
    def _build_reports(self):
        frm = self.reports_tab
        for w in frm.winfo_children():
            w.destroy()

        # Top controls
        top = ttk.Frame(frm, padding=6)
        top.pack(fill="x")
        ttk.Button(top, text="Export Sales Report", command=self._export_sales_report).pack(side="left", padx=4)
        ttk.Button(top, text="Export Inventory Report", command=self._export_inventory_report).pack(side="left", padx=4)
        ttk.Button(top, text="Export Expenses Report", command=self._export_expenses_report).pack(side="left", padx=4)

        # Summary statistics
        stats_frame = ttk.LabelFrame(frm, text="Summary Statistics", padding=10)
        stats_frame.pack(fill="x", padx=10, pady=10)

        # Fetch statistics
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM sales")
        total_sales = cur.fetchone()[0]
        cur.execute("SELECT SUM(total_amount) FROM sales")
        total_revenue = cur.fetchone()[0] or 0
        cur.execute("SELECT SUM(amount) FROM expenses")
        total_expenses = cur.fetchone()[0] or 0
        cur.execute("SELECT COUNT(*) FROM products WHERE quantity <= min_quantity")
        low_stock = cur.fetchone()[0]
        conn.close()

        ttk.Label(stats_frame, text=f"Total Sales: {total_sales}").pack(anchor="w")
        ttk.Label(stats_frame, text=f"Total Revenue: {money(total_revenue)}").pack(anchor="w")
        ttk.Label(stats_frame, text=f"Total Expenses: {money(total_expenses)}").pack(anchor="w")
        ttk.Label(stats_frame, text=f"Low Stock Products: {low_stock}").pack(anchor="w")

        # Optionally, add charts or graphs here using matplotlib or similar

    def _export_sales_report(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT s.id, s.date, c.name, s.total_amount, s.tax_amount, s.paid_amount, s.payment_method, u.username
            FROM sales s
            LEFT JOIN customers c ON s.customer_id = c.id
            LEFT JOIN users u ON s.user_id = u.id
            ORDER BY s.date DESC
        """)
        rows = cur.fetchall()
        conn.close()
        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Date", "Customer", "Total Amount", "Tax", "Paid", "Payment Method", "User"])
                writer.writerows(rows)
            messagebox.showinfo("Export Successful", f"Sales report exported to {file_path}")
        except Exception as ex:
            messagebox.showerror("Export Failed", f"Failed to export sales report: {ex}")

    def _export_inventory_report(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT p.id, p.sku, p.name, p.category, p.quantity, p.min_quantity, p.sell_price, s.name
            FROM products p
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            ORDER BY p.name
        """)
        rows = cur.fetchall()
        conn.close()
        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "SKU", "Name", "Category", "Quantity", "Min Quantity", "Sell Price", "Supplier"])
                writer.writerows(rows)
            messagebox.showinfo("Export Successful", f"Inventory report exported to {file_path}")
        except Exception as ex:
            messagebox.showerror("Export Failed", f"Failed to export inventory report: {ex}")

    def _export_expenses_report(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT e.id, e.date, e.category, e.amount, e.description, u.username
            FROM expenses e
            LEFT JOIN users u ON e.user_id = u.id
            ORDER BY e.date DESC
        """)
        rows = cur.fetchall()
        conn.close()
        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Date", "Category", "Amount", "Description", "User"])
                writer.writerows(rows)
            messagebox.showinfo("Export Successful", f"Expenses report exported to {file_path}")
        except Exception as ex:
            messagebox.showerror("Export Failed", f"Failed to export expenses report: {ex}")

# ... existing code continues ...
# ... existing code continues ...
# ... existing code continues ...