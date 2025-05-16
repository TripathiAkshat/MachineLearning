import sqlite3
DB = "bank.db"

def deposit(accno, amount, password):
    conn = sqlite3.connect(DB)
    data = conn.execute('Select Balance from bank where Bnkaccno is ? and Passwd is ?',(accno,password)).fetchone()
    if data is None:
        print("Incorrect account number or password")
        conn.close()
        return
    conn.execute('Update bank set Balance = Balance + ? where Bnkaccno = ? and Passwd = ?',(amount, accno,password))
    conn.commit()
    print(f"Successfully deposited {amount} to Account Number{accno} final balance: {data[0] + amount}")
    print()
    conn.close()
def withdraw(accno, amount, password):
    conn = sqlite3.connect(DB)
    data = conn.execute('Select Balance from bank where Bnkaccno is ? and Passwd is ?',(accno,password)).fetchone()
    if data is None:
        print("Incorrect account number or password")
        conn.close()
        return
    if data[0] < amount:
        print("Insufficient balance")
        conn.close()
        return
    conn.execute('Update bank Set Balance = Balance - ? where Bnkaccno = ? and Passwd = ?',(amount, accno,password))
    print(f"Successfully withdrawn {amount} from Account Number{accno} final balance: {data[0] - amount}")
    conn.commit()
    conn.close()
    print("")

def checkbalance(accno, password):
    conn = sqlite3.connect(DB)
    data = conn.execute('Select Balance from bank where Bnkaccno is ? and Passwd is ?',(accno,password)).fetchone()
    if data is None:
        print("Incorrect account number or password")
        conn.close()
        return
    print(f"The balance of {accno} is {data[0]}")
    conn.close()

def addacocunt(balance, password):
    conn = sqlite3.connect(DB)
    conn.execute('Insert into bank (Balance,Passwd) values (?,?)',(balance, password))
    conn.commit()
    cursor = conn.execute("SELECT * FROM bank ORDER BY Bnkaccno DESC LIMIT 1")
    last_row = cursor.fetchone()
    print(f"Created bankaccount with accno {last_row[0]} and password {last_row[1]} and balance {last_row[2]}")
    conn.close()



while(True):
    choice = int(input("Enter your choice:\n1. To create new account\n2. Existing Account \n3. To exit "))
    if choice == 1:
        balance = int(input("Enter your balance: "))
        password = input("Choose your password: ")
        addacocunt(balance, password)
    elif choice == 2:
        choice1 = int(input("\nEnter your choice: \n1. To deposit \n2. To withdraw \n3. To check balance\n4.To exit\n"))
        if choice1 == 1:
            accno = int(input("\nEnter your accno: "))
            password = input("Enter your password: ")
            amount = int(input("Enter amount to deposit: "))
            deposit(accno, amount, password)
            print()
        elif choice1 == 2:
            accno = int(input("\nEnter your accno: "))
            password = input("Enter your password: ")
            amount = int(input("Enter amount to withdaw: "))
            withdraw(accno, amount, password)
            print()
        elif choice1 == 3:
            accno = int(input("\nEnter your accno: "))
            password = input("Enter your password: ")
            checkbalance(accno, password)
            print()
        elif choice1 == 4:
            exit(0)
    else:
        exit(0)
