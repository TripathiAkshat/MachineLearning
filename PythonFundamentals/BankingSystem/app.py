from flask import Flask, render_template, request
app = Flask(__name__)
import sqlite3
import bcrypt
DB = "bank.db"

def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row  
    return conn

def initialize_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bank'")
    result = cursor.fetchone()
    if result is None:
        conn.execute('''
            CREATE TABLE bank(
                Bnkaccno INTEGER PRIMARY KEY AUTOINCREMENT,
                Passwd BLOB,
                Balance DOUBLE
            )
        ''')
        conn.execute("""
            INSERT INTO bank (Bnkaccno, Passwd, Balance)
            VALUES (?, ?, ?);
        """, (10000, 'dummy', 0.0))
        conn.commit()
    conn.close()

class DbConnection:
    def fetchdata(self, accno):
        conn = get_db_connection()
        data = conn.execute('SELECT Passwd, Balance FROM bank WHERE Bnkaccno = ?', (accno,)).fetchone()
        conn.close()
        return data
        
    def withdraw(self, accno, amount):
        conn = get_db_connection()
        conn.execute('UPDATE bank SET Balance = Balance - ? WHERE Bnkaccno = ?', (amount, accno))
        conn.commit()
        conn.close()

    def deposit(self, accno, amount):
        conn = get_db_connection()
        conn.execute('UPDATE bank SET Balance = Balance + ? WHERE Bnkaccno = ?', (amount, accno))
        conn.commit()
        conn.close()

    def checkbalance(self, accno):
        conn = get_db_connection()
        data = conn.execute('SELECT Balance FROM bank WHERE Bnkaccno = ?', (accno,)).fetchone()
        conn.close()
        return(f"The balance of {accno} is {data[0]}")

    def addaccount(self, balance, password):
        conn = get_db_connection()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        conn.execute('INSERT INTO bank (Balance, Passwd) VALUES (?, ?)', (balance, hashed_password))
        conn.commit()
        cursor = conn.execute("SELECT * FROM bank ORDER BY Bnkaccno DESC LIMIT 1")
        last_row = cursor.fetchone()
        conn.close()
        return(f"Created bank account with accno {last_row[0]}, password {password}, and balance {last_row[2]}, please note your account number and password for further transactions \n")

class Bank(DbConnection):
    def deposit(self, accno, amount, password):
        data = self.fetchdata(accno)
        if data is None:
            return "Incorrect account number"
        
        passwd = data[0]
        if isinstance(passwd, str):
            passwd = passwd.encode('utf-8')
            
        if bcrypt.checkpw(password.encode('utf-8'), passwd):
            super().deposit(accno, amount)
            return str(f"Deposited {amount} to Account Number {accno}. Final balance is {float(data[1]) + float(amount)}")
        else:
            return "Incorrect password"

    def withdraw(self, accno, amount, password):
        data = self.fetchdata(accno)
        if data is None:
            return "Incorrect account number"
            
        passwd = data[0]
        if isinstance(passwd, str):
            passwd = passwd.encode('utf-8')
            
        if bcrypt.checkpw(password.encode('utf-8'), passwd):
            if float(data[1]) < float(amount):
                return "Insufficient balance"
            super().withdraw(accno, amount)
            return f"Withdrawn {amount} from Account Number {accno}. Final balance is {float(data[1]) - float(amount)}"
        else:
            return "Incorrect password"

    def checkbalance(self, accno, password):
        data = self.fetchdata(accno)
        if data is None:
            return "Incorrect account number"
            
        passwd = data[0]
        if isinstance(passwd, str):
            passwd = passwd.encode('utf-8')
            
        if not bcrypt.checkpw(password.encode('utf-8'), passwd):
            return "Incorrect password"
        return super().checkbalance(accno)

    def addaccount(self, password, balance=0):
        return super().addaccount(balance, password)
        
@app.route('/')
def home():
    return render_template('home.html') 

@app.route('/chkbalance',methods=['GET','POST'])
def chkbalance():
    if request.method == 'GET':
        return render_template('checkbalance.html')
    else:
        accno = request.form['accountnumber']
        password = request.form['mpassword']
        ans = bank.checkbalance(accno, password)
        if ans == 'Incorrect account number' :
            return render_template('error.html',message=ans)
        elif ans == 'Incorrect password':
            return render_template('error.html',message=ans) 
        return render_template('success.html',message=ans)

@app.route('/deposit',methods=['GET','POST'])
def deposit():
    if request.method == 'GET':
        return render_template('deposit.html')
    else:
        accno = request.form['accountnumber']
        amount = request.form['amount']
        password = request.form['mpassword']
        result = bank.deposit(accno, amount, password)
        if result == 'Incorrect account number' :
            return render_template('error.html',message=result)
        elif result == 'Incorrect password':
            return render_template('error.html',message=result)     
        return render_template('success.html',message=result)

@app.route('/withdraw', methods=['GET','POST'])
def withdraw():
    if request.method == 'GET':
        return render_template('withdraw.html')
    else:
        accno = request.form['accountnumber']
        amount = request.form['amount']
        password = request.form['mpassword']
        result = bank.withdraw(accno, amount, password)
        if result == 'Incorrect account number' :
            return render_template('error.html',message=result)
        elif result == 'Incorrect password':
            return render_template('error.html',message=result) 
        return render_template('success.html', message=result)
        

@app.route('/createaccount', methods=['GET', 'POST'])
def createaccount():
    if request.method == 'GET':
        return render_template('createaccount.html')
    else:
        password = request.form['mpassword']
        balance = request.form['amount']
        result = bank.addaccount(password, balance)
        return render_template('success.html', message=result)

if __name__ == '__main__':
    initialize_db()  
    bank = Bank()
    app.run(debug=True)
