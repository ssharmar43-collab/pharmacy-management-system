================================================================================
                    PHARMACY MANAGEMENT SYSTEM
================================================================================

LOGIN CREDENTIALS:
- Username: admin
- Password: admin123

================================================================================
PART 1: DATABASE CREATION QUERIES (DDL)
================================================================================

These queries run automatically when the app starts. They create the database 
and all tables.

-------------------------------------------------------------------------------
QUERY 1: Create Database
-------------------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS PharmacyDB;

Purpose: Creates a new database named PharmacyDB to store all pharmacy data.

-------------------------------------------------------------------------------
QUERY 2: Create Users Table
-------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) DEFAULT 'staff'
);

Purpose: Stores user login information. Primary Key is user_id. 
         Username must be unique.

-------------------------------------------------------------------------------
QUERY 3: Create Medicines Table
-------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS medicines (
    medicine_id INT PRIMARY KEY AUTO_INCREMENT,
    medicine_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    manufacturer VARCHAR(100),
    price DECIMAL(10,2) NOT NULL,
    quantity INT DEFAULT 0,
    reorder_level INT DEFAULT 10,
    expiry_date DATE
);

Purpose: Stores all medicine inventory details. Primary Key is medicine_id.

-------------------------------------------------------------------------------
QUERY 4: Create Customers Table
-------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_name VARCHAR(100) NOT NULL,
    phone VARCHAR(15),
    registration_date DATE
);

Purpose: Stores customer information.

-------------------------------------------------------------------------------
QUERY 5: Create Sales Table
-------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sales (
    sale_id INT PRIMARY KEY AUTO_INCREMENT,
    invoice_no VARCHAR(20) UNIQUE,
    customer_id INT,
    sale_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    grand_total DECIMAL(10,2),
    payment_method VARCHAR(20),
    user_id INT
);

Purpose: Stores each bill/sale transaction. 
         Foreign Key user_id references users table.

-------------------------------------------------------------------------------
QUERY 6: Create Sale Items Table
-------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sale_items (
    sale_item_id INT PRIMARY KEY AUTO_INCREMENT,
    sale_id INT,
    medicine_id INT,
    quantity INT,
    unit_price DECIMAL(10,2),
    total_price DECIMAL(10,2)
);

Purpose: Stores individual items in each bill.
         Foreign Key sale_id references sales table.
         Foreign Key medicine_id references medicines table.

================================================================================
PART 2: INSERT QUERIES (DML)
================================================================================

-------------------------------------------------------------------------------
QUERY 7: Insert Admin User
-------------------------------------------------------------------------------
INSERT INTO users (username, password, full_name, role) 
VALUES ('admin', MD5('admin123'), 'Administrator', 'admin');

Purpose: Adds the default admin user so someone can login.
         MD5() encrypts the password.

-------------------------------------------------------------------------------
QUERY 8: Insert Sample Medicines
-------------------------------------------------------------------------------
INSERT INTO medicines (medicine_name, category, manufacturer, price, quantity, reorder_level, expiry_date) 
VALUES ('Paracetamol 500mg', 'Painkiller', 'Cipla', 25.00, 100, 20, '2025-12-31');

Purpose: Adds sample medicines so the inventory is not empty when app starts.

-------------------------------------------------------------------------------
QUERY 9: Add New Medicine (from Add Medicine button)
-------------------------------------------------------------------------------
INSERT INTO medicines (medicine_name, category, manufacturer, price, quantity, reorder_level, expiry_date) 
VALUES (%s, %s, %s, %s, %s, %s, %s);

Purpose: Adds a new medicine entered by the user through the form.
         %s are placeholders for user input values.

-------------------------------------------------------------------------------
QUERY 10: Create New Sale (when generating bill)
-------------------------------------------------------------------------------
INSERT INTO sales (invoice_no, grand_total, payment_method, user_id) 
VALUES (%s, %s, %s, %s);

Purpose: Creates a new bill record when user clicks "Generate Bill".

-------------------------------------------------------------------------------
QUERY 11: Add Items to Sale
-------------------------------------------------------------------------------
INSERT INTO sale_items (sale_id, medicine_id, quantity, unit_price, total_price) 
VALUES (%s, %s, %s, %s, %s);

Purpose: Adds each medicine to the current bill.

================================================================================
PART 3: SELECT QUERIES (DML)
================================================================================

-------------------------------------------------------------------------------
QUERY 12: Login Authentication
-------------------------------------------------------------------------------
SELECT * FROM users WHERE username=%s AND password=MD5(%s);

Purpose: Checks if username and password match. Allows user to login.

-------------------------------------------------------------------------------
QUERY 13: Get Total Medicines Count (Dashboard)
-------------------------------------------------------------------------------
SELECT COUNT(*) FROM medicines;

Purpose: Shows how many medicines are in the inventory on the dashboard.

-------------------------------------------------------------------------------
QUERY 14: Get Total Stock Quantity (Dashboard)
-------------------------------------------------------------------------------
SELECT SUM(quantity) FROM medicines;

Purpose: Shows total number of medicine units in stock.

-------------------------------------------------------------------------------
QUERY 15: Get Today's Sales Count (Dashboard)
-------------------------------------------------------------------------------
SELECT COUNT(*) FROM sales WHERE DATE(sale_date)=CURDATE();

Purpose: Shows how many bills were generated today.

-------------------------------------------------------------------------------
QUERY 16: View All Medicines (Inventory Page)
-------------------------------------------------------------------------------
SELECT medicine_id, medicine_name, category, manufacturer, price, quantity, expiry_date 
FROM medicines;

Purpose: Displays all medicines in a table format.

-------------------------------------------------------------------------------
QUERY 17: Search Medicines by Name
-------------------------------------------------------------------------------
SELECT * FROM medicines WHERE medicine_name LIKE %s;

Purpose: Filters medicines based on user search input.

-------------------------------------------------------------------------------
QUERY 18: Get Available Medicines for Billing
-------------------------------------------------------------------------------
SELECT medicine_id, medicine_name, price, quantity 
FROM medicines WHERE quantity > 0;

Purpose: Shows only medicines that are in stock for billing dropdown.

-------------------------------------------------------------------------------
QUERY 19: View All Sales (Report Page)
-------------------------------------------------------------------------------
SELECT DATE(sale_date), invoice_no, grand_total, payment_method 
FROM sales ORDER BY sale_date DESC;

Purpose: Displays all sales transactions for the report.

-------------------------------------------------------------------------------
QUERY 20: Get Total Revenue (Report Page)
-------------------------------------------------------------------------------
SELECT SUM(grand_total) FROM sales;

Purpose: Calculates total money earned from all sales.

-------------------------------------------------------------------------------
QUERY 21: Get Last Inserted Sale ID
-------------------------------------------------------------------------------
SELECT LAST_INSERT_ID();

Purpose: Gets the ID of the most recently created sale to link sale items.

================================================================================
PART 4: UPDATE QUERIES (DML)
================================================================================

-------------------------------------------------------------------------------
QUERY 22: Deduct Stock After Sale
-------------------------------------------------------------------------------
UPDATE medicines SET quantity = quantity - %s WHERE medicine_id = %s;

Purpose: Reduces medicine quantity when sold. Ensures stock stays accurate.

================================================================================
PART 5: PYTHON CODE FOR DATABASE CONNECTION
================================================================================

-------------------------------------------------------------------------------
Code 1: Database Connection Function
-------------------------------------------------------------------------------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="mysql",
        database="PharmacyDB"
    );

Purpose: Connects Python to MySQL database. Change password if needed.

-------------------------------------------------------------------------------
Code 2: Auto Setup Function
-------------------------------------------------------------------------------
def setup_database():
    conn = mysql.connector.connect(host="localhost", user="root", password="mysql")
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS PharmacyDB")
    cursor.execute("USE PharmacyDB")
    # ... all CREATE TABLE queries here ...
    conn.commit()

Purpose: Runs automatically when app starts. Creates everything if not exists.

-------------------------------------------------------------------------------
Code 3: Login Function
-------------------------------------------------------------------------------
def do_login(self):
    username = self.login_user.get()
    password = self.login_pass.get()
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=MD5(%s)", 
                   (username, password))
    user = cursor.fetchone()

Purpose: Gets user input, checks database, allows login if correct.

-------------------------------------------------------------------------------
Code 4: Add Medicine Function
-------------------------------------------------------------------------------
def save_medicine(self):
    cursor.execute("""INSERT INTO medicines 
                      (medicine_name, category, manufacturer, price, quantity, 
                       reorder_level, expiry_date)
                      VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                   (name, category, manufacturer, price, qty, reorder, expiry))

Purpose: Takes form input and saves new medicine to database.

-------------------------------------------------------------------------------
Code 5: Generate Bill Function
-------------------------------------------------------------------------------
def generate_bill(self):
    # Insert sale
    cursor.execute("INSERT INTO sales (invoice_no, grand_total, payment_method, user_id) 
                    VALUES (%s, %s, %s, %s)", 
                   (invoice_no, self.total_amount, payment, user_id))
    
    # Insert each item
    for item in self.cart_items:
        cursor.execute("INSERT INTO sale_items (sale_id, medicine_id, quantity, 
                       unit_price, total_price) VALUES (%s, %s, %s, %s, %s)",
                       (sale_id, item['id'], item['qty'], item['price'], item['total']))
        
        # Update stock
        cursor.execute("UPDATE medicines SET quantity = quantity - %s 
                       WHERE medicine_id = %s", 
                       (item['qty'], item['id']))

Purpose: Creates bill, adds items, reduces stock - all in one transaction.

================================================================================
PART 6: HOW TO RUN THE PROJECT
================================================================================

Step 1: Install MySQL from https://dev.mysql.com/downloads/installer/
        Set root password as: mysql

Step 2: Install Python Package
        pip install mysql-connector-python

Step 3: Save the code as pharmacy_app.py

Step 4: Run the application
        python pharmacy_app.py

Step 5: Login with: admin / admin123

================================================================================
PROJECT FILE STRUCTURE
================================================================================

Desktop/
└── PharmacySystem/
    ├── pharmacy_app.py    (Main application - contains all code and queries)
    └── README.txt         (This file)

================================================================================
SUMMARY OF WHAT THIS PROJECT DEMONSTRATES
================================================================================

1. Database Creation (CREATE DATABASE)
2. Table Creation with Constraints (CREATE TABLE with PRIMARY KEY, FOREIGN KEY)
3. Data Insertion (INSERT INTO)
4. Data Retrieval (SELECT, SELECT with WHERE, SELECT with LIKE)
5. Data Update (UPDATE)
6. Aggregate Functions (COUNT, SUM)
7. Date Functions (CURDATE(), DATE())
8. Encryption (MD5 for passwords)
9. Foreign Key Relationships (links tables together)
10. Python-MySQL Integration

================================================================================
END OF DOCUMENTATION
================================================================================