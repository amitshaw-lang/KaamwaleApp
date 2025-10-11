import os, sqlite3

# ---- DB path (yahi folder) ----
BASE_DIR = os.path.dirname(os.path.abspath(_file_))
DB_PATH = os.path.join(BASE_DIR, "rozgarwale.db")

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

# Before: kitne duplicates hai?
print("Checking duplicates BEFORE:")
for row in cur.execute("""
    SELECT name, phone, COUNT(*) c
    FROM workers
    GROUP BY name, phone
    HAVING c > 1
"""):
    print("  DUP:", row)

# 1) Normalize: extra spaces / dashes / country code hatao
cur.execute("UPDATE workers SET name = TRIM(name)")
# phone ko thoda normalize: spaces, dashes, non-breaking space remove
cur.execute("UPDATE workers SET phone = REPLACE(REPLACE(REPLACE(phone, ' ', ''), '-', ''), ' ', '')")
# (Optional) agar +91 prefix bahut entries me hai, toh uncomment:
# cur.execute("UPDATE workers SET phone = SUBSTR(phone, 4) WHERE phone LIKE '+91%'")

# 2) Duplicate removal: same (name, phone) me sirf minimum rowid bache
cur.execute("""
DELETE FROM workers
WHERE rowid NOT IN (
  SELECT MIN(rowid)
  FROM workers
  GROUP BY name, phone
)
""")

con.commit()

print("\nChecking duplicates AFTER:")
dups_left = list(cur.execute("""
    SELECT name, phone, COUNT(*) c
    FROM workers
    GROUP BY name, phone
    HAVING c > 1
"""))
if not dups_left:
    print("  ✔ No duplicates left.")
else:
    for row in dups_left:
        print("  STILL DUP:", row)

con.close()
print("\n✅ Cleanup done.")