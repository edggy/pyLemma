import mysql.connector 
from mysql.connector import errorcode

# This file is trying to test whether mysql
try:
	print("Hello world")
	conn = mysql.connector.connect(
		user="root",
		password="gengruijie",
		host= "127.0.0.1",
		database ="Student"
		)
	print("It works!!")

except mysql.connector.Error as e:
	if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
		print("Something is wrong with username or Password")
	elif e.errno == errorcode.ER_BAD_DB_ERROR:
		print("DataBase does not exist")
	else:
		print(e)


