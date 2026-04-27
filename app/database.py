import sqlite3

connection = sqlite3.connect("sqlite.db")

cursor = connection.cursor()


cursor.execute("""
    CREATE TABLE IF NOT EXISTS shipment (
        id INTEGER PRIMARY KEY,
        content TEXT,
        weight REAL,
        status TEXT
    )
""")

cursor.execute("""
   INSERT INTO shipment
   VALUES (12701, 'basalt', 18.5, 'in_transit')
""")


cursor.execute("""
    UPDATE shipment
    SET status= "placed"
    WHERE id = 12701       
""")

connection.commit()





cursor.execute("""
    SELECT * FROM shipment
    WHERE id = 12702
""")

result = cursor.fetchall()
print(result)


result = cursor.fetchmany(2)
print(result)


result = cursor.fetchone()
print(result)


connection.close()
