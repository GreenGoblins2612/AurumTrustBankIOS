#NOTE: USE COURIER NEW AS FONT
#Importing libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as pl
import math
import sqlite3
from datetime import datetime, timedelta
import sys

#Connector for mysql
con=sqlite3.connect(database='Aurum_Trust_Bank')
cur=con.cursor()

#TABLES SETUP
cur.execute("""
CREATE TABLE IF NOT EXISTS Active_loans (
    Accno CHAR(10) NOT NULL,
    Debt_left DOUBLE DEFAULT NULL,
    Loan_Applied_Date DATE DEFAULT (CURRENT_DATE)
)
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS customers (
    Accno CHAR(10) NOT NULL PRIMARY KEY,
    First_name VARCHAR(100) DEFAULT NULL,
    Last_name VARCHAR(100) DEFAULT NULL,
    Ph_no CHAR(10) UNIQUE DEFAULT NULL,
    Adh_no CHAR(12) UNIQUE DEFAULT NULL,
    Acc_Creation_Date DATE DEFAULT (CURRENT_DATE),
    Address VARCHAR(100) DEFAULT NULL,
    Branch VARCHAR(50) DEFAULT NULL,
    Acc_Password VARCHAR(20) DEFAULT NULL,
    pin INT DEFAULT NULL,
    Balance DOUBLE DEFAULT 0,
    Recovery_Question VARCHAR(35) DEFAULT NULL,
    Recovery_Answer VARCHAR(100) DEFAULT NULL,
    Freeze_Status INT DEFAULT 0,
    Delete_Status INT DEFAULT 0
)
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    Accno CHAR(10) DEFAULT NULL,
    Money DOUBLE DEFAULT NULL,
    Type_TXN VARCHAR(50) DEFAULT NULL,
    TXN_Date_Time DATETIME DEFAULT CURRENT_TIMESTAMP,
    Final_Bal DOUBLE DEFAULT NULL
)
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS virtual_gold_customer (
    accno CHAR(10) NOT NULL PRIMARY KEY,
    Amount_24 DOUBLE DEFAULT NULL,
    Amount_18 DOUBLE DEFAULT NULL
)
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS virtual_gold_price (
    Price_18 DOUBLE DEFAULT NULL,
    Price_24 DOUBLE DEFAULT NULL,
    Date_Time DATETIME DEFAULT NULL
)
""")
con.commit()

#Steps for entering in admin mode:
"""
1) In ' what would you like to: ' write '2'
2) Write the account number as 'admin'
3) Enter the admin password which is 'aurum_trust_bank'
4) Enjoy admin mode!
"""

#FOR PRICE VARIATION OF VIRTUAL GOLD!
cur.execute("select Date_Time from virtual_gold_price")
rows=cur.fetchall()
Virtual_gold=pd.Series(rows)

if Virtual_gold.empty == True:
    initial_value_18 = 11600
    initial_value_24 = 15600
    cur.execute("insert into virtual_gold_price values(?,?,datetime('now', 'localtime'))",(initial_value_18,initial_value_24))
    con.commit()
elif Virtual_gold.empty == False:
    
    cur.execute("select datetime('now', 'localtime')") # system time
    row=cur.fetchone()    
    Date_stored=Virtual_gold[len(Virtual_gold)-1]        #last updated date

    current_time = datetime.fromisoformat(row[0])
    stored_time = datetime.fromisoformat(Date_stored[0])
    time_diff = current_time - stored_time

    cur.execute("select Price_24 from virtual_gold_price;")
    row_24=cur.fetchall()[-1][0]        #rows_24 is an int
    cur.execute("select Price_18 from virtual_gold_price;")
    row_18=cur.fetchall()[-1][0]
    
    days = time_diff.days
    if days > 0:
        new_date = stored_time
        
        for i in range(days):                             #random gold price generator!
            x = np.random.randint(1,11)
            if x <= 8:
                value_24k = row_24 + np.random.randint(1000,2001)
                value_18k = row_18 + np.random.randint(500,1501)
            else:
                value_24k = row_24 - np.random.randint(1000,2001)
                value_18k = row_18 - np.random.randint(500,1501)
                
            new_date = new_date + timedelta(days=1)
            cur.execute("insert into virtual_gold_price values (?,?,?);",(value_18k,value_24k,new_date.strftime("%Y-%m-%d %H:%M:%S")))
            con.commit()
            row_24 = value_24k
            row_18 = value_18k
            

#ADMIN acc login info
admin_pass="aurum_trust_bank"
admin_login=False

#Login system
print("Hello User!")
print("Welcome to Aurum Trust Bank!")
print("Where your money is Safe, Secure & Solid as Gold")
print("The bank with endless golden opportunities.")
print()
login_factor=False    #variable for login status
tmp_loop=True
while tmp_loop:
    print("+"+"-"*21+"+")
    print("| Would you like to:  |")
    print("+"+"-"*21+"+")
    print("| 1) Sign up.         |")
    print("| 2) Log in           |")
    print("| 3) Account Recovery |")
    print("+"+"-"*21+"+")
    ch_for_sign=int(input("Enter choice here: "))
    if ch_for_sign==1:
        print("You have choosen to make a new account.")
        print()
        print("Please enter the following details: ")
        tmp_fname=input("Enter your first name: ").lower()
        tmp_fname=tmp_fname[0:1].upper() + tmp_fname[1:] #to capitalize the first letter
        tmp_lname=input("Enter your last name: ").lower()
        tmp_lname=tmp_lname[0:1].upper() + tmp_lname[1:] # capitalization of first letter
        cur.execute("select Ph_no from customers;")
        tmp_ph=cur.fetchall()
        while True:
            tmp_phno=input("Enter your phone number: ")
            if len(tmp_phno)!=10:
                print("Phone number must be 10 digits!")
            elif (tmp_phno,) in tmp_ph:
                print("This is not your phone number!\nIt already exists!")
            else:
                break
        cur.execute("select Adh_no from customers;")
        tmp_adh=cur.fetchall()
        while True:
            tmp_adhno=input("Enter your aadhaar number: ")
            if len(tmp_adhno)!=12:
                print("Aadhaar number should be 12!")
            elif (tmp_adhno,) in tmp_adh:
                print("This is not your Aadhaar number!\nIt already exists!")
            else:
                 break
        while True:
            tmp_address=input("Enter your address: ")
            if len(tmp_address) >100:
                print("Address too long!")
            elif len(tmp_address) <1:
                print("You have not entered the address please enter it!")
            else:
                break
        print("Here are the branches \n1)Pune City Branch\n2)Golden Square Branch\n3)Crown District Branch")
        while True:                                  #user choosing real branch
            tmp_branch=input("Enter your branch: ").lower()
            if tmp_branch not in ['pune city branch','golden square branch','crown district branch']:
                print("Branch not in list! Please input correct spelling")
            else:
                break

        while True:
            print("+"+"-"*34+"+")
            print("| Set your Safety Question         |")
            print("+"+"-"*34+"+")
            print("| 1) Name of your favourite pet?   |")
            print("| 2) Where were you born?          |")
            print("| 3) Name of your favourite movie? |")
            print("| 4) Who is your childhood hero?   |")
            print("| 5) What your favourite food?     |")
            print("+"+"-"*34+"+")
            tmp_rec_ques=int(input("Enter choice here: "))
            if tmp_rec_ques > 5 or tmp_rec_ques< 1:
                print("Entered question does not exist, retry!")
                continue
            print()
            tmp_list_ques=["Name of your favourite pet?","Where were you born?","Name of your favourite movie?","Who is your childhood hero?","What your favourite food?"]
            print(tmp_list_ques[tmp_rec_ques-1])
            tmp_rec_ans=input("Enter the answer: ").lower()
            break
        while True:                                     #adding the password checker
            tmp_accpass1=input("Create your password (8-20 character long): ")
            tmp_accpass2=input("Renter your password: ")
            print()
            if tmp_accpass1 == tmp_accpass2 and len(tmp_accpass1)>=8 and len(tmp_accpass1)<=20:#if cond not met gives false so loop loops
                
                #accno generation
                cur.execute('Select Accno from customers order by Accno DESC;')
                row_accno=cur.fetchone()
                                            #checking if customer table is emty
                if row_accno != None:           #There exists other accounts
                    row_accno_str=row_accno[0]          #changing to string
                    tmp_accno=int(row_accno_str[2:])+1 #removing AU prefix + remove 0s
                    tmp_accno=str(tmp_accno)          #converted to string for concatination
                    tmp_0 = 8-len(tmp_accno)          #no. of zeros to be added in accno

                    new_accno= 'AU' + '0'*tmp_0 + str(tmp_accno)
                    print("Your account number is:",new_accno)
                
                else:                           #There is no other accounts
                    new_accno='AU00000001'
                    print("Your ACCOUNT NUMBER IS:",new_accno)
                    print()
                    accno = new_accno
                #creation of pin after creation of accno
                while True:
                    tmp_pin=int(input("Create a four digit PIN for your account: "))
                    if len(str(tmp_pin)) != 4:
                        print("Pin must be 4 digits!")
                    else:
                        break

                        #put data in sql
                cur.execute("insert into customers(Accno,First_name,Last_name,Ph_no,adh_no,address,Branch,Acc_password,pin,Recovery_Question,Recovery_Answer) values(?,?,?,?,?,?,?,?,?,?,?)",
                            (new_accno,tmp_fname,tmp_lname,tmp_phno,tmp_adhno,tmp_address,tmp_branch,tmp_accpass1,tmp_pin,tmp_list_ques[tmp_rec_ques-1],tmp_rec_ans)
                                )
                con.commit()
                print()
                print('Account Created,',tmp_fname)
                accno=new_accno     #assigning new_accno (temp variable) to accno (permanent variable)
                login_factor=True   #user's account created and user logged in
                break               #account has been created! & the user is logged in

            else:               # condition if the creation of password goes wrong , i.e., passwords do not match, or lenght not correct
                print("Passwords do not match or doesn't fall in range!")
                print("Try again!")
                print()
        break
    elif ch_for_sign==2:
        print()
        print("You have choosen to log into your account!")
        
        cur.execute("Select accno from customers;")
        tmp_accs=cur.fetchall()
        accs_list=[]  
        for i in range(len(tmp_accs)):          #getting all accounts in list
            accs_list.append(tmp_accs[i][0])
        if accs_list :
            cur.execute("select accno, acc_password from customers;")       #getting all account passwords
            tmp_acc_pass=cur.fetchall()
            acc_pass_list=[]
            for i in range(len(tmp_acc_pass)):
                acc_pass_list.append(tmp_acc_pass[i])

            pass_loop = True
            while pass_loop:
                acc_user=input("Enter your account number: ").upper()
                
                if acc_user == "ADMIN":     #admin checker
                    admin_login = True
                    tmp_loop = False
                    break
                
                elif acc_user in accs_list:     #normal people checker
                    k=0
                    while k<3:
                        tmp_user_pass = input("Enter your account password: ")
                        user_data = (acc_user,tmp_user_pass)

                        if user_data in acc_pass_list:      #user logged in because credentials are right
                            login_factor = True
                            tmp_loop = False
                            accno=acc_user
                            break
                        
                        elif user_data not in acc_pass_list:    #password incorrect counter
                            k = k + 1
                            print("Incorrect Password!")
                            
                        if k == 3:          # 3 attempts done so session termed, check last line
                            login_factor=False
                            tmp_loop=False
                            pass_loop = False
                            break
                        
                if login_factor:
                    #user has logged in so we break loop
                    break
            
        else:
            print("No accounts exist!")
            
    elif ch_for_sign == 3:  #Account recovery option!
        print("+"+"-"*33+"+")
        print("| What would you like to recover? |")
        print("+"+"-"*33+"+")
        print("| 1) Account Number               |")
        print("| 2) Password                     |")
        print("+"+"-"*33+"+")
        ch_for_rec=int(input("Enter you choice here: "))
        if ch_for_rec==1:
            print("Contact admin!")
        elif ch_for_rec==2:
            accno=input("Enter Account Number: ").upper()
            cur.execute("select Recovery_Question, Recovery_Answer,Delete_Status from customers where Accno=?;",(accno,))
            rows=cur.fetchall()
            column_names=[]
            for i in cur.description:
                column_names.append(i[0])
            Rec_info=pd.DataFrame(data=rows,columns=column_names)
            if len(Rec_info) != 0 and Rec_info['Delete_Status'][0]==0:
                print()
                print(Rec_info['Recovery_Question'][0])
                rec_answer=input("Enter your answer: ").lower()
                if Rec_info['Recovery_Answer'][0] == rec_answer:
                    print("Correctly answered!")
                    while True:
                        rec_pass=input("Enter new password(8-20): ")
                        rec_pass_2=input("Re-enter your password: ")
                        if len(rec_pass)>=8 and len(rec_pass) <21 and rec_pass==rec_pass_2:
                            cur.execute("update customers set Acc_Password=? where Accno=?;",(rec_pass,accno))
                            con.commit()
                            print()
                            print("Successfuly changed password!")
                            print("Please sign in now!")
                            break
                        else:
                            print("Password instructions not followed, retry!")
                            print()
            else:
                print("Incorrect Account number / Account number does not exist! ")

    else:
       print("Invalid option!")
       print("Please put a valid input")
       print()


#main action stuff
tmp_loop=False
if login_factor:        #checking if user logged in!
    while True:
        print()
        #for Name
        cur.execute("Select First_name from customers where Accno=?",(accno,))
        tmp_fname=cur.fetchone()[0]
        #adding time checking
        cur.execute("Select time('now', 'localtime')")
        time=str(cur.fetchone()[0])
        if(':' in time[0:2]):
            time='0'+time[0]
        print("="*22+"AURUM TRUST BANK"+"="*30)
        print()
        if int(time[0:2]) < 12 and int(time[0:2]) >=0:
            print("Good Morning,",tmp_fname+"!")
        elif int(time[0:2])>= 12 and int(time[0:2]) <=15:
            print("Good Afternoon,",tmp_fname+"!")
        else:
            print("Good Evening,",tmp_fname+"!")

        #Getting if account is frozen
        cur.execute("Select Freeze_Status from customers where Accno=?",(accno,))
        Freeze_status=cur.fetchone()[0]
        if Freeze_status==0:
            Freeze_factor=False     #Account not frozen
        else:
            Freeze_factor=True      #Acount Frozen

        print()
        print("+"+"-"*61+"+")
        print("| What would you like to perform today:                       |")
        print("+"+"-"*28+"+"+"-"*32+"+")
        print("| 1) Deposit                 | 2)  Withdrawal                 |")
        print("| 3) Transfer                | 4)  See Transaction History    |")
        print("| 5) Financial Calculators   | 6)  View Other Account Holders |")
        print("| 7) Instant Loans           | 8)  Delete Account             |")
        print("| 9) Virtual Gold Investment | 10) Check Balance              |")
        print("| 11) Account Profile Page   | 12) Freeze/Unfreeze Account    |")
        print("+"+"-"*28+"+"+"-"*32+"+")
        print("|                       13) LOGOUT                            |")
        print("+"+"-"*61+"+")
        ch_for_process=int(input("Enter choice here: "))
        print()
        #Deposit Code Block
        if ch_for_process==1:
            if not Freeze_factor:       #Account not frozen
                Transaction_Online=True
                Transaction_Status="Unknown"
                while(Transaction_Online):
                    
                    cur.execute("select * from customers where accno=?",(accno,))
                    rows=cur.fetchall()
                    column_names=[]
                    for i in cur.description:
                        column_names.append(i[0])
                    Acc_Info=pd.DataFrame(data=rows,columns=column_names)

                    while True:
                        deposit_amount_input=float(input("Enter amount to deposit in your account:"))
                        if(deposit_amount_input<=0):
                            print("Amount cannot be negative or zero.\nRetry\n")
                        else:
                            break
                    while True:
                        pin_input=int(input("Enter your 4 digit secret PIN:"))
                        if(pin_input>=10000):
                            print("Entered PIN is more than 4 digits.\nRetry\n")
                        elif(pin_input<1000):
                            print("Entered PIN is less than 4 digits.\nRetry\n")
                        else:
                            break
                    if(pin_input!=Acc_Info["pin"][0]):
                        print("Transaction Declined - Incorrect PIN")
                        Transaction_Status="Failed"
                        Transaction_Online=False
                        break

                    Final_Balance=Acc_Info['Balance'][0]+deposit_amount_input
                    cur.execute("update customers set balance=? where accno=?;",(Final_Balance,accno))
                    con.commit()
                    Transaction_Status="Success"
                    Transaction_Online=False
                    cur.execute("insert into transactions(Accno,Money,Type_TXN,Final_Bal) values(?,?,'Deposit',?)",(accno,deposit_amount_input,Final_Balance))
                    con.commit()
                    print()
                    print("Initial Balance --> Final Balance")
                    print("₹"+str(Acc_Info['Balance'][0])+" --> "+"₹"+str(Final_Balance))
                    print()
                    print("Transaction Successful")
        
            else:
                print("Account is frozen, cannot deposit cash!")
        #Withdraw Code Block
        elif ch_for_process==2:
            if not Freeze_factor:       #Account not frozen
                Transaction_Online=True
                Transaction_Status="Unknown"
                while(Transaction_Online):
                    cur.execute("select * from customers where accno=?",(accno,))
                    rows=cur.fetchall()
                    column_names=[]
                    for i in cur.description:
                        column_names.append(i[0])
                    Acc_Info=pd.DataFrame(data=rows,columns=column_names)

                    while True:
                        withdraw_amount_input=float(input("Enter amount to withdraw from your account:"))
                        if(withdraw_amount_input<=0):
                                print("Amount cannot be negative or zero.\nRetry\n")
                        else:
                            break
                    while True:
                        pin_input=int(input("Enter your 4 digit secret PIN:"))
                        if(pin_input>=10000):
                            print("Entered PIN is more than 4 digits.\nRetry\n")
                        elif(pin_input<1000):
                            print("Entered PIN is less than 4 digits.\nRetry\n")
                        else:
                            break
                    if(pin_input!=Acc_Info["pin"][0]):
                        print("Transaction Declined - Incorrect PIN")
                        Transaction_Status="Failed"
                        Transaction_Online=False
                        break
                    if(withdraw_amount_input>Acc_Info["Balance"][0]):
                        print("Transaction Declined - Insufficient Balance")
                        Transaction_Status="Failed"
                        Transaction_Online=False
                        break
                    
                    Final_Balance=Acc_Info['Balance'][0]-withdraw_amount_input
                    cur.execute("update customers set balance=? where accno=?;",(Final_Balance,accno))
                    con.commit()
                    Transaction_Status="Success"
                    Transaction_Online=False
                    cur.execute("insert into transactions(Accno,Money,Type_TXN,Final_Bal) values(?,?,'Withdraw',?)",(accno,withdraw_amount_input,Final_Balance))
                    con.commit()
                    print()
                    print("Initial Balance --> Final Balance")
                    print("₹"+str(Acc_Info['Balance'][0])+" --> "+"₹"+str(Final_Balance))
                    print()
                    print("Transaction Successful")
            else:
                print("Account is frozen, cannot withdrawal cash!")
            
        #Transfer codE Bloack
        elif ch_for_process==3:
            cur.execute("Select accno from customers;")
            tmp_accs=cur.fetchall()
            accs_list=[] 
            for i in range(len(tmp_accs)):          #getting all accounts in list
                accs_list.append(tmp_accs[i][0])
            if len(accs_list) > 1:
                Transaction_Online=True
                Transaction_Status="Unknown"
                if not Freeze_factor:
                    while(Transaction_Online):
                        
                        cur.execute("select Accno from customers;")
                        AC_Numbers=cur.fetchall()
                        
                        while(True):
                            reciever_accno=input("Enter 10 letter account number of reciever (AUXXXXXXXX)(or Exit to cancel):").upper()
                            if reciever_accno == accno:
                                print("Entered account number is your own account number, not possible!")
                            elif reciever_accno == 'EXIT':
                                print("Exiting transaction mode...")
                                Transaction_Online = False
                                break
                            else:
                                if(len(reciever_accno)>10):
                                    print("Entered account number is more than 10 letters.\nRetry\n")
                                elif(len(reciever_accno)<10):
                                    print("Entered account number is less than 10 letters.\nRetry\n")
                                else:
                                    if((reciever_accno,) in AC_Numbers):

                                        cur.execute("Select Delete_Status from customers where accno=?;",(reciever_accno,))
                                        Delete_status= cur.fetchone()[0]
                                        if Delete_status == 1:
                                            print("Cannot send funds to deleted account!\nRetry!")
                                        else:
                                            break
                                    else:
                                        print("Entered account number does not exist.\nRetry\n")
                        
                        if not Transaction_Online:          #this is when the user exits!
                            break
                        else:                   #transaction is online, i.e., user did not exit!
                            cur.execute("select * from customers where accno=?",(accno,))
                            rows=cur.fetchall()
                            column_names=[]
                            for i in cur.description:
                                column_names.append(i[0])
                            Acc_Info=pd.DataFrame(data=rows,columns=column_names)
                            
                            cur.execute("select * from customers where accno=?",(reciever_accno,))
                            rows=cur.fetchall()
                            column_names=[]
                            for i in cur.description:
                                column_names.append(i[0])
                            Reciever_Acc_Info=pd.DataFrame(data=rows,columns=column_names)
                            
                            #Deposit Section

                            tmp1="Enter amount to transfer to "+reciever_accno+":"
                            while True:
                                transfer_amount_input=float(input(tmp1))
                                if(transfer_amount_input<=0):
                                    print("Amount cannot be negative or zero.\nRetry\n")
                                else:
                                    break
                            while True:
                                pin_input=int(input("Enter your 4 digit secret PIN:"))
                                if(pin_input>=10000):
                                    print("Entered PIN is more than 4 digits.\nRetry\n")
                                elif(pin_input<1000):
                                    print("Entered PIN is less than 4 digits.\nRetry\n")
                                else:
                                    break
                            if(pin_input!=Acc_Info["pin"][0]):
                                print("Transaction Declined - Incorrect PIN")
                                Transaction_Status="Failed"
                                Transaction_Online=False
                                break
                            if(transfer_amount_input>Acc_Info["Balance"][0]):
                                print("Transaction Declined - Insufficient Balance")
                                Transaction_Status="Failed"
                                Transaction_Online=False
                                break
                            
                            Final_Balance=Reciever_Acc_Info['Balance'][0]+transfer_amount_input
                            cur.execute("update customers set balance=? where accno=?;",(Final_Balance,reciever_accno))
                            cur.execute("insert into transactions(Accno,Money,Type_TXN,Final_Bal) values(?,?,'Deposit',?)",(reciever_accno,transfer_amount_input,Final_Balance))
                            
                        #Withdraw Section
                        
                            Final_Balance=Acc_Info['Balance'][0]-transfer_amount_input
                            cur.execute("update customers set balance=? where accno=?;",(Final_Balance,accno))
                            con.commit()
                            Transaction_Status="Success"
                            Transaction_Online=False
                            cur.execute("insert into transactions(Accno,Money,Type_TXN,Final_Bal) values(?,?,'Withdraw',?)",(accno,transfer_amount_input,Final_Balance))
                            con.commit()
                            print()
                            print("Initial Balance --> Final Balance")
                            print("₹"+str(Acc_Info['Balance'][0])+" --> "+"₹"+str(Final_Balance))
                            print()
                            print("Transaction Successful")
                else:
                    print("Account is frozen, cannot transfer cash!")
            else:
                print("There exist only 1 account, Transfer not possible!")

        #TXN History
        elif ch_for_process==4:

            
            cur.execute("select * from transactions where accno=? order by TXN_Date_Time desc;",(accno,))
            rows=cur.fetchall()
            column_names=[]
            for i in cur.description:
                column_names.append(i[0])
            TXN_History_Table=pd.DataFrame(data=rows,columns=column_names,index=range(1,len(rows)+1))

            print("+"+"-"*46+"+")
            print("| Enter the Number of Transactions to be Seen: |")
            print("| 1) ALL                                       |")
            print("| 2) Specific number of transactions           |")
            print("+"+"-"*46+"+")
            tmp_cols=int(input("Enter choice here: "))
            if tmp_cols==1:
                print("You have choosen to see all transactions!")
                tmp_n=len(rows)
            elif tmp_cols==2:
                tmp_n=int(input("Enter number of transactions: "))
                TXN_History_Table=TXN_History_Table.head(tmp_n)            #newest to oldest
            print("Your Transaction History:")
            print(TXN_History_Table)
            print()

            #Graph stuff of past transactions
            
            TXN_hist_list=[]        #gathering data for bar graph
            type_TXN=[]
            money_TXN=[]
            for i in range(0,len(TXN_History_Table)):
                
                type_TXN.append( TXN_History_Table['Type_TXN'].iloc[i] )  #we use .iloc[i] for taking the row with index value i(positional index)
                money_TXN.append( TXN_History_Table['Money'].iloc[i] )    #same here ^^^
                TXN_hist_list.extend([type_TXN + money_TXN])  #combining type and money in 1 list (list of list)
                type_TXN=[]
                money_TXN=[]
                
            total_withdrawal=0          #calculating total withdrawal, deposit, loan taken, loan payed
            total_deposit=0
            total_loan_taken=0
            total_loan_payed=0
            for i in TXN_hist_list:
                if i[0]=='Withdraw':
                    total_withdrawal=total_withdrawal+i[1]
                elif i[0]=='Deposit':
                    total_deposit=total_deposit+i[1]
                elif i[0]=='Loan_added':
                    total_loan_taken=total_loan_taken + i[1]
                else:
                    total_loan_payed = total_loan_payed + i[1]
            
            while True:
                #"Do you want to\n1)See bar graph of past transactions\n2)See line chart of past transactions\n3)Download csv file\n4)Do other action\nEnter choice: "))
                print("+"+"-"*40+"+")
                print("| Do you want to:                        |")
                print("+"+"-"*40+"+")
                print("| 1) See bar graph of past transactions  |")
                print("| 2) See line chart of past transactions |")
                print("| 3) Download csv file                   |")
                print("| 4) Do other action                     |")
                print("+"+"-"*40+"+")
                ch_for_graph=int(input("Enter choice here: "))
                if ch_for_graph==1:
                    print()
                    print("You want to see bar graph of past transactions!")
                    print()
                    print("Total withdrawal amount:",total_withdrawal)
                    print("Total deposit amount:",total_deposit)
                    print("Total loan taken:",total_loan_taken)
                    print("Total loan payed:",total_loan_payed)
                    print()

                # Bar graph codce
                    pl.bar(["Withdrawal","Deposit","Loan Taken","Loan payed"],[total_withdrawal,total_deposit,total_loan_taken,total_loan_payed],color=['orange','green','red','navy'])
                    pl.title("Bar graph for past transactions")
                    pl.ylabel("Money")
                    pl.show()
                    print("Here is the graph!")
                    print()
                    
                elif ch_for_graph==2:
                    print()
                    print("You have choosen Line chart")
                    print()
                    bal_graph_list=[]
                    for i in range(0,len(TXN_History_Table)):           #values for balance
                        bal_graph_list.append(TXN_History_Table['Final_Bal'].iloc[i])
                        date_bal=[]
                    for i in range(0,len(TXN_History_Table)):
                        tmp_date_time=TXN_History_Table['TXN_Date_Time'].iloc[i]
                        date_bal.append(tmp_date_time)

                    #line chart code
                    pl.plot(date_bal,bal_graph_list,color='#894585',marker='*') #'#894585' = baigun colour
                    pl.title("Account Balance Trend Over Time")
                    pl.xlabel("Date and time of Transaction")
                    pl.ylabel("Balance (₹)")
                    pl.grid()
                    pl.show()
                    print("Here is the graph!")
                    print()
                elif ch_for_graph==3:
                    print("You have choosen to download your TXN history!")
                    TXN_History_Table.to_csv("Transaction history of "+str(accno)+".csv",index=False)
                    print("Your history has been downloaded!")
                    print("(Note: it is downloaded where this python file is downloaded!)")
                else:
                    break
        #FD Calculator (Fixed Deposit)
        elif ch_for_process==5:
            #"Which calculator would like to use?\n1)FD (Fixed Deposit) calculator\n2)RD (Recurring Deposit) calculator\nEnter choice here: "))
            print("+"+"-"*38+"+")
            print("| Which calculator would like to use?  |")
            print("+"+"-"*38+"+")
            print("| 1) FD (Fixed Deposit) calculator     |")
            print("| 2) RD (Recurring Deposit) calculator |")
            print("+"+"-"*38+"+")
            tmp_for_calc=int(input("Enter your choice here: "))
            print()
            if tmp_for_calc==1:
                print("You have choosen calculation of FD!")
                print()
                Deposit_Amount=float(input("Enter Amount to be deposited:"))
                Rate_of_Interest=float(input("Enter Rate of Interest per annum:"))
                Compounding_Frequency=4 #quarterly it will compound
                Time=float(input("Enter the tenure in years:"))
                Maturity_Value_Quaterly=[]
                for i in range(0,int(Time*12)+1,3):
                    Maturity_Value_Quaterly.append(Deposit_Amount*math.pow(1+Rate_of_Interest/(100*Compounding_Frequency),Compounding_Frequency*(i/12)))

                Final_Maturity_Value=math.ceil(Maturity_Value_Quaterly[-1])
                print("Final Maturity Value is :",Final_Maturity_Value)
                tmp3=np.arange(0,int(Time*12)+1,3)
                pl.plot(tmp3,Maturity_Value_Quaterly,marker='o',mfc='r')
                pl.xlabel("Months")
                pl.ylabel("Amount")
                pl.title("Fixed Deposit Growth (Every 3 Months)")
                pl.grid(True)
                pl.show()
                
            elif tmp_for_calc==2:          #RD (recurring deposit) section
                print("You have choosen calculation of RD!")
                mat_amt=0 #Maturity amount
                p=int(input("Enter monthly Deposit: "))     #Monthly deposit
                r=float(input("Enter annual interest(in %): "))
                annual_interest=r/100           #Annual interest needed in float
                time=int(input("Enter time in years: "))
                total_time=time*12
                months_ka_list=[]
                rd_ka_list=[]
                balance_ut=0
                for i in range(1,1 + total_time):
                    balance_ut = p + balance_ut                       #principle amount + monthly balance
                    balance_ut = balance_ut*(1 + annual_interest/12)  #new monthly balance = monthly balance x interest
                    months_ka_list.append(i)                          #x-axis stuff
                    rd_ka_list.append(balance_ut)                     #y-axis stuff
                print('Your Maturity Amount is:',math.ceil(balance_ut))
                print()
                
                pl.plot(months_ka_list , rd_ka_list,c='gold',marker='o')    #RD graph section
                pl.title('RD GRAPH')
                pl.xlabel('MONTHS')
                pl.ylabel('RD VALUES')
                pl.grid()
                pl.show()
                
            else:
                print("Wrong input!")
                
        elif ch_for_process==6:
            print("You have choosen to see our other account holders.")
            print()
            cur.execute("Select Accno, First_name, Last_name from customers where Delete_Status = 0")
            tmp_accno_holders=cur.fetchall() #all the rows present
            column_names=[]
            for i in cur.description:         #using description because it runs desc <table_name> in sql for column names
                column_names.append(i[0])
            account_holders=pd.DataFrame(data=tmp_accno_holders,columns=column_names,index=range(1,len(tmp_accno_holders)+1,1))
            print("Here are other account holders:")
            print(account_holders)
            
        elif ch_for_process==7:
            if not Freeze_factor:
                print()
                print("You have choosen Instant loans!")
                print("+"+"-"*31+"+")
                print("| What would you like to choose |")
                print("+"+"-"*31+"+")
                print("| 1) Take instant loans         |")
                print("| 2) Check debt                 |")
                print("| 3) Do other action            |")
                print("+"+"-"*31+"+")
                ch_for_loan=int(input("Enter your choice here: "))
                cur.execute("select pin from customers where Accno=(?);",(accno,))
                pin=cur.fetchone()
                cur.execute("Select Balance from customers where Accno=(?);",(accno,))
                init_bal=cur.fetchone()
                final_bal=0
                if ch_for_loan==1:
                    print()
                    print("Choosen for instant loan!")
                    loan_loop=True

                    #checking if user already has loan!
                    cur.execute("Select Accno from Active_loans where Accno=?",(accno,))   #whether we get value or we dont
                    accnos_loan=cur.fetchone()
                    if accnos_loan:     #if we get account user, accnos_loan != empty so cannot get one more loan
                        loan_loop=False
                        print()
                        print("You already have a loan! Please pay that before taking new loans!")
                    else:               #account_loan = None which is false ,user doesnt have loan ---> loan allowed
                        loan_loop=True
                    
                    while loan_loop:            #checking range and pin 
                        loan_money=int(input("Enter amount of money to take (max 10000)!: "))
                        tmp_pin=int(input("Enter pin: "))
                        if 0<loan_money<=10000 and tmp_pin == pin[0]:
                            print()
                            print("Correct info!")
                            final_bal=init_bal[0]+loan_money
                            loan_loop=False
                            
                            #money sending into account
                            cur.execute("Insert into Active_loans(Accno,Debt_left) values(?,?)",(accno,loan_money+loan_money*(0.11)))
                            con.commit()    #saves changes

                            #updating customer table
                            cur.execute("update customers set Balance=? where Accno=?",(final_bal,accno))
                            con.commit()
                                                                                                                                                                
                            #uPdating Transaction tables!
                            cur.execute("insert into Transactions(Accno,Money,Type_TXN,Final_Bal) values(?,?,?,?)",(accno,loan_money,"Loan_added",final_bal))
                            con.commit()
                            print("Loan successfully taken!!")
                            
                        elif 0<loan_money<=10000 and tmp_pin !=pin[0]:
                            print("Inccorect pin")
                            print("Loan failed!")
                            loan_loop=False
                        else:
                            print("Money out of range!")
                   
                elif ch_for_loan==2:
                    print()
                    print("You have choosen to check debt!")

                    cur.execute("Select Debt_left from Active_loans where Accno=?",(accno,))
                    debt_tup=cur.fetchone()
                    debt_flag = True
                    if debt_tup==None:
                        print("You dont have active loans!")
                        debt_flag=False
                        
                    else:
                        print("Your debt amount is:",debt_tup[0])
                        print()
                    #asking for paying debt
                    print("+---------------------+")
                    print("| Do you want to:     |")
                    print("+---------------------+")
                    print("| 1) Pay Debt         |")
                    print("| 2) Do other actions |")
                    print("+---------------------+")
                    ch_pay_debt=int(input("Enter choice here: "))
                    if debt_flag:
                        if ch_pay_debt==1 :
                                    
                            cur.execute("select Debt_left from Active_loans where Accno=?",(accno,))
                            debt_amt=cur.fetchone()
                                
                            cur.execute("select pin from customers where Accno=?",(accno,))
                            pin_pay=cur.fetchone()

                            cur.execute("select Balance from customers where Accno=?",(accno,))
                            bal_of_user=cur.fetchone()

                            debt_pay_loop=True
                            print("Your debt is:",debt_amt[0])
                            
                            while debt_pay_loop:
                                pay_debt=float(input("Enter ammount to pay: "))
                                if pay_debt>debt_amt[0]:        #debt_amt is tuple so we take 0 index element
                                    print("Amount entered is too much!")
                                elif pay_debt<=0:
                                    print("Amount entered is NEGATIVE / ZERO!")
                                elif pay_debt<debt_amt[0]:
                                    print()
                                    if bal_of_user[0]>=pay_debt:
                                        print()
                                        print("You have sufficient balance in you account!")
                                        pin_check=int(input("Enter you pin: "))
                                            
                                        if pin_check==pin_pay[0]:           #pin checker + executer
                                            print("Entered pin is correct!")
                                            debt_remain = debt_amt[0] - pay_debt
                                            print("You have",debt_remain,"debt remaining!")

                                            new_balance = bal_of_user[0] - pay_debt     #user's new balance
                                            #updation of customers table
                                            cur.execute("update Customers set Balance= ? where Accno= ?",(new_balance,accno))
                                            con.commit()

                                            #updating loan table
                                            cur.execute("update Active_loans set Debt_left = ? where Accno = ?",(debt_remain,accno))
                                            con.commit()
                                            depy_pay_loop = False

                                            #updating Transaction table
                                            cur.execute("insert into transactions(Accno,Money,Type_TXN,Final_Bal) values(?,?,?,?)",(accno,pay_debt , "Loan_pay",new_balance))
                                            con.commit()
                                            break
                                        else:
                                            print("Transaction failed!")
                                            print("PIN not correct!")
                                            print()
                                            debt_pay_loop = False # breaks the loop
                                    else:
                                        print("Amount entered is not in your account!!")
                                        debt_pay_loop = False #user poor so loop break

                                elif pay_debt == debt_amt[0]:   #special case, removes the loan instead setting to zero
                                    print()
                                    pin_check=int(input("Enter you pin: "))
                                    if pin_check==pin_pay[0]:
                                        print("Entered pin is correct!")
                                        print("Your debt has been removed!")

                                        #updating loans
                                        cur.execute("delete from Active_loans where Accno=?",(accno,))
                                        con.commit()
                                        debt_pay_loop=False

                                        new_balance = bal_of_user[0] - pay_debt     #user's new balance
                                        #updation of customers table
                                        cur.execute("update Customers set Balance= ? where Accno= ?",(new_balance,accno))
                                        con.commit()

                                        #updating Transaction table
                                        cur.execute("insert into transactions(Accno,Money,Type_TXN,Final_Bal) values(?,?,?,?)",(accno,pay_debt , "Loan_pay",new_balance))
                                        con.commit()
                                        
                                    else:
                                        print("Transaction Failed!!!")
                                        debt_pay_loop=False
                                        loan_loop_pay=False
                   
                elif ch_for_loan==3:
                    print("Exiting loan mode!")
                    loan_loop=False
                    print()
            else:
                print("Account is frozen, cannot take instant loans!")
        elif ch_for_process==8:
            if not Freeze_factor:
                print()
                print("YOU HAVE CHOOSEN TO DELETE ACCOUNT!!")
                while True:
                    print("+------------------------------------------+")
                    print("| ARE YOU SURE YOU WANT TO DELETE ACCOUNT? |")
                    print("+------------------------------------------+")
                    print("| 1) Yes                                   |")
                    print("| 2) No                                    |")
                    print("+------------------------------------------+")
                    del_check_1=int(input("Enter choice here: "))
                    if del_check_1==2:
                        print()
                        print("Account deletion canceled!")
                        print("Thank you for not deleting account!")
                        print()
                        break
                    elif del_check_1==1:
                        print()
                        cur.execute("Select Acc_Password from customers where accno=?",(accno,))  #using placeholders
                        acc_pass_del=cur.fetchone()

                        cur.execute("Select pin from customers where accno=?",(accno,))
                        acc_pin_del=cur.fetchone()
                        
                        acc_pass_ask=input("Enter your Account password: ")
                        acc_pin_ask=int(input("Enter your pin: "))
                        
                        tmp_del_pass=acc_pass_del[0]
                        tmp_del_pin=acc_pin_del[0]
                        if acc_pass_ask==tmp_del_pass and acc_pin_ask==tmp_del_pin:
                            print("+-----------------+")
                            print("| You still sure? |")
                            print("+-----------------+")
                            print("| 1) Yes          |")
                            print("| 2) No           |")
                            print("+-----------------+")
                            del_check_2=int(input("Enter choice here: "))

                            if del_check_2==2:
                                print("YOU HAVE CHOOSEN NOT TO DELETE ACCOUNT!")
                                print()
                            elif del_check_2==1:        #user choose to delete account
                                print("It was nice knowing you!")
                                cur.execute("""update customers set
                                            First_name = NULL,
                                            Last_name = NULL,
                                            Ph_no = NULL,
                                            Adh_no = NULL,
                                            Acc_Creation_Date = NULL,
                                            Address = NULL,
                                            Branch = NULL,
                                            Acc_Password = NULL,
                                            pin = NULL,
                                            Balance = NULL,
                                            Recovery_Question = NULL,
                                            Recovery_Answer = NULL,
                                            Freeze_Status = NULL,
                                            Delete_Status = 1
                                            where accno=?""",(accno,))
                                con.commit()
                                print("Session ended!")
                                tmp_loop=False
                                break
                            else:
                                print("Termination of account failed!") #if user not choose 1 or 2
                        elif acc_pass_ask!=tmp_del_pass or acc_pin_ask!=tmp_del_pin:
                                print("Incorrect Account Password or PIN")
                                print()
            else:
                print("Account is frozen, cannot delete account!")

        elif ch_for_process==9:
            if not Freeze_factor:

                cur.execute("Select * from virtual_gold_customer where accno=(?);",(accno,))
                accno_check=cur.fetchone()
                if accno_check == None:
                    cur.execute("insert into virtual_gold_customer values(?,0.0,0.0);",(accno,))
                    con.commit()
                print()
                print("You have choosen VIRTUAL GOLD!\n ")
                print()
                print("+"+"-"*27+"+")
                print("| Would you like to         |")
                print("+"+"-"*27+"+")
                print("| 1) Purchase Virtual Gold  |")
                print("| 2) Sell Your Virtual Gold |")
                print("| 3) See Gold Trend         |")
                print("+"+"-"*27+"+")

                while (True) :
                    tmp_ch=int(input("Enter your choice here:"))
                    if tmp_ch in [1,2,3]:
                        break
                    else:
                        print("Invalid choice!")
                        print()
                
                if tmp_ch == 1:
                    print()
                    print("You have chosen to buy Virtual Gold!\n")
                    print("+"+"-"*46+"+") 
                    print("| Enter what purity gold you would like to buy |")
                    print("+"+"-"*46+"+")
                    print("| 1) 24 karat gold                             |")
                    print("| 2) 18 karat gold                             |")
                    print("+"+"-"*46+"+")
                    print()
                    while (True) :
                        tmp_purity=int(input("Enter your choice here:"))
                        if tmp_purity == 1 or tmp_purity == 2:
                            break
                        else:
                            print("Invalid choice!")
                            print()
                    
                    if tmp_purity == 1:
                        print("You have chosen to buy 24k purity gold!")
                        print()
                        cur.execute("Select Price_24 from Virtual_gold_price;")
                        Price_24=cur.fetchall()[-1][0]
                        cur.execute("Select date_time from Virtual_gold_price;")
                        Time=cur.fetchall()[-1][0]
                        print("The price of gold on, "+str(Time).split(" ")[0]+", is",Price_24,"per gram!")
                        print()
                        while True:
                            amt_24=float(input("Enter the amount to buy in grams: "))
                            if amt_24 < 0 :
                                print("Amount cannot be NEGATIVE/ZERO!")
                            else:
                                break
                        cur.execute("Select Amount_24 from virtual_gold_customer where accno=(?);",(accno,))
                        old_amt_24=cur.fetchone()[0]
                        
                        new_amt_24=old_amt_24 + amt_24
                        cost_price_24 = (amt_24) * (Price_24)
                        print()
                        print("The amount you have to pay is:",cost_price_24)
                        
                        #for purchasing
                        Transaction_Online=True
                        Transaction_Status="Unknown"
                        while(Transaction_Online):
                            cur.execute("select * from customers where accno=?",(accno,))
                            rows=cur.fetchall()
                            column_names=[]
                            for i in cur.description:
                                column_names.append(i[0])
                            Acc_Info=pd.DataFrame(data=rows,columns=column_names)

                            withdraw_amount = cost_price_24
                            while True:
                                pin_input=int(input("Enter your 4 digit secret PIN:"))
                                if(pin_input>=10000):
                                    print("Entered PIN is more than 4 digits.\nRetry\n")
                                elif(pin_input<1000):
                                    print("Entered PIN is less than 4 digits.\nRetry\n")
                                else:
                                    break
                            if(pin_input!=Acc_Info["pin"][0]):
                                print("Transaction Declined - Incorrect PIN")
                                Transaction_Status="Failed"
                                Transaction_Online=False
                                break
                            if(withdraw_amount>Acc_Info["Balance"][0]):
                                print("Purchased Declined - Insufficient Balance")
                                Transaction_Status="Failed"
                                Transaction_Online=False
                                break
                            
                            Final_Balance=Acc_Info['Balance'][0]-withdraw_amount
                            cur.execute("update customers set balance=? where accno=?;",(Final_Balance,accno))
                            con.commit()
                            Transaction_Status="Success"
                            Transaction_Online=False
                            cur.execute("insert into transactions(Accno,Money,Type_TXN,Final_Bal) values(?,?,'Withdraw',?)",(accno,withdraw_amount,Final_Balance))
                            con.commit()
                            print()
                            print("Initial Balance --> Final Balance")
                            print("₹"+str(Acc_Info['Balance'][0])+" --> "+"₹"+str(Final_Balance))
                            print("Initial Gold Amount --> Final Gold Balance")
                            print(old_amt_24,"g -->",new_amt_24,'g')
                            print()
                            print("Purchase Successful")

                            #for updating gold table
                            cur.execute("Update virtual_gold_customer set amount_24 = (?) where accno=(?);",(new_amt_24,accno))
                            con.commit()
                    elif tmp_purity == 2:
                        print("You have chosen to buy 18k purity gold!")
                        print()
                        cur.execute("Select Price_18 from Virtual_gold_price;")
                        Price_18=cur.fetchall()[-1][0]
                        cur.execute("Select date_time from Virtual_gold_price;")
                        Time=cur.fetchall()[-1][0]
                        print("The price of gold on, "+str(Time).split(" ")[0]+", is",Price_18,"per gram!")
                        print()
                        while True:
                            amt_18=float(input("Enter the amount to buy in grams: "))
                            if amt_18 < 0 :
                                print("Amount cannot be NEGATIVE/ZERO!")
                            else:
                                break
                        cur.execute("Select Amount_18 from virtual_gold_customer where accno=(?);",(accno,))
                        old_amt_18=cur.fetchone()[0]
                        
                        new_amt_18=old_amt_18 + amt_18
                        cost_price_18 = (amt_18) * (Price_18)
                        print()
                        print("The amount you have to pay is:",cost_price_18)
                        
                        #for purchasing
                        Transaction_Online=True
                        Transaction_Status="Unknown"
                        while(Transaction_Online):
                            cur.execute("select * from customers where accno=?",(accno,))
                            rows=cur.fetchall()
                            column_names=[]
                            for i in cur.description:
                                column_names.append(i[0])
                            Acc_Info=pd.DataFrame(data=rows,columns=column_names)

                            withdraw_amount = cost_price_18
                            while True:
                                pin_input=int(input("Enter your 4 digit secret PIN:"))
                                if(pin_input>=10000):
                                    print("Entered PIN is more than 4 digits.\nRetry\n")
                                elif(pin_input<1000):
                                    print("Entered PIN is less than 4 digits.\nRetry\n")
                                else:
                                    break
                            if(pin_input!=Acc_Info["pin"][0]):
                                print("Transaction Declined - Incorrect PIN")
                                Transaction_Status="Failed"
                                Transaction_Online=False
                                break
                            if(withdraw_amount>Acc_Info["Balance"][0]):
                                print("Purchased Declined - Insufficient Balance")
                                Transaction_Status="Failed"
                                Transaction_Online=False
                                break
                            
                            Final_Balance=Acc_Info['Balance'][0]-withdraw_amount
                            cur.execute("update customers set balance=? where accno=?;",(Final_Balance,accno))
                            con.commit()
                            Transaction_Status="Success"
                            Transaction_Online=False
                            cur.execute("insert into transactions(Accno,Money,Type_TXN,Final_Bal) values(?,?,'Withdraw',?)",(accno,withdraw_amount,Final_Balance))
                            con.commit()
                            print()
                            print("Initial Balance --> Final Balance")
                            print("₹"+str(Acc_Info['Balance'][0])+" --> "+"₹"+str(Final_Balance))
                            print("Initial Gold Amount --> Final Gold Balance")
                            print(old_amt_18,"g -->",new_amt_18,'g')
                            print()
                            print("Purchase Successful")

                            #for updating gold table
                            cur.execute("Update virtual_gold_customer set amount_18 = (?) where accno=(?);",(new_amt_18,accno))
                            con.commit()

                elif tmp_ch == 2:
                    print("You have chosen to sell Virtual Gold")
                    print("+"+"-"*47+"+") 
                    print("| Enter what purity gold you would like to sell |")
                    print("+"+"-"*47+"+")
                    print("| 1) 24 karat gold                              |")
                    print("| 2) 18 karat gold                              |")
                    print("+"+"-"*47+"+")
                    print()
                    while (True) :
                        tmp_purity=int(input("Enter your choice here: "))
                        if tmp_purity == 1 or tmp_purity == 2:
                            break
                        else:
                            print("Invalid choice!")
                            print()
                    print()
                    if tmp_purity == 1:
                        print("You have chosen to sell 24k purity gold!")
                        print()
                        
                        cur.execute("Select Price_24 from Virtual_gold_price;")
                        Price_24=cur.fetchall()[-1][0]
                        cur.execute("Select date_time from Virtual_gold_price;")
                        Time=cur.fetchall()[-1][0]
                        cur.execute("Select Amount_24 from virtual_gold_customer where accno=(?);",(accno,))
                        old_amt_24=cur.fetchone()[0]
                        
                        if old_amt_24 == 0:
                            print("You dont possess 24k gold!")
                            
                        else:
                            print("The price of gold on, "+str(Time).split(" ")[0]+", is",Price_24,"per gram!")
                            print("You have,", old_amt_24,'g')
                            print()
                            while True:
                                amt_24=float(input("Enter the amount to sell in grams: "))
                                if amt_24 < 0 :
                                    print("Amount cannot be NEGATIVE!")
                                else:
                                    break
                            
                            new_amt_24=old_amt_24 - amt_24
                            sell_price_24 = (amt_24) * (Price_24)
                            print()
                            print("The amount you will earn is:",sell_price_24)
                            Transaction_Online=True
                            Transaction_Status="Unknown"
                            while(Transaction_Online):
                                
                                cur.execute("select * from customers where accno=?",(accno,))
                                rows=cur.fetchall()
                                column_names=[]
                                for i in cur.description:
                                    column_names.append(i[0])
                                Acc_Info=pd.DataFrame(data=rows,columns=column_names)
                                deposit_amount_input = sell_price_24
                                while True:
                                    pin_input=int(input("Enter your 4 digit secret PIN:"))
                                    if(pin_input>=10000):
                                        print("Entered PIN is more than 4 digits.\nRetry\n")
                                    elif(pin_input<1000):
                                        print("Entered PIN is less than 4 digits.\nRetry\n")
                                    else:
                                        break
                                if(pin_input!=Acc_Info["pin"][0]):
                                    print("Transaction Declined - Incorrect PIN")
                                    Transaction_Status="Failed"
                                    Transaction_Online=False
                                    break

                                Final_Balance=Acc_Info['Balance'][0]+deposit_amount_input
                                cur.execute("update customers set balance=? where accno=?;",(Final_Balance,accno))
                                con.commit()
                                Transaction_Status="Success"
                                Transaction_Online=False
                                cur.execute("insert into transactions(Accno,Money,Type_TXN,Final_Bal) values(?,?,'Deposit',?)",(accno,deposit_amount_input,Final_Balance))
                                con.commit()
                                print()
                                print("Initial Balance --> Final Balance")
                                print("₹"+str(Acc_Info['Balance'][0])+" --> "+"₹"+str(Final_Balance))
                                print("Initial Gold Amount --> Final Gold Amount")
                                print(old_amt_24,"g -->",new_amt_24,'g')
                                print()
                                print("Purchase Successful")
                                      
                            #for updating gold table
                            cur.execute("Update virtual_gold_customer set amount_24 = (?) where accno=(?);",(new_amt_24,accno))
                            con.commit()
                
                    elif tmp_purity == 2:
                        print("You have chosen to sell 18k purity gold!")
                        print()
                        
                        cur.execute("Select Price_18 from Virtual_gold_price;")
                        Price_18=cur.fetchall()[-1][0]
                        cur.execute("Select date_time from Virtual_gold_price;")
                        Time=cur.fetchall()[-1][0]
                        cur.execute("Select Amount_18 from virtual_gold_customer where accno=(?);",(accno,))
                        old_amt_18=cur.fetchone()[0]
                        
                        if old_amt_18 == 0:
                            print("You dont possess 18k gold!")
                            
                        else:
                            print("The price of gold on, "+str(Time).split(" ")[0]+", is",Price_18,"per gram!")
                            print("You have,", old_amt_18,'g')
                            print()
                            while True:
                                amt_18=float(input("Enter the amount to sell in grams: "))
                                if amt_18 < 0 :
                                    print("Amount cannot be NEGATIVE!")
                                else:
                                    break
                            
                            new_amt_18=old_amt_18 - amt_18
                            sell_price_18 = (amt_18) * (Price_18)
                            print()
                            print("The amount you will earn is:",sell_price_18)
                            Transaction_Online=True
                            Transaction_Status="Unknown"
                            while(Transaction_Online):
                                
                                cur.execute("select * from customers where accno=?",(accno,))
                                rows=cur.fetchall()
                                column_names=[]
                                for i in cur.description:
                                    column_names.append(i[0])
                                Acc_Info=pd.DataFrame(data=rows,columns=column_names)
                                deposit_amount_input = sell_price_18
                                while True:
                                    pin_input=int(input("Enter your 4 digit secret PIN:"))
                                    if(pin_input>=10000):
                                        print("Entered PIN is more than 4 digits.\nRetry\n")
                                    elif(pin_input<1000):
                                        print("Entered PIN is less than 4 digits.\nRetry\n")
                                    else:
                                        break
                                if(pin_input!=Acc_Info["pin"][0]):
                                    print("Transaction Declined - Incorrect PIN")
                                    Transaction_Status="Failed"
                                    Transaction_Online=False
                                    break

                                Final_Balance=Acc_Info['Balance'][0]+deposit_amount_input
                                cur.execute("update customers set balance=? where accno=?;",(Final_Balance,accno))
                                con.commit()
                                Transaction_Status="Success"
                                Transaction_Online=False
                                cur.execute("insert into transactions(Accno,Money,Type_TXN,Final_Bal) values(?,?,'Deposit',?)",(accno,deposit_amount_input,Final_Balance))
                                con.commit()
                                print()
                                print("Initial Balance --> Final Balance")
                                print("₹"+str(Acc_Info['Balance'][0])+" --> "+"₹"+str(Final_Balance))
                                print("Initial Gold Amount --> Final Gold Amount")
                                print(old_amt_18,"g -->",new_amt_18,'g')
                                print()
                                print("Purchase Successful")
                                      
                            #for updating gold table
                            cur.execute("Update virtual_gold_customer set amount_18 = (?) where accno=(?);",(new_amt_18,accno))
                            con.commit()

                elif tmp_ch == 3:
                    print("You have chosen to see the trends of our virtual gold!")
                    cur.execute("Select Price_18 from virtual_gold_price;")
                    tup_18k=cur.fetchall()
                    cur.execute("Select Price_24 from virtual_gold_price;")
                    tup_24k=cur.fetchall()
                    
                    cur.execute("Select Date_time from virtual_gold_price;")
                    DT_tup=cur.fetchall()
                    DT_list=[]
                    for i in range(len(DT_tup)):
                        DT_list.append(str(DT_tup[i][0]).split(" ")[0])
                    pl.plot(DT_list,tup_24k,marker='o',color="#C9B226",label='24 karat')
                    pl.plot(DT_list,tup_18k,marker='x',color="#CD7F32",label='18 karat')
                    pl.grid()
                    pl.title("GOLD TRENDS OVER TIME")
                    pl.xlabel("Date")
                    pl.ylabel("Gold Price")
                    pl.legend(loc="upper right")
                    pl.show()
            else:
                print("Account is frozen, cannot buy virtual gold!")

        elif ch_for_process==10:
            print()
            print("You have choosen to check your balance!")
            print()
            cur.execute("Select Balance from customers where Accno=?",(accno,))
            Balance=cur.fetchone()
            print("Your balance is:",Balance[0])
        elif ch_for_process==11:
            #account profile thingie
            cur.execute("select * from customers;")
            rows=cur.fetchall()
            column_names=[]
            for i in cur.description:
                column_names.append(i[0])
            customers_table=pd.DataFrame(data=rows,columns=column_names)
            
            acc_info=customers_table[customers_table["Accno"]==accno]
            tmp_acc_data=[acc_info.iloc[0].loc['Accno'],acc_info.iloc[0].loc['First_name'],
                           acc_info.iloc[0].loc['Last_name'],acc_info.iloc[0].loc['Ph_no'],
                           str(acc_info.iloc[0].loc['Acc_Creation_Date']),acc_info.iloc[0].loc['Adh_no'],
                           acc_info.iloc[0].loc['Address'],acc_info.iloc[0].loc['Branch']]
            tmp_max_len=0
            for i in tmp_acc_data:
                if len(i)>tmp_max_len:
                    tmp_max_len=len(i)
            print("+-------------------------"+"-"*(tmp_max_len+1)+"+")        
            print("| Account Profile Page    "+" "*(tmp_max_len+1)+"|")
            print("+-----------------------+-"+"-"*(tmp_max_len+1)+"+")
            print("| Account Number        | "+tmp_acc_data[0]+" "*(tmp_max_len-len(tmp_acc_data[0]))+" |")
            print("| First Name            | "+tmp_acc_data[1]+" "*(tmp_max_len-len(tmp_acc_data[1]))+" |")
            print("| Last Name             | "+tmp_acc_data[2]+" "*(tmp_max_len-len(tmp_acc_data[2]))+" |")
            print("| Phone Number          | "+tmp_acc_data[3]+" "*(tmp_max_len-len(tmp_acc_data[3]))+" |")
            print("| Account Creation Date | "+tmp_acc_data[4]+" "*(tmp_max_len-len(tmp_acc_data[4]))+" |")
            print("| Aadhaar Number        | "+tmp_acc_data[5]+" "*(tmp_max_len-len(tmp_acc_data[5]))+" |")
            print("| Address               | "+tmp_acc_data[6]+" "*(tmp_max_len-len(tmp_acc_data[6]))+" |")
            print("| Branch                | "+tmp_acc_data[7]+" "*(tmp_max_len-len(tmp_acc_data[7]))+" |")
            print("+-----------------------+-"+"-"*(tmp_max_len+1)+"+")
        elif ch_for_process==12:
            #freeze unfreeze
            print()
            print("+"+"-"*44+"+")
            print("|You have choosen to Freeze/Unfreeze account!|")
            print("+"+"-"*44+"+")
            print("| What would you like to do:                 |")
            print("| 1) Freeze account                          |")
            print("| 2) Unfreeze account                        |")
            print("| 3) Do other action                         |")
            print("+"+"-"*44+"+")
            
            ch_for_frez=int(input("Enter you choice here: "))
            cur.execute("Select Freeze_Status from customers where Accno=?",(accno,))  #geting freeze status
            Freeze_status=cur.fetchone()[0]
            if ch_for_frez == 1:
                if Freeze_status==1: # account already frozen!
                    print("Your account is already frozen!")
                elif Freeze_status==0:
                    print()
                    print("You have choosen to freeze account!")
                    #getting password
                    cur.execute("select Acc_password from customers where Accno=?;",(accno,))
                    acc_password=cur.fetchone()[0]
                    pass_loop=1
                    while pass_loop <=3:
                        ask_pass=input("Enter your account password: ")
                        if ask_pass == acc_password:
                            print()
                            print("Correct password!")
                            cur.execute("update customers set Freeze_Status = 1 where Accno=?;",(accno,))
                            con.commit()
                            Freze_status=1
                            print("Account frozen successfully!")
                            pass_loop=100
                        else:
                            print("Passwords do not match!")
                            pass_loop = pass_loop + 1
            elif ch_for_frez == 2:
                if Freeze_status==0: #Account is not frozen
                    print("Account not frozen!")
                else:
                    print()
                    print("You have choosen to Unfreeze account!")
                    #geeting password
                    cur.execute("select Acc_password from customers where Accno=?;",(accno,))
                    acc_password=cur.fetchone()[0]
                    #getting pin
                    cur.execute("select pin from customers where Accno=?;",(accno,))
                    acc_pin=cur.fetchone()[0]
                    unfrez_loop=1
                    cur.execute("select Recovery_Question from customers where Accno=?;",(accno,))
                    tmp_ques=cur.fetchone()[0]
                    cur.execute("select Recovery_Answer from customers where Accno=?;",(accno,))
                    tmp_rec_ans=cur.fetchone()[0]
                    while unfrez_loop <=3:
                        ask_pass=input("Enter your password: ")
                        ask_pin=int(input("Enter you pin: "))
                        print()
                        print(tmp_ques)
                        ask_rec_ans=input("Enter the answer: ").lower()
                        if ask_pass == acc_password and ask_pin==acc_pin and ask_rec_ans==tmp_rec_ans:
                            print()
                            print("Correct pin and password and correct answer!")
                            cur.execute("update customers set Freeze_Status = 0 where Accno=?;",(accno,))
                            con.commit()
                            print("Account unfrozen successfully!")
                            unfrez_loop=1000
                        else:
                            print("Incorrect password or pin or incorrect answer to recovery question!\nRetry!")
            else:
                pass
                            
        elif ch_for_process==13:
            tmp_loop=False
            print("Thank you for Choosing Aurum Trust Bank as Your Banking Solution!")
                    #some nice ending lines 
            tmp_gret_list=[ "Your Rupees Will Miss You :(",
                            "We hope you have a prosperous and golden day ahead of you!",
                            "Your Future. Your Goals. Your Bank.\nThank You For Banking With Us.",
                            "Stay Golden. Stay Prosperous. Stay Aurum.\nThank You For Banking With Us.",
                            "May Your Aspirations Continue To Grow.\nThank You For Banking With Us.",
                            "Until Next Time —\nStay Secure, Stay Prosperous, Stay Golden.",
                            "Go Chase Dreams —\nWe'll Guard The Treasure.",
                            "Keep Building.\nRome Wasn't Funded In A Day.",
                            "Your Dreams Are Only One Withdrawal Away.",
                            "Every Great Journey Begins With A Single Step.\nAnd An Aurum Account.",
                            "The Gold Was Never In The Vault.\nThe Gold Was You All Along."
                            ]
            print(tmp_gret_list[np.random.randint(0,11)])      #to get random ending line
            print()
            print()
            print()
            print("Aryan And Utkarsh are the founders of Aurum Trust Bank!")
            sys.exit()
        print()
else:
    if(admin_login==False) and accs_list:           # if there is account + too many attempts!
        #termination of session block
        print("SESSION TERMINANTED!!")
        print("REASON: 3 INCORRECT ATTEMPTS OF PASSWORD!!")
    else:
        tmp_admin_flag=False
        for i in range(3):
            tmp1="Please Enter Administrator Password ("+str(3-i)+" Attempts Remaining) : "
            tmp_admin_pass_check=input(tmp1)
            if(tmp_admin_pass_check==admin_pass):
                tmp_admin_flag=True
                break
        if(tmp_admin_flag):
            while True:
                print("\n"+"="*100+"\n\nWelcome Admin!")
                print("\nOnly use this panel if you know what you are doing.\n")
                print("+"+"-"*38+"+")
                print("| ADMINISTRATOR PANEL                  |")
                print("+"+"-"*38+"+")
                print("| 1) See All Account Holders           |")
                print("| 2) Edit Account Information          |")
                print("| 3) Delete an account                 |")
                print("| 4) Purge all accounts and their data |")
                print("| 5) QUIT                              |")
                print("+"+"-"*38+"+")
                tmp_choice=int(input("Enter your choice here: "))
                
                cur.execute("select * from customers;")
                rows=cur.fetchall()
                column_names=[]
                for i in cur.description:
                    column_names.append(i[0])
                customers_table=pd.DataFrame(data=rows,columns=column_names)
                    
                if(tmp_choice==1):
                    while True:
                        #for asking accno from admin
                        print()
                        cur.execute("select Accno from customers where Delete_Status=0 order by Accno;")
                        tmp_accnos_tup=cur.fetchall()
                        columns_names=["All Account Numbers: "]
                        tmp_accnos_df=pd.DataFrame(data=tmp_accnos_tup,columns=columns_names)
                        print(tmp_accnos_df)
                        print()
                        while True:
                            tmp_flag_edit=True
                            accno=input("Enter Account Number (AUXXXXXXXX): ").upper()
                            if(len(accno)!=10):
                                print("Invalid Length of Account Number. Must be of length 10.")
                                continue
                            if("AU" not in accno):
                                print("Bank Prefix 'AU' not used.")
                                continue
                            acc_info=customers_table[customers_table["Accno"]==accno]
                            if(len(acc_info)==0):
                                print("Entered Account Does Not Exist.")
                                tmp_flag_edit=False
                                break
                            break
                        if(tmp_flag_edit==False):
                            break
                        
                        print("Selected Account Holder:")
                        print()
                        print(acc_info.iloc[0])
                        print()
                        print("+"+"-"*42+"+")
                        print("| Would You like to return to admin panel? |")
                        print("+"+"-"*42+"+")
                        print("| 1) Yes                                   |")
                        print("| 2) No                                    |")
                        print("+"+"-"*42+"+")
                        tmp_choice_leave=int(input("Enter your choice here: "))
                        if(tmp_choice_leave==1):
                            break
                        else:
                            continue
                    
                elif tmp_choice==2:
                    while True:
                        print()
                        tmp_flag_edit=True
                        accno=input("Enter Account Number (AUXXXXXXXX): ").upper()
                        if(len(accno)!=10):
                            print("Invalid Length of Account Number. Must be of length 10.")
                            continue
                        if("AU" not in accno):
                            print("Bank Prefix 'AU' not used.")
                            continue
                        acc_info=customers_table[customers_table["Accno"]==accno]
                        if(len(acc_info)==0):
                            print("Entered Account Does Not Exist.")
                            tmp_flag_edit=False
                            break
                        break
                    if(tmp_flag_edit==False):
                        break
                    print()
                    print("+"+"-"*36+"+")
                    print("| Choose Task                        |")
                    print("+"+"-"*36+"+")
                    print("| 1) Change Phone Number             |")
                    print("| 2) Change Address                  |")
                    print("| 3) Change Password                 |")
                    print("| 4) Change PIN                      |")
                    print("| 5) Change Recovery Question Answer |")
                    print("| 6) Freeze/Unfreeze Account         |")
                    print("+"+"-"*36+"+")
                    tmp_choice_task=int(input("Enter your choice here: "))
                        
                    if(tmp_choice_task==1):
                        print()
                        while True:
                            tmp_new_field=input("Enter new 10 digit phone number: ")
                            if(len(tmp_new_field)!=10):
                                print("Not a 10 digit phone number. Retry")
                            else:
                                break
                        cur.execute("update customers set Ph_no=? where Accno=?;",(tmp_new_field,accno))
                        con.commit()
                        print("Succesfully Updated Phone Number.")
                        
                    elif (tmp_choice_task==2):
                        print()
                        while True:
                            tmp_new_field=input("Enter new address: ")
                            if(len(tmp_new_field)>100):
                                print("Length of Address too big. Retry")
                            else:
                                break
                        cur.execute("update customers set Address=? where Accno=?;",(tmp_new_field,accno))
                        con.commit()
                        print("Succesfully Updated Address.")
                            
                    elif (tmp_choice_task==3):
                        print()
                        while True:
                            tmp_new_field=input("Enter new password: ")
                            if(not(len(tmp_new_field)>=8 and len(tmp_new_field)<=20)):
                                print("Password must be between length 8 to 20. Retry")
                            else:
                                break
                        cur.execute("update customers set Acc_Password=? where Accno=?;",(tmp_new_field,accno))
                        con.commit()
                        print("Succesfully Updated Password.")
                        
                    elif (tmp_choice_task==4):
                        print()
                        while True:
                            tmp_new_field=int(input("Enter new PIN: "))
                            if(len(str(tmp_new_field))>4):
                                print("PIN must be 4 digits. Retry")
                            else:
                                break
                        cur.execute("update customers set pin=? where Accno=?;",(tmp_new_field,accno))
                        con.commit()
                        print("Succesfully Updated PIN.")
                        
                    elif (tmp_choice_task==5):
                        print()
                        while True:
                            tmp_new_field=input("Enter new Safety Question Answer: ")
                            if(len(tmp_new_field)>100):
                                print("Length of Safety Question Answer too big. Retry")
                            else:
                                break
                        cur.execute("update customers set Recovery_Answer=? where Accno=?;",(tmp_new_field,accno))
                        con.commit()
                        print("Succesfully Updated Safety Question Answer.")
                    
                    elif(tmp_choice_task==6):
                        print()
                        tmp_freeze_status=acc_info["Freeze_Status"].iloc[0]
                        if(tmp_freeze_status==0):
                            cur.execute("update customers set Freeze_Status=1 where Accno=?",(accno,))
                            con.commit()
                            print("Account has been succesfully FREEZED.")
                        else:
                            cur.execute("update customers set Freeze_Status=0 where Accno=?",(accno,))
                            con.commit()
                            print("Account has been succesfully UN-FREEZED.")
                    
                    else:
                        print()
                        print("Invalid Choice. Retry.")
                
                elif tmp_choice==3:
                    while True:
                        print()
                        tmp_flag_edit=True
                        accno=input("Enter Account Number to delete (AUXXXXXXXX): ").upper()
                        if(len(accno)!=10):
                            print("Invalid Length of Account Number. Must be of length 10.")
                            continue
                        if("AU" not in accno):
                            print("Bank Prefix 'AU' not used.")
                            continue
                        acc_info=customers_table[customers_table["Accno"]==accno]
                        if(len(acc_info)==0):
                            print("Entered Account Does Not Exist.")
                            tmp_flag_edit=False
                            break
                        break
                    if(tmp_flag_edit==False):
                        break
                    print()
                    print("+"+"-"*15+"+")
                    print("| Are You Sure? |")
                    print("+"+"-"*15+"+")
                    print("| 1) Yes        |")
                    print("| 2) No         |")
                    print("+"+"-"*15+"+")
                    tmp_choice_leave=int(input("Enter your choice here: "))
                    if(tmp_choice_leave==1):
                        cur.execute("""update customers set
                                        First_name = NULL,
                                        Last_name = NULL,
                                        Ph_no = NULL,
                                        Adh_no = NULL,
                                        Acc_Creation_Date = NULL,
                                        Address = NULL,
                                        Branch = NULL,
                                        Acc_Password = NULL,
                                        pin = NULL,
                                        Balance = NULL,
                                        Recovery_Question = NULL,
                                        Recovery_Answer = NULL,
                                        Freeze_Status = NULL,
                                        Delete_Status = 1
                                        where accno=?""",(accno,))
                        con.commit()
                        print("Account Deleted Succesfully.")
                    else:
                        print("ABORTED!")
                
                elif (tmp_choice==4):
                    print()
                    print("+"+"-"*52+"+")
                    print("| Are you sure To Purge all accounts and their data? |")
                    print("+"+"-"*52+"+")
                    print("| 1) Yes                                             |")
                    print("| 2) No                                              |")
                    print("+"+"-"*52+"+")
                    tmp_choice_leave=int(input("Enter your choice here: "))
                    if(tmp_choice_leave==1):
                        cur.execute("delete from customers;")
                        cur.execute("delete from Active_Loans;")
                        cur.execute("delete from transactions;")
                        cur.execute("delete from Virtual_Gold_customer;")
                        cur.execute("delete from virtual_gold_price;")
                        con.commit()
                        print("Succesfully Purged All Accounts and their data.")
                    else:
                        print("ABORTED!!")
                 
                elif (tmp_choice==5):
                    print()
                    print("Goodbye Admin!")
                    break
                    
                else:
                    print("Invalid Choice. Retry.")
            
        else:
            #termination of session block
            print("SESSION TERMINANTED!!")
            print("REASON: 3 INCORRECT ATTEMPTS OF PASSWORD!!")

