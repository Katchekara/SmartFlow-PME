import sqlite3

conn = sqlite3.connect("smartflow.db")
cursor = conn.cursor()

# Voir les tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables :", cursor.fetchall())

# Voir les crédits
cursor.execute("SELECT * FROM credits;")
print("Crédits :", cursor.fetchall())

conn.close()
