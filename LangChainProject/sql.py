import sqlite3

connection = sqlite3.connect("student.db") #connecting to sql
cursor =connection.cursor() #create cursor object to insert record, create table, retrieve 

#create the table
table_info=""" 
        CREATE TABLE student (
        Name VARCHAR(50),
        Class VARCHAR(25),
        Section vARCHAR(25),
        Marks int);
"""

cursor.execute(table_info)

#inserting records

cursor.execute('''Insert Into STUDENT values('Krish','Data Science','A',90)''')
cursor.execute('''Insert Into STUDENT values('Sudhanshu','MLops','B',100)''')
cursor.execute('''Insert Into STUDENT values('Darius','Data Science','A',86)''')
cursor.execute('''Insert Into STUDENT values('Vikash','DEVOPS','A',50)''')
cursor.execute('''Insert Into STUDENT values('Dipesh','DEVOPS','B',35)''')
cursor.execute('''Insert Into STUDENT values('Mansi','MLops','A',90)''')
cursor.execute('''Insert Into STUDENT values('Paula','MLops','B',87)''')
cursor.execute('''Insert Into STUDENT values('Annie','Data Science','A',92)''')
cursor.execute('''Insert Into STUDENT values('Kyle','DEVOPS','B',43)''')
cursor.execute('''Insert Into STUDENT values('Joeseph','DEVOPS','B',65)''')

#displaying the records
print("The inserted records are:")
data= cursor.execute('''SELECT*from student''')

for r in data:
    print(r)

#close3 the connection
connection.commit()
connection.close()