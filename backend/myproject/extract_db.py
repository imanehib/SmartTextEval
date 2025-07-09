import sqlite3
import json

conn = sqlite3.connect('/home/nbl/SmartTextEval/backend/myproject/db.sqlite3')
cursor = conn.cursor()

# Replace 'your_table' with the table you want to export
cursor.execute("SELECT * FROM text_analysis_typingevent")
columns = [description[0] for description in cursor.description]
rows = cursor.fetchall()

data = [dict(zip(columns, row)) for row in rows]

with open('output.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

conn.close()
