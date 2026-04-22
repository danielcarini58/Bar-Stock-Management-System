from flask import Flask, request, jsonify, render_template
from flask_cors import CORS 
import sqlite3
from dotenv import load_dotenv
load_dotenv()
import os
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

app = Flask(__name__, template_folder="Templates")
CORS(app)

def get_status(stock):
    if stock == 0:
        return "Out of Stock"
    elif stock <= 3:
        return "Critical"
    elif stock <=10:
        return "Low Stock"
    else:
        return "In Stock"
@app.route("/")
def home():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("index.html")

@app.route("/sidebar")
def sidebar():
    return render_template("components/sidebar.html")

@app.route("/inventory")
def inventory():
    return render_template("inventory.html")

@app.route("/sales")
def sales():
    return render_template("sales.html")

@app.route("/purchases")
def purchases():
    return render_template("purchases.html")

@app.route("/reports")
def reports():
    return render_template("reports.html")

@app.route("/debug-db")
def debug_db():
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    return{
        "db_path": DB_PATH,
        "tables": tables
    }

@app.route("/debug-db-path")
def debug_db_path():
    return {"db_path":DB_PATH}

@app.route("/init_db")
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS purchases (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   order_id INTEGER NOT NULL,
                   supplier TEXT NOT NULL,
                   description TEXT NOT NULL,
                   purchase_date TEXT NOT NULL,
                   status TEXT NOT NULL
               )""")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS purchase_items (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   purchase_id INTEGER NOT NULL,
                   item_id INTEGER NOT NULL,
                   quantity INTEGER NOT NULL)""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS waste(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    waste_date TEXT NOT NULL,
    cost REAL NOT NULL,      
    reason TEXT NOT NULL,                
    FOREIGN KEY (item_id) REFERENCES items(id)
)""")
    
    conn.commit()
    conn.close()

    return {"message": "Database initialized"}

@app.route("/ai", methods=["POST"])
def ai():  
    data = request.json
    message = data.get("message").lower()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if "low stock" in message or "reorder" in message:
        cursor.execute("SELECT name, stock FROM items WHERE stock < 5")
        items = cursor.fetchall()
        conn.close()
        if items:
            text = "\n".join([f"{name}: {stock} in stock" for name, stock in items])
            return jsonify({"response": f"You should consider reordering the following items: {text}"})
        else:
            return jsonify({"response": "All items are sufficiently stocked."})
        
    if "top" in message and "selling" in message:
        cursor.execute("""
            SELECT items.name, SUM(sales.quantity) as total FROM sales
            JOIN items ON sales.item_id = items.id
            GROUP BY items.name
            ORDER BY total DESC
            LIMIT 1""")  
        top_item = cursor.fetchone()
        conn.close()
        if top_item:
            return jsonify({"response": f"The top selling item is {top_item[0]} with {top_item[1]} sold."})
        else:
            return jsonify({"response": "No sales data available."})
        
    if "worst" in message and "selling" in message:
        cursor.execute("""
            SELECT items.name, SUM(sales.quantity) as total FROM sales
            JOIN items ON sales.item_id = items.id
            GROUP By items.name
            ORDER BY total ASC
            LIMIT 1""")    
        worst_item =cursor.fetchone()
        conn.close()
        if worst_item:
            return jsonify({"response": f"The worst selling item is {worst_item[0]} with only {worst_item[1]} sold."})
        else:
            return jsonify({"response": "No sales data available"})
        
    if "today" in message and "sales" in message:
        cursor.execute("""
            SELECT COUNT(*), SUM(cost) FROM sales
            WHERE sale_date = date('now')""")
        count, revenue = cursor.fetchone()
        conn.close()
        revenue = revenue or 0
        return jsonify({"response": f"Today you made {count} sales with £{revenue} revenue."}) 

    if "week" in message and "revenue" in message:
        cursor.execute("""
            SELECT SUM(cost) FROM sales
            WHERE sale_date >= date('now', '-7 days')
        """)  
        revenue = cursor.fetchone()[0] or 0
        conn.close()
        return jsonify({"response": f"This week's revenue is £{revenue}."})
    
    if "pending" in message and "orders" in message:
        cursor.execute("SELECT COUNT(*) FROM purchases WHERE status = 'Pending'")
        count = cursor.fetchone()[0] or 0
        conn.close()
        return jsonify({"response": f"You currently have {count} pending orders."})
    
    if "waste" in message and "today" in message:
        cursor.execute("""
            SELECT SUM(quantity), SUM(cost) FROM waste
            WHERE waste_date = date('now')
        """)
        quantity, cost = cursor.fetchone()
        conn.close()
        quantity = quantity or 0
        cost = cost or 0
        return jsonify({"response": f"Today you wasted {quantity} items costing £{cost}."})

    if "total sales" in message:
        cursor.execute("SELECT SUM(cost) FROM sales")
        total_sales = cursor.fetchone()[0] or 0
        conn.close()
        return jsonify({"response": f"The total sales revenue is £{total_sales}."})   

    if "inventory summary" in message or "summarise inventory" in message:
        cursor.execute("SELECT COUNT(*), SUM(stock) FROM items")
        total_items, total_stock = cursor.fetchone()
        conn.close()
        return jsonify({"response": f"You have {total_items} items with a total stock of {total_stock} units."}) 

    cursor.execute("SELECT name, stock FROM items")
    items = cursor.fetchall()

    cursor.execute("""
        SELECT items.name, SUM(sales.quantity) FROM sales
        JOIN items ON sales.item_id = items.id
        GROUP BY items.name""")
    sales = cursor.fetchall()  
    conn.close()

    inventory_text = "\n".join([f"{name}: {stock} in stock" for name, stock in items])
    sales_text = "\n".join([f"{name}: {quantity} sold" for name, quantity in sales])

    context = f"""Inventory:{inventory_text}
    Sales:{sales_text}"""   

    try:
        response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for a stock management system."
             "You must:"
            "- Answer questions about sales, inventory, and purchases based on the data provided."
            "- Suggest actions when stock is low or sales are high."
            "- Provide insights based on trends in the data."
            "- Do not make up information. Only use the data provided to answer questions."},
            {"role": "user", "content": f"{message}\n\nData:\n{context}"}

        ]    
    )
        reply = response.choices[0].message.content
        return jsonify({"response": reply.strip()})

    except Exception as e:
        return jsonify({"response": "An error occurred while processing your request."})

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    data = request.json

    email = data.get("email")
    password = data.get("password")

    conn=sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"success": True, "role": user[3], "message": "Login successful"})
    else:
        return jsonify({"success": False, "message": "Invalid email or password"})

@app.route("/get_items", methods=["GET"])
def get_items():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM items")
    stocks = cursor.fetchall()
    
    

    items = []
    for stock in stocks:
        item_id=stock[0]

        cursor.execute("""
            SELECT MAX(p.purchase_date)
            FROM purchases p
            JOIN purchase_items pi ON p.id = pi.purchase_id
            WHERE pi.item_id = ?
        """, (item_id,))
        
        last_restock = cursor.fetchone()[0]
        items.append({
            "id": stock[0],
            "name": stock[1],
            "stock": stock[2],
            "Status": get_status(stock[2]),
            "LastRestock": last_restock if last_restock else "Never",
            "price": stock[5]
        })
    conn.close()
    return jsonify(items)

@app.route("/add_item", methods=["POST"])
def add_item():
    data = request.json

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO items (name,stock,Status,LastRestock, price) VALUES (?, ?, ?, ?, ?)", (data["name"], data["stock"], data["Status"], data["LastRestock"], data["price"]))
    conn.commit()
    conn.close()

    return jsonify({"message": "Item added successfully"})

@app.route("/delete_item/<int:id>", methods=["DELETE"])
def delete_item(id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM items WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Item deleted successfully"})

@app.route("/get_sales", methods=["GET"])
def get_sales():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
                SELECT sales.id, items.name, sales.quantity, sales.sale_date, sales.cost
                   FROM sales
                     JOIN items ON sales.item_id = items.id
                """)
    
    rows = cursor.fetchall()
    conn.close()

    sales = []
    for row in rows:
        sales.append({
            "id": row[0],
            "name": row[1],
            "quantity": row[2],
            "sale_date": row[3],
            "cost": row[4]
        })
    return jsonify(sales)

@app.route("/add_sale", methods=["POST"])
def add_sale():
    data = request.json

    if data["quantity"] <= 0:
        return jsonify({"message": "Please enter a quantity greater than 0."}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT stock, price FROM items WHERE id = ?", (data["item_id"],))
    result = cursor.fetchone()

    if result is None:
        return jsonify({"message": "Item not found"}), 400
    
    current_stock = result[0]
    price = result[1] or 0

    if current_stock < data["quantity"]:
        return jsonify({"message": "Not enough stock available"}), 400
    
    total_cost = price *data["quantity"]
    
    cursor.execute("INSERT INTO sales (item_id, quantity, sale_date, cost) VALUES (?, ?, ?, ?)", (data["item_id"], data["quantity"], data["sale_date"], total_cost))

    cursor.execute("""UPDATE items SET stock = stock - ? WHERE id = ?""", (data["quantity"], data["item_id"]))
    conn.commit()
    conn.close()

    return jsonify({"message": "Sale recorded successfully"})

@app.route("/get_purchases", methods=["GET"])
def get_purchases():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            purchases.id, purchases.order_id, purchases.supplier,purchases.description, purchases.purchase_date, purchases.status
                   FROM purchases""")
    rows = cursor.fetchall()
    conn.close()

    purchases = []
    for row in rows:
        purchases.append({
            "id": row[0],
            "order_id": row[1],
            "supplier": row[2],
            "description": row[3],
            "purchase_date": row[4],
            "status": row[5]
        })
    return jsonify(purchases)

@app.route("/get_purchase_items/<int:purchase_id>", methods=["GET"])
def get_purchase_items(purchase_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT items.name,purchase_items.quantity
        FROM purchase_items
        JOIN items ON purchase_items.item_id = items.id
        WHERE purchase_items.purchase_id = ?""", (purchase_id,))
    
    rows = cursor.fetchall()
    conn.close()
    items = []
    for name,quantity in rows:
        items.append({
            "name": name,
            "quantity": quantity
        })
    return jsonify(items)

@app.route("/add_purchase", methods=["POST"])
def add_purchase():
    data = request.json

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO purchases (order_id, supplier, description, purchase_date, status) VALUES (?, ?, ?, ?, ?)", (data["order_id"], data["supplier"], data["description"], data["purchase_date"], data["status"]))

    purchase_id = cursor.lastrowid

    for item in data["items"]:
        cursor.execute("INSERT INTO purchase_items (purchase_id, item_id, quantity) VALUES (?, ?, ?)", (purchase_id, item["item_id"], item["quantity"]))

    conn.commit()
    conn.close()

    return jsonify({"message": "Purchase order added successfully"})

@app.route("/update_purchase_status/<int:id>", methods=["PUT"])
def update_purchase_status(id):
    data = request.json
    
    conn= sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("UPDATE purchases SET status = ? WHERE id = ?", (data["status"], id))

    from datetime import datetime

    if data["status"] == "Delivered":
        cursor.execute("SELECT item_id, quantity FROM purchase_items WHERE purchase_id = ?", (id,))
        items = cursor.fetchall()

        today = datetime.now().strftime("%Y-%m-%d")

        for item_id, quantity in items:
            cursor.execute("UPDATE items SET stock = stock + ?, LastRestock = ? WHERE id = ?", (quantity, today, item_id))


    conn.commit()
    conn.close()

    return jsonify({"message": "Purchase status updated successfully"})

@app.route("/generate_report", methods=["POST"])
def generate_report():
    data = request.json
    report_type = data["report_type"]
    start_date = data["start_date"]
    end_date = data["end_date"]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    result = ""
    if report_type == "sales":
        cursor.execute("""
            SELECT COUNT(*) FROM sales
            WHERE sale_date BETWEEN ? AND ?""", (start_date, end_date))
        total = cursor.fetchone()[0] or 0
        
        cursor.execute("""
             SELECT items.name, SUM(sales.quantity) FROM sales
             JOIN items ON sales.item_id = items.id
             WHERE sale_date BETWEEN ? AND ?
             GROUP BY items.name""", (start_date, end_date))
        item_sales = cursor.fetchall()
        item_text = ", ".join([f"{name} (x{quantity})" for name, quantity in item_sales])           
        result = f"Total Sales: {total}. Items Sold: {item_text}"   

    elif report_type == "purchases":
        cursor.execute("""
            SELECT COUNT(*) FROM purchases
            WHERE purchase_date BETWEEN ? AND ?""", (start_date, end_date))
        total1 = cursor.fetchone()[0] or 0
        
        cursor.execute("""
             SELECT items.name, SUM(purchase_items.quantity) FROM purchase_items
             JOIN purchases ON purchase_items.purchase_id = purchases.id
             JOIN items ON purchase_items.item_id = items.id
             WHERE purchases.purchase_date BETWEEN ? AND ?
             GROUP BY items.name""", (start_date, end_date))
        item_purchases = cursor.fetchall()
        item_text= ", ".join([f"{name} (x{quantity})" for name, quantity in item_purchases])
        result = f"Total Purchases: {total1}. Items Purchased: {item_text}"                                        
           

    elif report_type == "profit":
        cursor.execute("SELECT SUM(cost) FROM sales")
        sales_total = cursor.fetchone()[0] or 0
        profit = sales_total
        result = f"Total Profit: £{profit}"   

    elif report_type == "waste":
        cursor.execute(""" 
            SELECT COUNT(*), SUM(quantity), SUM(cost)
            FROM waste WHERE waste_date BETWEEN ? AND ? """,
            (start_date, end_date))
        total_records,total_quantity,total_cost = cursor.fetchone()
        total_records = total_records or 0
        total_quantity = total_quantity or 0
        total_cost = total_cost or 0

        cursor.execute("""
        SELECT items.name, waste.quantity, waste.cost, waste.reason FROM waste
        JOIN items ON waste.item_id = items.id
        WHERE waste.waste_date BETWEEN ? AND ? """,
        (start_date, end_date))       
        waste_items = cursor.fetchall()  

        item_text=", ".join([f"{name} (x{quantity}, £{cost}, {reason})"
                             for name, quantity, cost, reason in waste_items])   

        result = (
            f"Total Waste Records: {total_records}."
            f"Total Items Wasted: {total_quantity}."
            f"Total Cost: £{total_cost}."
            f"Items: {item_text}"
        )                                     

    cursor.execute("INSERT INTO reports (report_type, start_date, end_date, details, generated_at) VALUES (?, ?, ?, ?, datetime('now'))", (report_type, start_date, end_date, result))
    conn.commit()
    conn.close()

    return jsonify({"message": "Report generated successfully", "report": result})    

@app.route("/get_reports", methods=["GET"])
def get_reports():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT report_type, start_date, end_date, details, generated_at FROM reports")
    rows = cursor.fetchall()
    conn.close()

    reports = []
    for row in rows:
        reports.append({
            "report_type": row[0],
            "range": f"{row[1]} to {row[2]}",
            "details": row[3],
            "generated_at": row[4]         
        })

    return jsonify(reports)

@app.route("/dashboard_data")
def dashboard_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM items")
    total_items = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM items WHERE stock < 5")
    low_stock = cursor.fetchone()[0] or 0

    cursor.execute("SELECT name, stock FROM items WHERE stock < 5")
    low_stock_items = cursor.fetchall()

    cursor.execute("SELECT SUM(stock * price) FROM items")    
    inventory_value = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT COUNT(*), SUM(cost) FROM sales
        WHERE sale_date = date('now')""")
    
    result1 = cursor.fetchone()
    today_sales = result1[0] or 0
    today_revenue = result1[1] or 0

    cursor.execute("""
        SELECT SUM(cost) FROM sales
        WHERE sale_date >= date('now', '-7 days')""")
    week_revenue = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT items.name, SUM(sales.quantity) as total FROM sales
        JOIN items ON sales.item_id = items.id
        GROUP BY items.name
        ORDER BY total DESC
        LIMIT 1""")  

    top_item = cursor.fetchone()
    top_item = top_item[0] if top_item else "N/A"

    cursor.execute("""
        SELECT SUM(p.quantity * i.price) FROM purchase_items p
        JOIN items i ON p.item_id = i.id
    """)
    total_cost = cursor.fetchone()[0] or 0           

    cursor.execute("""
        SELECT items.name, SUM(sales.quantity) as total FROM sales
        JOIN items ON sales.item_id = items.id
        GROUP BY items.name
        ORDER BY total ASC
        LIMIT 1""")
    
    worst_item = cursor.fetchone()
    worst_item = worst_item[0] if worst_item else "N/A"

    cursor.execute("""
        SELECT COUNT(*) FROM purchases WHERE status = 'Pending'""")
    pending_orders = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT COUNT(*) FROM purchases
        WHERE purchase_date >= date('now', '-7 days')""")
    weekly_orders = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT items.name, waste.quantity, waste.cost, waste.reason FROM waste
        JOIN items ON waste.item_id = items.id  
        WHERE waste.waste_date = date('now')""")
    waste_today_items = cursor.fetchall()

    cursor.execute("""
        SELECT SUM(quantity), SUM(cost) FROM waste
        WHERE waste_date = date('now')""")
    waste_today, cost_today = cursor.fetchone()
    waste_today = waste_today or 0
    cost_today = cost_today or 0        

    conn.close()

    return jsonify({
        "total_items": total_items,
        "low_stock": low_stock,
        "inventory_value": inventory_value,
        "today_sales": today_sales,
        "today_revenue": today_revenue,
        "week_revenue": week_revenue,
        "top_item": top_item,
        "worst_item": worst_item,
        "pending_orders": pending_orders,
        "weekly_orders": weekly_orders,
        "total_cost": total_cost,
        "low_stock_items": low_stock_items,
        "waste_today": waste_today,
        "cost_today": cost_today,
        "waste_today_items": waste_today_items
    })          

@app.route("/sales_by_item")
def sales_by_item():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT items.name, SUM(sales.quantity) as total FROM sales
        JOIN items ON sales.item_id = items.id
        GROUP BY items.name""")
    
    rows = cursor.fetchall()
    conn.close()

    labels = [row[0] for row in rows]
    values = [row[1] for row in rows]

    return jsonify({"labels": labels, "values": values})

from datetime import datetime

@app.route("/add_waste",methods=["POST"])
def add_waste():
    data=request.json
    conn=sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    waste_date = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        INSERT INTO waste(item_id, quantity, waste_date, cost, reason)  
        VALUES(?, ?, ?, ?, ?)
        """, (data["item_id"], data["quantity"], waste_date, data["cost"], data["reason"]))
    
    cursor.execute("""
        UPDATE items SET stock = stock - ? WHERE id = ?""",
        (data["quantity"], data["item_id"]))           

    conn.commit()
    conn.close()

    return jsonify({"message": "Waste has been recorded successfully"})                               



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
