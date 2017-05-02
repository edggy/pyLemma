import mysql.connector 
from mysql.connector import errorcode
import my_sql_class

# This file is trying to test whether mysql
try:
	conn = mysql.connector.connect(
		user="root",
		password="gengruijie",
		host= "127.0.0.1",
		database ="Lemma"
		)

except mysql.connector.Error as e:
	if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
		print("Something is wrong with username or Password")
	elif e.errno == errorcode.ER_BAD_DB_ERROR:
		print("DataBase does not exist")
	else:
		print(e)


hw = my_sql_class.Database_mysql("root","gengruijie","127.0.0.1","Lemma")
# hw.create_hw_table()

# information = [1,'ABCD',"123",21]
# hw.add_hw_data(table_name,information)

# hw.add_student_hw("Ruijie",1234,1234)
# hw.delete("student1")

# hw.drop("student1")    # it does not exist any more.
# hw.drop("student1_hw8")    # it does not exist any more.


# hw.read_code("Ruijie","hw8")

commend = input("What is the commend? (up_load or down_load) ")
if commend == "up_load":
	name = input("what is name? ")
	hw_name = input("what is homework name? ")
	file_name = input("what is file name? ")
	hw.up_load_code(name,hw_name,file_name)

else:
	hw.show_student()
	name = input("who does you want to download? ")
	hw.show_homework(name)
	homework_name = input("what is homework name? ")
	output = name+"_"+homework_name+".prf"
	hw.down_load_file(name,homework_name,output)


















