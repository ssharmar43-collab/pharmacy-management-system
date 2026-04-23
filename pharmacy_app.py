"""
PHARMACY MANAGEMENT SYSTEM - Complete Setup
Everything runs from this single file.
No need to open MySQL command line.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
from datetime import datetime

# Database password
DB_PASSWORD = "mysql"

def setup_database():
    """Automatically create database and tables"""
    try:
        # Connect without database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS PharmacyDB")
        cursor.execute("USE PharmacyDB")
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                role VARCHAR(20) DEFAULT 'staff'
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medicines (
                medicine_id INT PRIMARY KEY AUTO_INCREMENT,
                medicine_name VARCHAR(100) NOT NULL,
                category VARCHAR(50),
                manufacturer VARCHAR(100),
                price DECIMAL(10,2) NOT NULL,
                quantity INT DEFAULT 0,
                reorder_level INT DEFAULT 10,
                expiry_date DATE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INT PRIMARY KEY AUTO_INCREMENT,
                customer_name VARCHAR(100) NOT NULL,
                phone VARCHAR(15),
                registration_date DATE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                sale_id INT PRIMARY KEY AUTO_INCREMENT,
                invoice_no VARCHAR(20) UNIQUE,
                customer_id INT,
                sale_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                grand_total DECIMAL(10,2),
                payment_method VARCHAR(20),
                user_id INT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sale_items (
                sale_item_id INT PRIMARY KEY AUTO_INCREMENT,
                sale_id INT,
                medicine_id INT,
                quantity INT,
                unit_price DECIMAL(10,2),
                total_price DECIMAL(10,2)
            )
        """)
        
        # Insert admin user if not exists
        cursor.execute("SELECT * FROM users WHERE username='admin'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users (username, password, full_name, role) VALUES ('admin', MD5('admin123'), 'Administrator', 'admin')")
        
        # Insert sample medicines if empty
        cursor.execute("SELECT COUNT(*) FROM medicines")
        if cursor.fetchone()[0] == 0:
            medicines = [
                ('Paracetamol 500mg', 'Painkiller', 'Cipla', 25.00, 100, 20, '2025-12-31'),
                ('Crocin 650mg', 'Painkiller', 'GSK', 30.00, 80, 15, '2025-11-30'),
                ('Dolo 650mg', 'Fever', 'Micro Labs', 28.00, 120, 25, '2025-10-15'),
                ('Azithromycin 500mg', 'Antibiotic', 'Cipla', 120.00, 50, 10, '2025-09-30'),
                ('Insulin R', 'Diabetes', 'Eli Lilly', 450.00, 30, 5, '2025-08-15'),
                ('Amoxicillin 250mg', 'Antibiotic', 'GSK', 45.00, 60, 12, '2025-12-20'),
                ('Cetrizine 10mg', 'Antihistamine', 'Sun Pharma', 35.00, 90, 15, '2026-01-10'),
                ('Vitamin C 500mg', 'Vitamin', 'Abbott', 50.00, 150, 25, '2025-12-31'),
            ]
            cursor.executemany("INSERT INTO medicines (medicine_name, category, manufacturer, price, quantity, reorder_level, expiry_date) VALUES (%s, %s, %s, %s, %s, %s, %s)", medicines)
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Database Error", f"Error setting up database: {str(e)}\n\nMake sure MySQL is installed and password is 'mysql'")
        return False

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=DB_PASSWORD,
        database="PharmacyDB"
    )

class PharmacyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pharmacy Management System")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f0f0')
        
        self.current_user = None
        self.cart_items = []
        self.total_amount = 0
        
        # Setup database on startup
        if not setup_database():
            self.root.destroy()
            return
        
        self.show_login()
    
    def show_login(self):
        """Login Screen"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.place(relx=0.5, rely=0.5, anchor='center', width=400, height=350)
        
        tk.Label(main_frame, text="💊 Pharmacy Management", font=('Arial', 16, 'bold'),
                 bg='#2c3e50', fg='white').pack(pady=20)
        
        tk.Label(main_frame, text="Username:", bg='#2c3e50', fg='white').pack(pady=(20, 0))
        self.login_user = tk.Entry(main_frame, width=30)
        self.login_user.pack(pady=5)
        
        tk.Label(main_frame, text="Password:", bg='#2c3e50', fg='white').pack()
        self.login_pass = tk.Entry(main_frame, width=30, show='*')
        self.login_pass.pack(pady=5)
        
        tk.Button(main_frame, text="Login", command=self.do_login, bg='#27ae60', fg='white',
                  width=20).pack(pady=20)
        
        # Show credentials
        tk.Label(main_frame, text="Use: admin / admin123", bg='#2c3e50', fg='gray').pack()
    
    def do_login(self):
        username = self.login_user.get()
        password = self.login_pass.get()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=MD5(%s)", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            self.current_user = user
            self.show_dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials!\nUse: admin / admin123")
    
    def show_dashboard(self):
        """Main Dashboard"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Header
        header = tk.Frame(self.root, bg='#2c3e50', height=60)
        header.pack(fill='x')
        tk.Label(header, text="💊 Pharmacy Management System", font=('Arial', 18, 'bold'),
                 fg='white', bg='#2c3e50').pack(side='left', padx=20)
        tk.Label(header, text=f"Welcome, {self.current_user[3]}", font=('Arial', 12),
                 fg='white', bg='#2c3e50').pack(side='right', padx=20)
        
        # Navigation Buttons
        nav_frame = tk.Frame(self.root, bg='#34495e', height=50)
        nav_frame.pack(fill='x')
        
        buttons = [
            ("➕ Add Medicine", self.show_add_medicine),
            ("📋 View Medicines", self.show_medicines),
            ("🧾 New Bill", self.show_billing),
            ("📊 Sales Report", self.show_report),
            ("🚪 Logout", self.show_login),
        ]
        
        for text, cmd in buttons:
            tk.Button(nav_frame, text=text, command=cmd, bg='#34495e', fg='white',
                      font=('Arial', 11), padx=15).pack(side='left', padx=5, pady=10)
        
        # Content Area
        self.content_frame = tk.Frame(self.root, bg='white')
        self.content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Dashboard Stats
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM medicines")
        med_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(quantity) FROM medicines")
        total_stock = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM sales WHERE DATE(sale_date)=CURDATE()")
        today_sales = cursor.fetchone()[0]
        
        conn.close()
        
        stats_frame = tk.Frame(self.content_frame, bg='white')
        stats_frame.pack(pady=20)
        
        stats = [
            ("💊 Total Medicines", str(med_count), "#3498db"),
            ("📦 Stock Items", str(total_stock), "#27ae60"),
            ("💰 Today's Bills", str(today_sales), "#e67e22"),
        ]
        
        for i, (title, value, color) in enumerate(stats):
            card = tk.Frame(stats_frame, bg=color, relief=tk.RIDGE, bd=2)
            card.grid(row=0, column=i, padx=10, pady=10, ipadx=30, ipady=20)
            tk.Label(card, text=title, font=('Arial', 12), fg='white', bg=color).pack()
            tk.Label(card, text=value, font=('Arial', 24, 'bold'), fg='white', bg=color).pack()
        
        # Recent Medicines
        tk.Label(self.content_frame, text="📋 Recent Medicines", font=('Arial', 14, 'bold'),
                 bg='white', fg='#2c3e50').pack(anchor='w', pady=(20, 5))
        
        columns = ('ID', 'Name', 'Price', 'Stock')
        tree = ttk.Treeview(self.content_frame, columns=columns, show='headings', height=5)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        tree.pack(fill='x', padx=10)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT medicine_id, medicine_name, price, quantity FROM medicines LIMIT 5")
        for med in cursor.fetchall():
            tree.insert('', 'end', values=(med[0], med[1], f"₹{med[2]}", med[3]))
        conn.close()
    
    def show_add_medicine(self):
        """Add Medicine Form"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.content_frame, text="➕ Add New Medicine", font=('Arial', 18, 'bold'),
                 fg='#2c3e50', bg='white').pack(pady=10)
        
        form_frame = tk.Frame(self.content_frame, bg='white')
        form_frame.pack(pady=20)
        
        fields = [
            ("Medicine Name:", "name"),
            ("Category:", "category"),
            ("Manufacturer:", "manufacturer"),
            ("Price (₹):", "price"),
            ("Quantity:", "qty"),
            ("Reorder Level:", "reorder"),
            ("Expiry Date (YYYY-MM-DD):", "expiry"),
        ]
        
        self.entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(form_frame, text=label, bg='white').grid(row=i, column=0, padx=10, pady=5)
            entry = tk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries[key] = entry
        
        tk.Button(self.content_frame, text="💾 Save Medicine", command=self.save_medicine,
                  bg='#27ae60', fg='white', padx=20, pady=5).pack(pady=20)
    
    def save_medicine(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO medicines 
                              (medicine_name, category, manufacturer, price, quantity, reorder_level, expiry_date)
                              VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                           (self.entries['name'].get(),
                            self.entries['category'].get(),
                            self.entries['manufacturer'].get(),
                            float(self.entries['price'].get()),
                            int(self.entries['qty'].get()),
                            int(self.entries['reorder'].get()),
                            self.entries['expiry'].get()))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Medicine added successfully!")
            self.show_medicines()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def show_medicines(self):
        """View All Medicines"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.content_frame, text="📋 Medicine Inventory", font=('Arial', 18, 'bold'),
                 fg='#2c3e50', bg='white').pack(pady=10)
        
        # Search
        search_frame = tk.Frame(self.content_frame, bg='white')
        search_frame.pack(pady=10)
        tk.Label(search_frame, text="🔍 Search:", bg='white').pack(side='left')
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side='left', padx=5)
        tk.Button(search_frame, text="Search", command=self.search_medicine, bg='#3498db', fg='white').pack(side='left')
        tk.Button(search_frame, text="Refresh", command=self.show_medicines, bg='#27ae60', fg='white').pack(side='left', padx=5)
        
        # Treeview
        columns = ('ID', 'Name', 'Category', 'Manufacturer', 'Price', 'Stock', 'Expiry')
        self.tree = ttk.Treeview(self.content_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        
        self.tree.pack(fill='both', expand=True, padx=20)
        
        self.load_medicines()
    
    def load_medicines(self, search=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if search:
            cursor.execute("SELECT * FROM medicines WHERE medicine_name LIKE %s", (f'%{search}%',))
        else:
            cursor.execute("SELECT medicine_id, medicine_name, category, manufacturer, price, quantity, expiry_date FROM medicines")
        
        for med in cursor.fetchall():
            self.tree.insert('', 'end', values=(med[0], med[1], med[2], med[3], f"₹{med[4]}", med[5], med[6]))
        
        conn.close()
    
    def search_medicine(self):
        search = self.search_entry.get()
        self.load_medicines(search)
    
    def show_billing(self):
        """Billing Section"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        self.cart_items = []
        self.total_amount = 0
        
        tk.Label(self.content_frame, text="🧾 New Bill", font=('Arial', 18, 'bold'),
                 fg='#2c3e50', bg='white').pack(pady=10)
        
        # Two columns
        main_frame = tk.Frame(self.content_frame, bg='white')
        main_frame.pack(fill='both', expand=True)
        
        # LEFT PANEL
        left_frame = tk.Frame(main_frame, bg='white', relief=tk.RIDGE, bd=2)
        left_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(left_frame, text="🛒 Select Medicine", font=('Arial', 14, 'bold'), bg='white').pack(pady=10)
        
        self.med_combo = ttk.Combobox(left_frame, width=40)
        self.med_combo.pack(pady=10)
        self.load_medicines_to_combo()
        
        tk.Label(left_frame, text="Quantity:", bg='white').pack()
        self.qty_entry = tk.Entry(left_frame, width=20)
        self.qty_entry.pack(pady=5)
        
        tk.Button(left_frame, text="➕ Add to Cart", command=self.add_to_cart,
                  bg='#27ae60', fg='white', width=20, padx=10, pady=5).pack(pady=10)
        
        # RIGHT PANEL
        right_frame = tk.Frame(main_frame, bg='white', relief=tk.RIDGE, bd=2)
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(right_frame, text="🛍️ Cart", font=('Arial', 14, 'bold'), bg='white').pack(pady=10)
        
        columns = ('Medicine', 'Qty', 'Price', 'Total')
        self.cart_tree = ttk.Treeview(right_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=120)
        
        self.cart_tree.pack(fill='both', expand=True, padx=10)
        
        # Total
        total_frame = tk.Frame(right_frame, bg='white')
        total_frame.pack(fill='x', pady=10)
        
        tk.Label(total_frame, text="Total: ₹", font=('Arial', 16, 'bold'), bg='white').pack(side='left', padx=10)
        self.total_label = tk.Label(total_frame, text="0", font=('Arial', 16, 'bold'), fg='green', bg='white')
        self.total_label.pack(side='left')
        
        tk.Label(total_frame, text="Payment:", bg='white').pack(side='left', padx=20)
        self.payment_combo = ttk.Combobox(total_frame, values=['cash', 'card', 'upi'], width=10)
        self.payment_combo.pack(side='left')
        self.payment_combo.set('cash')
        
        tk.Button(total_frame, text="✅ Generate Bill", command=self.generate_bill,
                  bg='#3498db', fg='white', padx=20, pady=5).pack(side='right', padx=10)
    
    def load_medicines_to_combo(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT medicine_id, medicine_name, price, quantity FROM medicines WHERE quantity > 0")
        self.med_list = cursor.fetchall()
        conn.close()
        
        med_display = [f"{m[1]} - ₹{m[2]} (Stock: {m[3]})" for m in self.med_list]
        self.med_combo['values'] = med_display
    
    def add_to_cart(self):
        selection = self.med_combo.get()
        if not selection:
            messagebox.showwarning("Warning", "Please select a medicine!")
            return
        
        try:
            qty = int(self.qty_entry.get())
            if qty <= 0:
                raise ValueError
        except:
            messagebox.showerror("Error", "Please enter valid quantity!")
            return
        
        for med in self.med_list:
            if med[1] in selection:
                if qty > med[3]:
                    messagebox.showerror("Error", f"Only {med[3]} units available!")
                    return
                
                total = med[2] * qty
                self.cart_items.append({
                    'id': med[0], 'name': med[1], 'price': med[2], 'qty': qty, 'total': total
                })
                self.total_amount += total
                self.total_label.config(text=str(self.total_amount))
                
                self.cart_tree.insert('', 'end', values=(med[1], qty, f"₹{med[2]}", f"₹{total}"))
                self.qty_entry.delete(0, 'end')
                break
    
    def generate_bill(self):
        if not self.cart_items:
            messagebox.showwarning("Warning", "Cart is empty!")
            return
        
        invoice_no = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO sales (invoice_no, grand_total, payment_method, user_id) VALUES (%s, %s, %s, %s)",
                       (invoice_no, self.total_amount, self.payment_combo.get(), self.current_user[0]))
        conn.commit()
        
        cursor.execute("SELECT LAST_INSERT_ID()")
        sale_id = cursor.fetchone()[0]
        
        for item in self.cart_items:
            cursor.execute("INSERT INTO sale_items (sale_id, medicine_id, quantity, unit_price, total_price) VALUES (%s, %s, %s, %s, %s)",
                           (sale_id, item['id'], item['qty'], item['price'], item['total']))
            cursor.execute("UPDATE medicines SET quantity = quantity - %s WHERE medicine_id = %s",
                           (item['qty'], item['id']))
        
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Success", f"Bill Generated!\nInvoice: {invoice_no}\nTotal: ₹{self.total_amount}")
        self.show_billing()
    
    def show_report(self):
        """Sales Report"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.content_frame, text="📊 Sales Report", font=('Arial', 18, 'bold'),
                 fg='#2c3e50', bg='white').pack(pady=10)
        
        columns = ('Date', 'Invoice', 'Total', 'Payment')
        tree = ttk.Treeview(self.content_frame, columns=columns, show='headings', height=18)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=180)
        
        tree.pack(fill='both', expand=True, padx=20)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DATE(sale_date), invoice_no, grand_total, payment_method FROM sales ORDER BY sale_date DESC")
        
        for sale in cursor.fetchall():
            tree.insert('', 'end', values=sale)
        
        cursor.execute("SELECT SUM(grand_total) FROM sales")
        total = cursor.fetchone()[0] or 0
        conn.close()
        
        tk.Label(self.content_frame, text=f"💰 Total Revenue: ₹{total}", font=('Arial', 16, 'bold'),
                 fg='green', bg='white').pack(pady=10)

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = PharmacyApp(root)
    root.mainloop()