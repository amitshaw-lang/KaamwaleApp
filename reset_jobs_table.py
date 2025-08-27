import sqlite3

conn = sqlite3.connect("RozgarWale.db")
c = conn.cursor()

# ❌ Ye pura table delete karega (agar already bana hai)
c.execute("DROP TABLE IF EXISTS jobs")

# ✅ Naya table banayenge correct columns ke saath
c.execute('''
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer TEXT,
    description TEXT,
    location TEXT,
    status TEXT,
    worker TEXT,
    price INTEGER,
    timestamp TEXT
)
''')

conn.commit()
conn.close()

print("✅ New 'jobs' table created successfully!")