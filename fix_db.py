import sqlite3

conn = sqlite3.connect("RozgarWale.db")
c = conn.cursor()

try:
    c.execute("ALTER TABLE jobs ADD COLUMN timestamp TEXT")
    print("✅ timestamp column added successfully.")
except Exception as e:
    print("⚠️ Error or already added:", e)

conn.commit()
conn.close()