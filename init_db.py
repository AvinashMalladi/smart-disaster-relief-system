import sqlite3

conn = sqlite3.connect("database.db")

# REPORTS TABLE
conn.execute("""
CREATE TABLE IF NOT EXISTS reports(
id INTEGER PRIMARY KEY AUTOINCREMENT,
location TEXT,
rainfall REAL,
water_level REAL,
risk TEXT,
latitude REAL,
longitude REAL
)
""")

# CAMPS TABLE
conn.execute("""
CREATE TABLE IF NOT EXISTS camps(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
location TEXT,
capacity INTEGER,
occupied INTEGER,
food INTEGER,
water INTEGER,
latitude REAL,
longitude REAL
)
""")

# VICTIMS TABLE
conn.execute("""
CREATE TABLE IF NOT EXISTS victims(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
age INTEGER,
camp_id INTEGER
)
""")

conn.commit()
conn.close()

print("✅ Database Ready")