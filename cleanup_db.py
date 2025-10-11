import os
import sqlite3

# Safest way: current working directory se DB path
BASE_DIR = os.getcwd()   # abhi jaha se run karoge wahi folder lega
DB_PATH = os.path.join(BASE_DIR, "rozgarwale.db")

print("DB Path ->", DB_PATH)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# REMOVE DUPLICATES (keep first by name+phone)
c.execute("""
DELETE FROM workers
WHERE rowid NOT IN (
  SELECT MIN(rowid)
  FROM workers
  GROUP BY name, phone
)
""")
conn.commit()
conn.close()

print("✅ Duplicate rows removed successfully!")