import sqlite3

DB = "bank.db"

class DbConnection:
    def __init__(self):
        self.conn = sqlite3.connect(DB)
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bank'")
        result = cursor.fetchone()
        if result is None:
            self.conn.execute('''
                CREATE TABLE bank(
                    Bnkaccno INTEGER PRIMARY KEY AUTOINCREMENT,
                    Passwd VARCHAR(50),
                    Balance DOUBLE
                )
            ''')
            self.conn.execute("""
                INSERT INTO bank (Bnkaccno, Passwd, Balance)
                VALUES (?, ?, ?);
            """, (10000, 'dummy', 0.0))
            self.conn.commit()

    def withdraw(self, accno, amount):
        self.conn.execute('UPDATE bank SET Balance = Balance - ? WHERE Bnkaccno = ?', (amount, accno))
        self.conn.commit()

    def deposit(self, accno, amount):
        self.conn.execute('UPDATE bank SET Balance = Balance + ? WHERE Bnkaccno = ?', (amount, accno))
        self.conn.commit()

    def checkbalance(self, accno):
        data = self.conn.execute('SELECT Balance FROM bank WHERE Bnkaccno = ?', (accno,)).fetchone()
        if data is None:
            print("Incorrect account number")
            return
        print(f"The balance of {accno} is {data[0]}")

    def addaccount(self, balance, password):
        self.conn.execute('INSERT INTO bank (Balance, Passwd) VALUES (?, ?)', (balance, password))
        self.conn.commit()
        cursor = self.conn.execute("SELECT * FROM bank ORDER BY Bnkaccno DESC LIMIT 1")
        last_row = cursor.fetchone()
        print(f"Created bank account with accno {last_row[0]}, password {last_row[1]}, and balance {last_row[2]} \n")

class Bank(DbConnection):
    def __init__(self):
        super().__init__()

    def deposit(self, accno, amount, password):
        data = self.conn.execute('SELECT Balance FROM bank WHERE Bnkaccno = ? AND Passwd = ?', (accno, password)).fetchone()
        if data is None:
            print("Incorrect account number or password")
            return
        super().deposit(accno, amount)
        print(f"Deposited {amount} to Account Number {accno}. Final balance is {data[0] + amount} ")
        print()

    def withdraw(self, accno, amount, password):
        data = self.conn.execute('SELECT Balance FROM bank WHERE Bnkaccno = ? AND Passwd = ?', (accno, password)).fetchone()
        if data is None:
            print("Incorrect account number or password")
            return
        if data[0] < amount:
            print("Insufficient balance")
            return
        super().withdraw(accno, amount)
        print(f"Withdrawn {amount} from Account Number {accno}. Final balance is {data[0] - amount} ")
        print()

    def checkbalance(self, accno, password):
        data = self.conn.execute('SELECT Balance FROM bank WHERE Bnkaccno = ? AND Passwd = ?', (accno, password)).fetchone()
        if data is None:
            print("Incorrect account number or password")
            return
        print(f"The balance of {accno} is {data[0]}")

    def addaccount(self, password, balance=0):
        super().addaccount(balance, password)

# Main program
mybank = Bank()
while True:
    choice = int(input("Enter your choice:\n1. To create new account\n2. Existing Account \n3. To exit \n"))
    if choice == 1:
        password = input("Choose your password: ")
        choice2 = int(input("Enter 0 to make a zero balance account and 1 for creating new account with balance\n"))
        if choice2 == 0:
            mybank.addaccount(password)
        else:
            balance = float(input("Enter your balance: "))
            mybank.addaccount(password, balance)
    elif choice == 2:
        choice1 = int(input("\nEnter your choice: \n1. To deposit \n2. To withdraw \n3. To check balance\n4. To exit\n"))
        if choice1 == 1:
            accno = int(input("\nEnter your accno: "))
            password = input("Enter your password: ")
            amount = float(input("Enter amount to deposit: "))
            mybank.deposit(accno, amount, password)
        elif choice1 == 2:
            accno = int(input("\nEnter your accno: "))
            password = input("Enter your password: ")
            amount = float(input("Enter amount to withdraw: "))
            mybank.withdraw(accno, amount, password)
        elif choice1 == 3:
            accno = int(input("\nEnter your accno: "))
            password = input("Enter your password: ")
            mybank.checkbalance(accno, password)
        elif choice1 == 4:
            exit(0)
        else:
            exit(0)
    