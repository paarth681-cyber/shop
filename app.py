"""
Shop Manager — single-file application (app.py)

Features:
- Products, Customers, Suppliers, Sales (POS), Expenses, Reports
- Theme selector (Blue, Red, Yellow, White)
- Database file: shop.db (created automatically)
- Seeded users: admin/admin, cashier/cashier
- Self-test to run through many operations
"""

import os
import sqlite3
import csv
from datetime import datetime, date
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

DB_FILE = "shop.db"

# ---------------------------
# Utilities
# ---------------------------
def money(v):
    # Ensure digit-by-digit safe arithmetic formatting
    try:
        v_float = float(v or 0.0)
    except Exception:
        v_float = 0.0
    return f"${v_float:,.2f}"

def get_conn():
    return sqlite3.connect(DB_FILE)

def init_db():
    first = not os.path.exists(DB_FILE)
    conn = get_conn()
    cur = conn.cursor()
    # users
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )""")
    # products
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT UNIQUE,
        name TEXT,
        description TEXT,
        quantity INTEGER DEFAULT 0,
        cost_price REAL DEFAULT 0,
        sell_price REAL DEFAULT 0,
        supplier_id INTEGER
    )""")
    # customers
    cur.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        email TEXT,
        address TEXT
    )""")
    # suppliers
    cur.execute("""
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        email TEXT,
        address TEXT
    )""")
    # sales (header)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        customer_id INTEGER,
        total_amount REAL,
        paid INTEGER DEFAULT 1,
        user_id INTEGER,
        note TEXT
    )""")
    # sale_lines (items)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sale_lines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER,
        product_id INTEGER,
        qty INTEGER,
        price REAL,
        line_total REAL
    )""")
    # expenses
    cur.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        title TEXT,
        amount REAL,
        note TEXT
    )""")
    conn.commit()

    # seed default users/products if first run
    if first:
        try:
            cur.execute("INSERT OR IGNORE INTO users (username,password,role) VALUES (?,?,?)", ("admin","admin","admin"))
            cur.execute("INSERT OR IGNORE INTO users (username,password,role) VALUES (?,?,?)", ("cashier","cashier","cashier"))
            # seed some suppliers
            cur.execute("INSERT INTO suppliers (name,phone,email,address) VALUES (?,?,?,?)",
                        ("General Supplies Co.", "555-0100", "sales@gensup.com", "100 Supply St."))
            # sample products
            cur.execute("INSERT INTO products (sku,name,description,quantity,cost_price,sell_price,supplier_id) VALUES (?,?,?,?,?,?,?)",
                        ("SKU-001","Stapler","Heavy duty stapler",50,3.50,7.50,1))
            cur.execute("INSERT INTO products (sku,name,description,quantity,cost_price,sell_price,supplier_id) VALUES (?,?,?,?,?,?,?)",
                        ("SKU-002","A4 Paper Pack","500 sheets A4",200,5.00,12.00,1))
            cur.execute("INSERT INTO products (sku,name,description,quantity,cost_price,sell_price,supplier_id) VALUES (?,?,?,?,?,?,?)",
                        ("SKU-003","Pen (Box of 10)","Blue ink pens",150,2.00,6.00,1))
            # sample customers
            cur.execute("INSERT INTO customers (name,phone,email,address) VALUES (?,?,?,?)",
                        ("Walk-in Customer","", "",""))
            conn.commit()
        except Exception:
            conn.rollback()
    conn.close()

# ---------------------------
# Application UI
# ---------------------------
class ShopApp(tk.Tk):
    THEMES = {
        "Blue": {"bg": "#EAF2FF", "accent": "#2B6CB0", "fg": "#1F2937"},
        "Red": {"bg": "#FFF5F5", "accent": "#C53030", "fg": "#1F2937"},
        "Yellow": {"bg": "#FFFBEB", "accent": "#D69E2E", "fg": "#1F2937"},
        "White": {"bg": "#FFFFFF", "accent": "#0F172A", "fg": "#0F172A"}
    }

    def __init__(self):
        super().__init__()
        self.title("Shop Manager")
        self.geometry("1100x700")
        self.minsize(900,600)
        self.username = None
        self.user_role = None
        self.style = ttk.Style(self)
        self.current_theme = "Blue"
        self._setup_login()

    # ---------------------------
    # Login
    # ---------------------------
    def _setup_login(self):
        for w in self.winfo_children(): w.destroy()
        frm = ttk.Frame(self, padding=20)
        frm.pack(expand=True)
        ttk.Label(frm, text="Shop Manager", font=("Segoe UI", 20, "bold")).grid(row=0,column=0,columnspan=2,pady=(0,15))
        ttk.Label(frm, text="Username:").grid(row=1,column=0,sticky="e", padx=5, pady=5)
        uentry = ttk.Entry(frm); uentry.grid(row=1,column=1,sticky="w", padx=5, pady=5)
        ttk.Label(frm, text="Password:").grid(row=2,column=0,sticky="e", padx=5, pady=5)
        pentry = ttk.Entry(frm, show="*"); pentry.grid(row=2,column=1,sticky="w", padx=5, pady=5)

        def attempt():
            user = uentry.get().strip()
            pw = pentry.get().strip()
            conn = get_conn(); cur = conn.cursor()
            cur.execute("SELECT role FROM users WHERE username=? AND password=?", (user,pw))
            r = cur.fetchone()
            conn.close()
            if r:
                self.username = user
                self.user_role = r[0]
                self._setup_main()
            else:
                messagebox.showerror("Login failed", "Invalid credentials. Try 'admin'/'admin'.")

        login_btn = ttk.Button(frm, text="Login", command=attempt)
        login_btn.grid(row=3,column=0,columnspan=2,pady=10)

    # ---------------------------
    # Main window
    # ---------------------------
    def _setup_main(self):
        for w in self.winfo_children(): w.destroy()
        # Menu top
        topbar = ttk.Frame(self, padding=(8,8))
        topbar.pack(fill="x")
        title_lbl = ttk.Label(topbar, text=f"Shop Manager — User: {self.username}", font=("Segoe UI", 14, "bold"))
        title_lbl.pack(side="left", padx=(8,12))

        logout = ttk.Button(topbar, text="Logout", command=self._setup_login)
        logout.pack(side="right", padx=6)
        self.test_btn = ttk.Button(topbar, text="Run Self-Test", command=self.run_self_test)
        self.test_btn.pack(side="right", padx=6)
        # Theme selector
        ttk.Label(topbar, text="Theme:").pack(side="right", padx=(6,2))
        theme_cb = ttk.Combobox(topbar, values=list(self.THEMES.keys()), state="readonly", width=10)
        theme_cb.set(self.current_theme)
        theme_cb.pack(side="right", padx=(0,12))
        theme_cb.bind("<<ComboboxSelected>>", lambda e: self.apply_theme(theme_cb.get()))

        # Notebook
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        # Tabs
        self.dashboard_tab = ttk.Frame(nb)
        self.products_tab = ttk.Frame(nb)
        self.sales_tab = ttk.Frame(nb)
        self.customers_tab = ttk.Frame(nb)
        self.suppliers_tab = ttk.Frame(nb)
        self.expenses_tab = ttk.Frame(nb)
        self.reports_tab = ttk.Frame(nb)
        self.settings_tab = ttk.Frame(nb)

        nb.add(self.dashboard_tab, text="Dashboard")
        nb.add(self.products_tab, text="Products")
        nb.add(self.sales_tab, text="Sales (POS)")
        nb.add(self.customers_tab, text="Customers")
        nb.add(self.suppliers_tab, text="Suppliers")
        nb.add(self.expenses_tab, text="Expenses")
        nb.add(self.reports_tab, text="Reports")
        nb.add(self.settings_tab, text="Settings")

        # Populate each
        self._build_dashboard()
        self._build_products()
        self._build_sales()
        self._build_customers()
        self._build_suppliers()
        self._build_expenses()
        self._build_reports()
        self._build_settings()

        self.apply_theme(self.current_theme)
        self.refresh_all()

    # ---------------------------
    # Theme
    # ---------------------------
    def apply_theme(self, theme_name):
        if theme_name not in self.THEMES: return
        t = self.THEMES[theme_name]
        bg = t["bg"]; accent = t["accent"]; fg = t["fg"]
        # Basic widget colors via style
        self.style.configure("TFrame", background=bg)
        self.style.configure("TLabel", background=bg, foreground=fg)
        self.style.configure("TButton", background=accent, foreground="white")
        self.style.configure("TEntry", fieldbackground="#ffffff")
        # Treeview styling
        self.style.configure("Treeview", background="white", fieldbackground="white", foreground=fg)
        self.configure(background=bg)
        self.current_theme = theme_name

    # ---------------------------
    # Dashboard
    # ---------------------------
    def _build_dashboard(self):
        frm = self.dashboard_tab
        for w in frm.winfo_children(): w.destroy()
        left = ttk.Frame(frm, padding=12)
        right = ttk.Frame(frm, padding=12)
        left.pack(side="left", fill="both", expand=True)
        right.pack(side="right", fill="y")

        self.d_info = tk.StringVar()
        lbl = ttk.Label(left, textvariable=self.d_info, font=("Segoe UI", 12), justify="left")
        lbl.pack(anchor="nw", fill="both", expand=True)

        # Quick actions
        quick = ttk.Label(right, text="Quick Actions", font=("Segoe UI", 12, "bold"))
        quick.pack(anchor="n")
        ttk.Button(right, text="Add Product", command=self.dialog_add_product).pack(fill="x", pady=4)
        ttk.Button(right, text="Open POS", command=lambda: self.select_tab_by_text("Sales (POS)")).pack(fill="x", pady=4)
        ttk.Button(right, text="Export Inventory CSV", command=self.export_inventory_csv).pack(fill="x", pady=4)
        ttk.Button(right, text="Refresh", command=self.refresh_all).pack(fill="x", pady=4)

    def refresh_dashboard(self):
        conn = get_conn(); cur = conn.cursor()
        today = date.today().isoformat()
        cur.execute("SELECT IFNULL(SUM(total_amount),0) FROM sales WHERE date(date)=?", (today,))
        revenue = cur.fetchone()[0] or 0.0
        cur.execute("SELECT IFNULL(SUM(amount),0) FROM expenses WHERE date(date)=?", (today,))
        expenses = cur.fetchone()[0] or 0.0
        cur.execute("SELECT IFNULL(SUM(quantity*cost_price),0) FROM products")
        inv_val = cur.fetchone()[0] or 0.0
        cur.execute("SELECT COUNT(*) FROM products")
        prod_count = cur.fetchone()[0] or 0
        conn.close()
        txt = (f"Date: {today}\n\n"
               f"Today's Revenue: {money(revenue)}\n"
               f"Today's Expenses: {money(expenses)}\n"
               f"Inventory Cost Value: {money(inv_val)}\n"
               f"Total Products: {prod_count}\n")
        self.d_info.set(txt)

    # ---------------------------
    # Products tab
    # ---------------------------
    def _build_products(self):
        frm = self.products_tab
        for w in frm.winfo_children(): w.destroy()
        top = ttk.Frame(frm, padding=6)
        top.pack(fill="x")
        ttk.Button(top, text="Add Product", command=self.dialog_add_product).pack(side="left", padx=4)
        ttk.Button(top, text="Edit Product", command=self.dialog_edit_selected_product).pack(side="left", padx=4)
        ttk.Button(top, text="Delete Product", command=self.delete_selected_product).pack(side="left", padx=4)
        ttk.Button(top, text="Export CSV", command=self.export_inventory_csv).pack(side="left", padx=4)
        # Search
        ttk.Label(top, text="Search:").pack(side="left", padx=(12,4))
        self.prod_search_var = tk.StringVar()
        ent = ttk.Entry(top, textvariable=self.prod_search_var)
        ent.pack(side="left", padx=4)
        ent.bind("<Return>", lambda e: self.refresh_products())
        # Tree
        tree = ttk.Treeview(frm, columns=("id","sku","name","qty","cost","price"), show="headings")
        tree.heading("id", text="ID")
        tree.heading("sku", text="SKU")
        tree.heading("name", text="Name")
        tree.heading("qty", text="Qty")
        tree.heading("cost", text="Cost")
        tree.heading("price", text="Sell")
        tree.column("id", width=50, anchor="center")
        tree.column("sku", width=110)
        tree.column("name", width=300)
        tree.column("qty", width=70, anchor="center")
        tree.column("cost", width=90, anchor="e")
        tree.column("price", width=90, anchor="e")
        tree.pack(fill="both", expand=True, padx=8, pady=8)
        self.products_tree = tree

    def refresh_products(self):
        q = self.prod_search_var.get().strip()
        conn = get_conn(); cur = conn.cursor()
        if q:
            cur.execute("SELECT id,sku,name,quantity,cost_price,sell_price FROM products WHERE sku LIKE ? OR name LIKE ? OR description LIKE ?",
                        (f"%{q}%", f"%{q}%", f"%{q}%"))
        else:
            cur.execute("SELECT id,sku,name,quantity,cost_price,sell_price FROM products")
        rows = cur.fetchall(); conn.close()
        tree = self.products_tree
        for i in tree.get_children(): tree.delete(i)
        for r in rows:
            tree.insert("", "end", values=(r[0], r[1], r[2], r[3], money(r[4]), money(r[5])))

    def dialog_add_product(self):
        dlg = tk.Toplevel(self)
        dlg.title("Add Product")
        frm = ttk.Frame(dlg, padding=12); frm.pack(fill="both", expand=True)
        labels = ["SKU","Name","Description","Quantity","Cost Price","Sell Price","Supplier ID"]
        vars = [tk.StringVar() for _ in labels]
        for i,L in enumerate(labels):
            ttk.Label(frm, text=L+":").grid(row=i, column=0, sticky="e", padx=4, pady=4)
            ttk.Entry(frm, textvariable=vars[i], width=40).grid(row=i, column=1, padx=4, pady=4)
        def add():
            sku = vars[0].get().strip()
            name = vars[1].get().strip()
            desc = vars[2].get().strip()
            qty = int(vars[3].get() or 0)
            cost = float(vars[4].get() or 0.0)
            sell = float(vars[5].get() or 0.0)
            sup = int(vars[6].get() or 0) if vars[6].get().strip() else None
            conn = get_conn(); cur = conn.cursor()
            try:
                cur.execute("INSERT INTO products (sku,name,description,quantity,cost_price,sell_price,supplier_id) VALUES (?,?,?,?,?,?,?)",
                            (sku,name,desc,qty,cost,sell,sup))
                conn.commit(); conn.close()
                dlg.destroy()
                self.refresh_products(); self.refresh_dashboard()
            except Exception as ex:
                conn.rollback(); conn.close()
                messagebox.showerror("Error", f"Failed to add product: {ex}")
        ttk.Button(frm, text="Add", command=add).grid(row=len(labels), column=0, columnspan=2, pady=8)

    def dialog_edit_selected_product(self):
        sel = self.products_tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a product first.")
            return
        item = self.products_tree.item(sel[0])["values"]
        pid = item[0]
        conn = get_conn(); cur = conn.cursor()
        cur.execute("SELECT sku,name,description,quantity,cost_price,sell_price,supplier_id FROM products WHERE id=?", (pid,))
        row = cur.fetchone(); conn.close()
        if not row:
            messagebox.showerror("Missing", "Product not found.")
            return
        dlg = tk.Toplevel(self); dlg.title("Edit Product")
        frm = ttk.Frame(dlg, padding=12); frm.pack(fill="both", expand=True)
        labels = ["SKU","Name","Description","Quantity","Cost Price","Sell Price","Supplier ID"]
        vars = [tk.StringVar(value=str(row[i])) for i in range(7)]
        for i,L in enumerate(labels):
            ttk.Label(frm, text=L+":").grid(row=i, column=0, sticky="e", padx=4, pady=4)
            ttk.Entry(frm, textvariable=vars[i], width=40).grid(row=i, column=1, padx=4, pady=4)
        def save():
            sku = vars[0].get().strip()
            name = vars[1].get().strip()
            desc = vars[2].get().strip()
            qty = int(vars[3].get() or 0)
            cost = float(vars[4].get() or 0.0)
            sell = float(vars[5].get() or 0.0)
            sup = int(vars[6].get() or 0) if vars[6].get().strip() else None
            conn = get_conn(); cur = conn.cursor()
            try:
                cur.execute("""UPDATE products SET sku=?,name=?,description=?,quantity=?,cost_price=?,sell_price=?,supplier_id=? WHERE id=?""",
                            (sku,name,desc,qty,cost,sell,sup,pid))
                conn.commit(); conn.close()
                dlg.destroy()
                self.refresh_products(); self.refresh_dashboard()
            except Exception as ex:
                conn.rollback(); conn.close()
                messagebox.showerror("Error", f"Failed to save: {ex}")
        ttk.Button(frm, text="Save", command=save).grid(row=len(labels), column=0, columnspan=2, pady=8)

    def delete_selected_product(self):
        sel = self.products_tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a product first.")
            return
        item = self.products_tree.item(sel[0])["values"]
        pid = item[0]
        if not messagebox.askyesno("Delete", f"Delete product ID {pid}?"): return
        conn = get_conn(); cur = conn.cursor()
        try:
            cur.execute("DELETE FROM products WHERE id=?", (pid,))
            conn.commit(); conn.close()
            self.refresh_products(); self.refresh_dashboard()
        except Exception as ex:
            conn.rollback(); conn.close()
            messagebox.showerror("Error", f"Delete failed: {ex}")

    # ---------------------------
    # Sales (POS)
    # ---------------------------
    def _build_sales(self):
        frm = self.sales_tab
        for w in frm.winfo_children(): w.destroy()
        left = ttk.Frame(frm, padding=8)
        right = ttk.Frame(frm, padding=8)
        left.pack(side="left", fill="both", expand=True)
        right.pack(side="right", fill="y")

        # Product search & list
        searchfrm = ttk.Frame(left)
        searchfrm.pack(fill="x")
        ttk.Label(searchfrm, text="Lookup Product:").pack(side="left")
        self.pos_search_var = tk.StringVar()
        ent = ttk.Entry(searchfrm, textvariable=self.pos_search_var)
        ent.pack(side="left", padx=6, fill="x", expand=True)
        ent.bind("<Return>", lambda e: self.refresh_pos_products())
        ttk.Button(searchfrm, text="Search", command=self.refresh_pos_products).pack(side="left", padx=6)

        self.pos_products_tree = ttk.Treeview(left, columns=("id","sku","name","qty","price"), show="headings", height=12)
        for col,txt,wid in [("id","ID",50),("sku","SKU",120),("name","Name",320),("qty","Qty",70),("price","Price",90)]:
            self.pos_products_tree.heading(col, text=txt)
            self.pos_products_tree.column(col, width=wid, anchor="center" if col in ("id","qty") else "w")
        self.pos_products_tree.pack(fill="both", expand=True, pady=(6,0))
        # Cart
        cartlbl = ttk.Label(right, text="Cart", font=("Segoe UI", 12, "bold"))
        cartlbl.pack(anchor="n")
        self.cart_tree = ttk.Treeview(right, columns=("prod_id","name","qty","price","total"), show="headings", height=12)
        for col,txt,wid in [("prod_id","ID",50),("name","Name",180),("qty","Qty",60),("price","Price",80),("total","Total",90)]:
            self.cart_tree.heading(col, text=txt)
            self.cart_tree.column(col, width=wid, anchor="center" if col in ("prod_id","qty") else "w")
        self.cart_tree.pack()
        # POS controls
        controls = ttk.Frame(right, padding=(6,6))
        controls.pack(fill="x", pady=(6,0))
        ttk.Button(controls, text="Add Selected → Cart", command=self.pos_add_selected_to_cart).pack(fill="x", pady=4)
        ttk.Button(controls, text="Remove Selected Item", command=self.pos_remove_selected_item).pack(fill="x", pady=4)
        ttk.Button(controls, text="Complete Sale", command=self.pos_complete_sale).pack(fill="x", pady=4)

        self.pos_subtotal_var = tk.StringVar(value="Subtotal: $0.00")
        ttk.Label(right, textvariable=self.pos_subtotal_var, font=("Segoe UI", 11, "bold")).pack(pady=(8,0))

    def refresh_pos_products(self):
        q = self.pos_search_var.get().strip()
        conn = get_conn(); cur = conn.cursor()
        if q:
            cur.execute("SELECT id,sku,name,quantity,sell_price FROM products WHERE sku LIKE ? OR name LIKE ?", (f"%{q}%", f"%{q}%"))
        else:
            cur.execute("SELECT id,sku,name,quantity,sell_price FROM products")
        rows = cur.fetchall(); conn.close()
        tree = self.pos_products_tree
        for i in tree.get_children(): tree.delete(i)
        for r in rows:
            tree.insert("", "end", values=(r[0], r[1], r[2], r[3], money(r[4])))

    def pos_add_selected_to_cart(self):
        sel = self.pos_products_tree.selection()
        if not sel: messagebox.showinfo("Select", "Select a product first."); return
        item = self.pos_products_tree.item(sel[0])["values"]
        pid = item[0]
        # ask qty
        qty = simpledialog.askinteger("Quantity", "Enter quantity", parent=self, minvalue=1, initialvalue=1)
        if not qty: return
        # fetch price and name and check inventory
        conn = get_conn(); cur = conn.cursor()
        cur.execute("SELECT name,quantity,sell_price FROM products WHERE id=?", (pid,))
        row = cur.fetchone(); conn.close()
        if not row:
            messagebox.showerror("Error", "Product missing")
            return
        name,stock,price = row
        if qty > stock:
            if not messagebox.askyesno("Stock", f"Only {stock} in stock. Add {qty} anyway?"): return
        # add to cart tree; if already exists increment
        found = None
        for iid in self.cart_tree.get_children():
            vals = self.cart_tree.item(iid)["values"]
            if vals[0] == pid:
                found = iid; break
        if found:
            vals = self.cart_tree.item(found)["values"]
            newqty = int(vals[2]) + qty
            newtotal = float((newqty) * float(price))
            self.cart_tree.item(found, values=(pid, name, newqty, money(price), money(newtotal)))
        else:
            self.cart_tree.insert("", "end", values=(pid, name, qty, money(price), money(qty * float(price))))
        self.update_pos_subtotal()

    def pos_remove_selected_item(self):
        sel = self.cart_tree.selection()
        if not sel: messagebox.showinfo("Select", "Select cart item."); return
        for s in sel: self.cart_tree.delete(s)
        self.update_pos_subtotal()

    def update_pos_subtotal(self):
        subtotal = 0.0
        for iid in self.cart_tree.get_children():
            vals = self.cart_tree.item(iid)["values"]
            # vals[4] is "$x.xx" — parse safely
            total_str = str(vals[4]).replace("$","").replace(",","")
            try:
                subtotal += float(total_str)
            except Exception:
                subtotal += 0.0
        self.pos_subtotal_var.set(f"Subtotal: {money(subtotal)}")

    def pos_complete_sale(self):
        if not self.cart_tree.get_children():
            messagebox.showinfo("Empty", "Cart is empty.")
            return
        # Choose customer
        conn = get_conn(); cur = conn.cursor()
        cur.execute("SELECT id,name FROM customers")
        custs = cur.fetchall(); conn.close()
        cust_choices = {str(c[0]): c[1] for c in custs}
        cust_choices_display = "\n".join([f"{c[0]}: {c[1]}" for c in custs])
        cust_id = simpledialog.askinteger("Customer ID", f"Enter customer ID (or blank for Walk-in):\n{cust_choices_display}", parent=self)
        if cust_id is None:
            # treat as walk-in: pick first customer (seed)
            if custs:
                cust_id = custs[0][0]
            else:
                cust_id = None
        # Confirm and pay
        subtotal = 0.0
        items = []
        for iid in self.cart_tree.get_children():
            vals = self.cart_tree.item(iid)["values"]
            pid = vals[0]; qty = int(vals[2])
            price = float(str(vals[3]).replace("$","").replace(",",""))
            line_total = qty * price
            subtotal += line_total
            items.append((pid, qty, price, line_total))
        if not messagebox.askyesno("Complete", f"Complete sale for {money(subtotal)}?"): return
        # Insert sale
        conn = get_conn(); cur = conn.cursor()
        try:
            now = datetime.now().isoformat()
            cur.execute("INSERT INTO sales (date,customer_id,total_amount,paid,user_id) VALUES (?,?,?,?,?)", (now, cust_id, subtotal, 1, None))
            sale_id = cur.lastrowid
            for pid,qty,price,line_total in items:
                cur.execute("INSERT INTO sale_lines (sale_id,product_id,qty,price,line_total) VALUES (?,?,?,?,?)",
                            (sale_id, pid, qty, price, line_total))
                # decrement inventory
                cur.execute("UPDATE products SET quantity = quantity - ? WHERE id=?", (qty, pid))
            conn.commit(); conn.close()
            messagebox.showinfo("Done", f"Sale {sale_id} completed: {money(subtotal)}")
            # clear cart
            for iid in self.cart_tree.get_children(): self.cart_tree.delete(iid)
            self.update_pos_subtotal()
            self.refresh_products(); self.refresh_pos_products(); self.refresh_dashboard()
        except Exception as ex:
            conn.rollback(); conn.close()
            messagebox.showerror("Error", f"Sale failed: {ex}")

    # ---------------------------
    # Customers
    # ---------------------------
    def _build_customers(self):
        frm = self.customers_tab
        for w in frm.winfo_children(): w.destroy()
        top = ttk.Frame(frm, padding=6)
        top.pack(fill="x")
        ttk.Button(top, text="Add Customer", command=self.dialog_add_customer).pack(side="left", padx=4)
        ttk.Button(top, text="Edit Customer", command=self.dialog_edit_selected_customer).pack(side="left", padx=4)
        ttk.Button(top, text="Delete Customer", command=self.delete_selected_customer).pack(side="left", padx=4)
        ttk.Label(top, text="Search:").pack(side="left", padx=(12,4))
        self.cust_search_var = tk.StringVar()
        ent = ttk.Entry(top, textvariable=self.cust_search_var)
        ent.pack(side="left", padx=4)
        ent.bind("<Return>", lambda e: self.refresh_customers())
        tree = ttk.Treeview(frm, columns=("id","name","phone","email"), show="headings")
        for col,txt,wid in [("id","ID",50),("name","Name",250),("phone","Phone",120),("email","Email",200)]:
            tree.heading(col, text=txt); tree.column(col, width=wid)
        tree.pack(fill="both", expand=True, padx=8, pady=8)
        self.customers_tree = tree

    def refresh_customers(self):
        q = self.cust_search_var.get().strip()
        conn = get_conn(); cur = conn.cursor()
        if q:
            cur.execute("SELECT id,name,phone,email FROM customers WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?", (f"%{q}%", f"%{q}%", f"%{q}%"))
        else:
            cur.execute("SELECT id,name,phone,email FROM customers")
        rows = cur.fetchall(); conn.close()
        tree = self.customers_tree
        for i in tree.get_children(): tree.delete(i)
        for r in rows:
            tree.insert("", "end", values=r)

    def dialog_add_customer(self):
        dlg = tk.Toplevel(self); dlg.title("Add Customer")
        frm = ttk.Frame(dlg, padding=12); frm.pack(fill="both", expand=True)
        labels = ["Name","Phone","Email","Address"]
        vars = [tk.StringVar() for _ in labels]
        for i,L in enumerate(labels):
            ttk.Label(frm, text=L+":").grid(row=i, column=0, sticky="e", padx=4, pady=4)
            ttk.Entry(frm, textvariable=vars[i], width=50).grid(row=i, column=1, padx=4, pady=4)
        def add():
            name,phone,email,address = [v.get().strip() for v in vars]
            conn = get_conn(); cur = conn.cursor()
            try:
                cur.execute("INSERT INTO customers (name,phone,email,address) VALUES (?,?,?,?)", (name,phone,email,address))
                conn.commit(); conn.close(); dlg.destroy(); self.refresh_customers()
            except Exception as ex:
                conn.rollback(); conn.close(); messagebox.showerror("Error", f"Failed: {ex}")
        ttk.Button(frm, text="Add", command=add).grid(row=len(labels), column=0, columnspan=2, pady=8)

    def dialog_edit_selected_customer(self):
        sel = self.customers_tree.selection()
        if not sel: messagebox.showinfo("Select","Select customer."); return
        item = self.customers_tree.item(sel[0])["values"]
        cid = item[0]
        conn = get_conn(); cur = conn.cursor()
        cur.execute("SELECT name,phone,email,address FROM customers WHERE id=?", (cid,))
        row = cur.fetchone(); conn.close()
        if not row: messagebox.showerror("Missing","Customer not found"); return
        dlg = tk.Toplevel(self); dlg.title("Edit Customer")
        frm = ttk.Frame(dlg, padding=12); frm.pack(fill="both", expand=True)
        labels = ["Name","Phone","Email","Address"]
        vars = [tk.StringVar(value=row[i]) for i in range(4)]
        for i,L in enumerate(labels):
            ttk.Label(frm, text=L+":").grid(row=i, column=0, sticky="e", padx=4, pady=4)
            ttk.Entry(frm, textvariable=vars[i], width=50).grid(row=i, column=1, padx=4, pady=4)
        def save():
            name,phone,email,address = [v.get().strip() for v in vars]
            conn = get_conn(); cur = conn.cursor()
            try:
                cur.execute("UPDATE customers SET name=?,phone=?,email=?,address=? WHERE id=?", (name,phone,email,address,cid))
                conn.commit(); conn.close(); dlg.destroy(); self.refresh_customers()
            except Exception as ex:
                conn.rollback(); conn.close(); messagebox.showerror("Error", f"Failed: {ex}")
        ttk.Button(frm, text="Save", command=save).grid(row=len(labels), column=0, columnspan=2, pady=8)

    def delete_selected_customer(self):
        sel = self.customers_tree.selection()
        if not sel: messagebox.showinfo("Select","Select customer."); return
        item = self.customers_tree.item(sel[0])["values"]; cid = item[0]
        if not messagebox.askyesno("Delete", f"Delete customer {cid}?"): return
        conn = get_conn(); cur = conn.cursor()
        try:
            cur.execute("DELETE FROM customers WHERE id=?", (cid,)); conn.commit(); conn.close(); self.refresh_customers()
        except Exception as ex:
            conn.rollback(); conn.close(); messagebox.showerror("Error", f"Failed: {ex}")

    # ---------------------------
    # Suppliers
    # ---------------------------
    def _build_suppliers(self):
        frm = self.suppliers_tab
        for w in frm.winfo_children(): w.destroy()
        top = ttk.Frame(frm, padding=6)
        top.pack(fill="x")
        ttk.Button(top, text="Add Supplier", command=self.dialog_add_supplier).pack(side="left", padx=4)
        ttk.Button(top, text="Edit Supplier", command=self.dialog_edit_selected_supplier).pack(side="left", padx=4)
        ttk.Button(top, text="Delete Supplier", command=self.delete_selected_supplier).pack(side="left", padx=4)
        ttk.Label(top, text="Search:").pack(side="left", padx=(12,4))
        self.sup_search_var = tk.StringVar()
        ent = ttk.Entry(top, textvariable=self.sup_search_var)
        ent.pack(side="left", padx=4)
        ent.bind("<Return>", lambda e: self.refresh_suppliers())
        tree = ttk.Treeview(frm, columns=("id","name","phone","email"), show="headings")
        for col,txt,wid in [("id","ID",50),("name","Name",300),("phone","Phone",140),("email","Email",220)]:
            tree.heading(col, text=txt); tree.column(col, width=wid)
        tree.pack(fill="both", expand=True, padx=8, pady=8)
        self.suppliers_tree = tree

    def refresh_suppliers(self):
        q = self.sup_search_var.get().strip()
        conn = get_conn(); cur = conn.cursor()
        if q:
            cur.execute("SELECT id,name,phone,email FROM suppliers WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?", (f"%{q}%", f"%{q}%", f"%{q}%"))
        else:
            cur.execute("SELECT id,name,phone,email FROM suppliers")
        rows = cur.fetchall(); conn.close()
        tree = self.suppliers_tree
        for i in tree.get_children(): tree.delete(i)
        for r in rows:
            tree.insert("", "end", values=r)

    def dialog_add_supplier(self):
        dlg = tk.Toplevel(self); dlg.title("Add Supplier")
        frm = ttk.Frame(dlg, padding=12); frm.pack(fill="both", expand=True)
        labels = ["Name","Phone","Email","Address"]
        vars = [tk.StringVar() for _ in labels]
        for i,L in enumerate(labels):
            ttk.Label(frm, text=L+":").grid(row=i, column=0, sticky="e", padx=4, pady=4)
            ttk.Entry(frm, textvariable=vars[i], width=50).grid(row=i, column=1, padx=4, pady=4)
        def add():
            name,phone,email,address = [v.get().strip() for v in vars]
            conn = get_conn(); cur = conn.cursor()
            try:
                cur.execute("INSERT INTO suppliers (name,phone,email,address) VALUES (?,?,?,?)", (name,phone,email,address))
                conn.commit(); conn.close(); dlg.destroy(); self.refresh_suppliers()
            except Exception as ex:
                conn.rollback(); conn.close(); messagebox.showerror("Error", f"Failed: {ex}")
        ttk.Button(frm, text="Add", command=add).grid(row=len(labels), column=0, columnspan=2, pady=8)

    def dialog_edit_selected_supplier(self):
        sel = self.suppliers_tree.selection()
        if not sel: messagebox.showinfo("Select","Select supplier."); return
        item = self.suppliers_tree.item(sel[0])["values"]; sid = item[0]
        conn = get_conn(); cur = conn.cursor()
        cur.execute("SELECT name,phone,email,address FROM suppliers WHERE id=?", (sid,))
        row = cur.fetchone(); conn.close()
        if not row: messagebox.showerror("Missing","Supplier not found"); return
        dlg = tk.Toplevel(self); dlg.title("Edit Supplier")
        frm = ttk.Frame(dlg, padding=12); frm.pack(fill="both", expand=True)
        labels = ["Name","Phone","Email","Address"]
        vars = [tk.StringVar(value=row[i]) for i in range(4)]
        for i,L in enumerate(labels):
            ttk.Label(frm, text=L+":").grid(row=i, column=0, sticky="e", padx=4, pady=4)
            ttk.Entry(frm, textvariable=vars[i], width=50).grid(row=i, column=1, padx=4, pady=4)
        def save():
            name,phone,email,address = [v.get().strip() for v in vars]
            conn = get_conn(); cur = conn.cursor()
            try:
                cur.execute("UPDATE suppliers SET name=?,phone=?,email=?,address=? WHERE id=?", (name,phone,email,address,sid))
                conn.commit(); conn.close(); dlg.destroy(); self.refresh_suppliers()
            except Exception as ex:
                conn.rollback(); conn.close(); messagebox.showerror("Error", f"Failed: {ex}")
        ttk.Button(frm, text="Save", command=save).grid(row=len(labels), column=0, columnspan=2, pady=8)

    def delete_selected_supplier(self):
        sel = self.suppliers_tree.selection()
        if not sel: messagebox.showinfo("Select","Select supplier."); return
        item = self.suppliers_tree.item(sel[0])["values"]; sid = item[0]
        if not messagebox.askyesno("Delete", f"Delete supplier {sid}?"): return
        conn = get_conn(); cur = conn.cursor()
        try:
            cur.execute("DELETE FROM suppliers WHERE id=?", (sid,)); conn.commit(); conn.close(); self.refresh_suppliers()
        except Exception as ex:
            conn.rollback(); conn.close(); messagebox.showerror("Error", f"Failed: {ex}")

    # ---------------------------
    # Expenses
    # ---------------------------
    def _build_expenses(self):
        frm = self.expenses_tab
        for w in frm.winfo_children(): w.destroy()
        top = ttk.Frame(frm, padding=6); top.pack(fill="x")
        ttk.Button(top, text="Add Expense", command=self.dialog_add_expense).pack(side="left", padx=4)
        ttk.Button(top, text="Delete Expense", command=self.delete_selected_expense).pack(side="left", padx=4)
        self.exp_search_var = tk.StringVar()
        ttk.Label(top, text="Search:").pack(side="left", padx=(12,4))
        ent = ttk.Entry(top, textvariable=self.exp_search_var); ent.pack(side="left", padx=4)
        ent.bind("<Return>", lambda e: self.refresh_expenses())
        tree = ttk.Treeview(frm, columns=("id","date","title","amount","note"), show="headings")
        for col,txt,wid in [("id","ID",50),("date","Date",120),("title","Title",240),("amount","Amount",120),("note","Note",240)]:
            tree.heading(col, text=txt); tree.column(col, width=wid)
        tree.pack(fill="both", expand=True, padx=8, pady=8)
        self.expenses_tree = tree

    def dialog_add_expense(self):
        dlg = tk.Toplevel(self); dlg.title("Add Expense")
        frm = ttk.Frame(dlg, padding=12); frm.pack(fill="both", expand=True)
        date_var = tk.StringVar(value=date.today().isoformat())
        title_var = tk.StringVar()
        amt_var = tk.StringVar()
        note_var = tk.StringVar()
        ttk.Label(frm, text="Date (YYYY-MM-DD):").grid(row=0,column=0,sticky="e", padx=4, pady=4)
        ttk.Entry(frm, textvariable=date_var).grid(row=0,column=1, padx=4, pady=4)
        ttk.Label(frm, text="Title:").grid(row=1,column=0,sticky="e", padx=4, pady=4)
        ttk.Entry(frm, textvariable=title_var).grid(row=1,column=1, padx=4, pady=4)
        ttk.Label(frm, text="Amount:").grid(row=2,column=0,sticky="e", padx=4, pady=4)
        ttk.Entry(frm, textvariable=amt_var).grid(row=2,column=1, padx=4, pady=4)
        ttk.Label(frm, text="Note:").grid(row=3,column=0,sticky="e", padx=4, pady=4)
        ttk.Entry(frm, textvariable=note_var).grid(row=3,column=1, padx=4, pady=4)
        def add():
            dt = date_var.get().strip(); title = title_var.get().strip()
            try:
                amount = float(amt_var.get() or 0.0)
            except:
                messagebox.showerror("Error","Invalid amount"); return
            note = note_var.get().strip()
            conn = get_conn(); cur = conn.cursor()
            try:
                cur.execute("INSERT INTO expenses (date,title,amount,note) VALUES (?,?,?,?)", (dt,title,amount,note))
                conn.commit(); conn.close(); dlg.destroy(); self.refresh_expenses(); self.refresh_dashboard()
            except Exception as ex:
                conn.rollback(); conn.close(); messagebox.showerror("Error", f"Failed: {ex}")
        ttk.Button(frm, text="Add", command=add).grid(row=4, column=0, columnspan=2, pady=8)

    def refresh_expenses(self):
        q = self.exp_search_var.get().strip()
        conn = get_conn(); cur = conn.cursor()
        if q:
            cur.execute("SELECT id,date,title,amount,note FROM expenses WHERE title LIKE ? OR note LIKE ?", (f"%{q}%", f"%{q}%"))
        else:
            cur.execute("SELECT id,date,title,amount,note FROM expenses")
        rows = cur.fetchall(); conn.close()
        tree = self.expenses_tree
        for i in tree.get_children(): tree.delete(i)
        for r in rows:
            tree.insert("", "end", values=(r[0], r[1], r[2], money(r[3]), r[4]))

    def delete_selected_expense(self):
        sel = self.expenses_tree.selection()
        if not sel: messagebox.showinfo("Select","Select expense."); return
        item = self.expenses_tree.item(sel[0])["values"]; eid = item[0]
        if not messagebox.askyesno("Delete", f"Delete expense {eid}?"): return
        conn = get_conn(); cur = conn.cursor()
        try:
            cur.execute("DELETE FROM expenses WHERE id=?", (eid,)); conn.commit(); conn.close(); self.refresh_expenses(); self.refresh_dashboard()
        except Exception as ex:
            conn.rollback(); conn.close(); messagebox.showerror("Error", f"Failed: {ex}")

    # ---------------------------
    # Reports
    # ---------------------------
    def _build_reports(self):
        frm = self.reports_tab
        for w in frm.winfo_children(): w.destroy()
        ttk.Button(frm, text="Export Inventory CSV", command=self.export_inventory_csv).pack(padx=10, pady=6, anchor="w")
        ttk.Button(frm, text="Export Sales CSV", command=self.export_sales_csv).pack(padx=10, pady=6, anchor="w")
        ttk.Button(frm, text="View Recent Sales", command=self.view_recent_sales).pack(padx=10, pady=6, anchor="w")

    def export_inventory_csv(self):
        conn = get_conn(); cur = conn.cursor()
        cur.execute("SELECT sku,name,description,quantity,cost_price,sell_price FROM products")
        rows = cur.fetchall(); conn.close()
        if not rows:
            messagebox.showinfo("Export", "No products to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")], title="Save inventory CSV")
        if not path: return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["SKU","Name","Description","Quantity","Cost Price","Sell Price"])
                for r in rows:
                    w.writerow([r[0], r[1], r[2], r[3], f"{r[4]:.2f}", f"{r[5]:.2f}"])
            messagebox.showinfo("Exported", f"Inventory saved to {path}")
        except Exception as ex:
            messagebox.showerror("Error", f"Export failed: {ex}")

    def export_sales_csv(self):
        conn = get_conn(); cur = conn.cursor()
        cur.execute("SELECT id,date,customer_id,total_amount,paid FROM sales")
        rows = cur.fetchall(); conn.close()
        if not rows:
            messagebox.showinfo("Export", "No sales to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")], title="Save sales CSV")
        if not path: return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["Sale ID","Date","Customer ID","Total Amount","Paid"])
                for r in rows:
                    w.writerow([r[0], r[1], r[2], f"{r[3]:.2f}", r[4]])
            messagebox.showinfo("Exported", f"Sales saved to {path}")
        except Exception as ex:
            messagebox.showerror("Error", f"Export failed: {ex}")

    def view_recent_sales(self):
        conn = get_conn(); cur = conn.cursor()
        cur.execute("SELECT id,date,customer_id,total_amount FROM sales ORDER BY date DESC LIMIT 20")
        rows = cur.fetchall(); conn.close()
        dlg = tk.Toplevel(self); dlg.title("Recent Sales")
        tree = ttk.Treeview(dlg, columns=("id","date","cust","amount"), show="headings")
        tree.heading("id", text="ID"); tree.heading("date", text="Date"); tree.heading("cust", text="Customer"); tree.heading("amount", text="Amount")
        tree.column("amount", anchor="e")
        tree.pack(fill="both", expand=True)
        for r in rows:
            tree.insert("", "end", values=(r[0], r[1], r[2], money(r[3])))

    # ---------------------------
    # Settings
    # ---------------------------
    def _build_settings(self):
        frm = self.settings_tab
        for w in frm.winfo_children(): w.destroy()
        ttk.Label(frm, text="Appearance & Settings", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=12, pady=8)
        ttk.Label(frm, text="Themes available: Blue, Red, Yellow, White").pack(anchor="w", padx=12, pady=4)
        ttk.Button(frm, text="Open data folder", command=lambda: os.startfile(os.getcwd()) if os.name == "nt" else None).pack(anchor="w", padx=12, pady=6)

    # ---------------------------
    # Misc utilities
    # ---------------------------
    def refresh_all(self):
        self.refresh_products(); self.refresh_customers(); self.refresh_suppliers(); self.refresh_expenses(); self.refresh_dashboard(); self.refresh_pos_products()

    def select_tab_by_text(self, text):
        nb = None
        for child in self.winfo_children():
            if isinstance(child, ttk.Notebook):
                nb = child; break
        if not nb: return
        for i in range(nb.index("end")):
            if nb.tab(i, "text") == text:
                nb.select(i); return

    # ---------------------------
    # Self-test routine
    # ---------------------------
    def run_self_test(self):
        # Disable button
        self.test_btn.config(state="disabled")
        failures = []
        results = []
        try:
            # 1) Add temp product
            conn = get_conn(); cur = conn.cursor()
            cur.execute("INSERT INTO products (sku,name,description,quantity,cost_price,sell_price) VALUES (?,?,?,?,?,?)",
                        ("TST-001","Test Widget","Auto test product",10,1.25,2.50))
            pid = cur.lastrowid
            conn.commit()
            results.append("Added product TST-001")
            # 2) Add a customer
            cur.execute("INSERT INTO customers (name,phone,email) VALUES (?,?,?)", ("Test Buyer","000","test@example.com"))
            cid = cur.lastrowid; conn.commit()
            results.append("Added customer")
            # 3) Create a sale programmatically
            now = datetime.now().isoformat()
            cur.execute("INSERT INTO sales (date,customer_id,total_amount,paid,user_id) VALUES (?,?,?,?,?)", (now, cid, 5.0, 1, None))
            sale_id = cur.lastrowid
            cur.execute("INSERT INTO sale_lines (sale_id,product_id,qty,price,line_total) VALUES (?,?,?,?,?)", (sale_id,pid,2,2.50,5.0))
            # decrement inventory
            cur.execute("UPDATE products SET quantity = quantity - ? WHERE id=?", (2, pid))
            conn.commit()
            results.append(f"Created sale {sale_id}")
            # 4) Export inventory CSV to a temp file
            tmp_path = os.path.join(os.getcwd(), "tmp_inventory_export.csv")
            cur.execute("SELECT sku,name,description,quantity,cost_price,sell_price FROM products")
            rows = cur.fetchall()
            with open(tmp_path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f); w.writerow(["SKU","Name","Desc","Qty","Cost","Sell"])
                for r in rows: w.writerow([r[0], r[1], r[2], r[3], f"{r[4]:.2f}", f"{r[5]:.2f}"])
            results.append("Exported inventory CSV")
            # 5) Cleanup test product & customer
            cur.execute("DELETE FROM sale_lines WHERE sale_id=?", (sale_id,))
            cur.execute("DELETE FROM sales WHERE id=?", (sale_id,))
            cur.execute("DELETE FROM products WHERE id=?", (pid,))
            cur.execute("DELETE FROM customers WHERE id=?", (cid,))
            conn.commit(); conn.close()
            results.append("Cleaned up test data")
        except Exception as ex:
            failures.append(str(ex))
        finally:
            self.test_btn.config(state="normal")
        if failures:
            messagebox.showerror("Self-Test Failed", "Errors:\n" + "\n".join(failures))
        else:
            messagebox.showinfo("Self-Test Passed", "All automated checks passed:\n" + "\n".join(results))

# ---------------------------
# Entrypoint
# ---------------------------
if __name__ == "__main__":
    init_db()
    app = ShopApp()
    app.mainloop()
