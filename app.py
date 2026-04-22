from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# 1. THE DATABASE SETUP FUNCTION (This was missing or undefined)
def init_db():
    conn = sqlite3.connect('vendors.db')
    cursor = conn.cursor()
    # Creating the 6 tables exactly as per the BHEL report specs
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS vendors (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT);
        CREATE TABLE IF NOT EXISTS ratings (vendor_id INTEGER, rating REAL, FOREIGN KEY(vendor_id) REFERENCES vendors(id));
        CREATE TABLE IF NOT EXISTS loads (vendor_id INTEGER, load INTEGER, FOREIGN KEY(vendor_id) REFERENCES vendors(id));
        CREATE TABLE IF NOT EXISTS deliveries (vendor_id INTEGER, delivery_date TEXT, FOREIGN KEY(vendor_id) REFERENCES vendors(id));
        CREATE TABLE IF NOT EXISTS machines (vendor_id INTEGER, machine_type TEXT, FOREIGN KEY(vendor_id) REFERENCES vendors(id));
        CREATE TABLE IF NOT EXISTS contacts (vendor_id INTEGER, phone TEXT, email TEXT, FOREIGN KEY(vendor_id) REFERENCES vendors(id));
    ''')
    conn.commit()
    conn.close()
    print("Database initialized and vendors.db created successfully!")

# 2. DATA RETRIEVAL LOGIC
def get_vendor_details(min_rating=0, max_load=1000, max_date="9999-12-31"):
    conn = sqlite3.connect('vendors.db')
    cursor = conn.cursor()
    query = """
        SELECT v.name, r.rating, l.load, d.delivery_date, m.machine_type, c.phone, c.email
        FROM vendors v
        JOIN ratings r ON v.id = r.vendor_id
        JOIN loads l ON v.id = l.vendor_id
        JOIN deliveries d ON v.id = d.vendor_id
        JOIN machines m ON v.id = m.vendor_id
        JOIN contacts c ON v.id = c.vendor_id
        WHERE r.rating >= ? AND l.load <= ? AND d.delivery_date <= ?
        ORDER BY d.delivery_date ASC
    """
    cursor.execute(query, (min_rating, max_load, max_date))
    rows = cursor.fetchall()
    conn.close()
    return rows

# 3. ROUTES (WEB PAGES)
@app.route('/')
def home():
    return redirect('/vendor_list')

@app.route('/add_vendor', methods=['GET', 'POST'])
def add_vendor():
    if request.method == 'POST':
        name = request.form['name']
        rating = float(request.form['rating'])
        load = int(request.form['load'])
        delivery_date = request.form['delivery_date']
        machine_type = request.form['machine_type']
        phone = request.form['phone']
        email = request.form['email']

        conn = sqlite3.connect('vendors.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO vendors (name) VALUES (?)", (name,))
        v_id = cursor.lastrowid
        cursor.execute("INSERT INTO ratings VALUES (?, ?)", (v_id, rating))
        cursor.execute("INSERT INTO loads VALUES (?, ?)", (v_id, load))
        cursor.execute("INSERT INTO deliveries VALUES (?, ?)", (v_id, delivery_date))
        cursor.execute("INSERT INTO machines VALUES (?, ?)", (v_id, machine_type))
        cursor.execute("INSERT INTO contacts VALUES (?, ?, ?)", (v_id, phone, email))
        conn.commit()
        conn.close()
        return redirect('/vendor_list')
    return render_template('add_vendor.html')

@app.route('/vendor_list', methods=['GET', 'POST'])
def vendor_list():
    if request.method == 'POST':
        min_r = float(request.form.get('min_rating') or 0)
        max_l = int(request.form.get('max_load') or 10000)
        max_d = request.form.get('max_date') or "9999-12-31"
        vendors = get_vendor_details(min_r, max_l, max_d)
    else:
        vendors = get_vendor_details()
    return render_template('vendor_list.html', vendors=vendors)

# 4. START THE APP
if __name__ == '__main__':
    init_db()  # This calls the function defined at the top
    app.run(debug=True)