import sqlite3
from datetime import datetime

conn = sqlite3.connect("RozgarWale.db")
c = conn.cursor()

c.execute("INSERT INTO jobs (customer, description, location, status, worker, price, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)", 
          ("Ravi Kumar", "Plumber Needed", "Kolkata", "Pending", "Unassigned", 300, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

conn.commit()
conn.close()

print("✅ Dummy job inserted successfully!")