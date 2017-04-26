import mysql.connector 
from mysql.connector import errorcode
import my_sql_class

# This file is trying to test whether mysql
try:
	print("Hello world")
	conn = mysql.connector.connect(
		user="root",
		password="gengruijie",
		host= "127.0.0.1",
		database ="Lemma"
		)
	print("It works!!")

except mysql.connector.Error as e:
	if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
		print("Something is wrong with username or Password")
	elif e.errno == errorcode.ER_BAD_DB_ERROR:
		print("DataBase does not exist")
	else:
		print(e)


hw = my_sql_class.Database_mysql("root","gengruijie","127.0.0.1","Lemma")
# hw.create_hw_table()

table_name = "student1_hw8"
# information = [1,'ABCD',"123",21]
# hw.add_hw_data(table_name,information)

# hw.add_student_hw("Ruijie",1234,1234)
# hw.delete("student1")
# hw.drop(table_name)    # it does not exist any more.


# hw.read_code("Ruijie","hw8")
# hw.up_load_code("Ruijie","hw8","test.prf")

hw.down_load_file("Ruijie","hw8","testout.prf")