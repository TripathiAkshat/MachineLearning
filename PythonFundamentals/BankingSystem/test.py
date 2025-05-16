import sqlite3
conn = sqlite3.connect('bank.db')
conn.execute('''
    Create table bank(
    Bnkaccno INTEGER PRIMARY KEY AUTOINCREMENT,
    Passwd Varchar(50),
    Balance DOUBLE
    )
''')
conn.execute("""
INSERT INTO bank (Bnkaccno, Passwd, Balance)
VALUES (?, ?, ?);
""", (10000, 'dummy', 0.0))

conn.commit()
# Step 3: Delete dummy row

# ins = '''
#     insert into mytable Values(10001, "abcd", 500, "Akshat")
#     '''
# conn.execute(ins)
# conn.commit()
# data = conn.execute('select * from mytable')
# for row in data:
#     print(row[0])
conn.close()