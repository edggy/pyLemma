import mysql.connector 
from mysql.connector import errorcode

class Database_mysql:
	def __init__(self, user, password,host,database_name):
		self.user = user
		self.password = password
		self.host = host
		self.database = database_name
		# self.conn
		# self.cur

		try:
			self.conn = mysql.connector.connect(
				user=user,
				password=password,
				host= host,
				database =database_name)

			self.cur = self.conn.cursor()
				
		except mysql.connector.Error as e:
			if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
				print("Something is wrong with username or Password")
			elif e.errno == errorcode.ER_BAD_DB_ERROR:
				print("DataBase does not exist")
			else:
				print(e)

	def up_load(self,file,table_name):
		pass

	def create_hw_table(self,table_name):
		# table_name #= "gengruijie_hw1234"#input("Please entre the table name ==> ")
		query = "CREATE TABLE " + table_name +"""(
												id int NOT NULL AUTO_INCREMENT,
        										LineNo varchar(11) NOT NULL,
        										Part varchar(11) NOT NULL,
        										Sentence varchar(255) NOT NULL,
        										InferenceRule varchar(255), 
												reference varchar(11),
												Date datetime NOT NULL,
												primary key(id)
												)"""
		self.cur.execute(query)
		self.conn.commit()



	def add_hw_data(self,table_name,info):#,part,step2save,text2save, rule2save,refs2save):
		 #input("Please entre the table name you want to add")
		query = "INSERT INTO "+ table_name +" ( Part, LineNo, Sentence,InferenceRule,reference,Date)  "+' VALUES (%s,%s,%s,%s,%s ,NOW())'
		self.cur.execute(query,info)
		self.conn.commit()

		# "INSERT INTO "+ table_name +" (Part, Sentence,InferenceRule,reference,Date) " +' VALUES (?,?,?,? ,NOW())',information

	def add_student(self,info):
		table_name = "Student"		
		# do not remember why I need ProofInfo in this section.
		query = "INSERT INTO "+table_name+ """ (FirstName,LastName,RIN,Email,ProofNum,ProofInfo) 
												VALUE (%s,%s,%s,%s,%s,%s)"""
		self.cur.execute(query,info)
		self.conn.commit()

	# name is student name
	# info is all of the hw content of this student
	def add_student_hw(self,name,hw_name,info):
		query = "SELECT PersonID from Student WHERE FirstName = %s"

		# get the key of the student.
		self.cur.execute(query,[name])
		data = self.cur.fetchone()
		try:
			useless = self.cur.fetchall()
		except:
			pass
		# this is the table_name of the student which stores the hw.
		table_name = str(data[0])
		table_name = "student"+table_name
		try:
			# this is create new student personal table to store the code information.
			query = "CREATE TABLE "+table_name+	"""(CodeID int(11) NOT NULL AUTO_INCREMENT,
													CodeName varchar(255) NOT NULL,
													PRIMARY KEY (CodeID) )
												"""
			# print(table_name)
			self.cur.execute(query)
			self.conn.commit()
			# print(table_name)

			query_insert = "INSERT INTO "+table_name+" (CodeName) VALUES(%s)"
			self.cur.execute(query_insert,[hw8])
			self.conn.commit()

		except:
			# this is situation that students have their own table (which is normal 
			# case.) We need to check that whether they already have a row for hw or
			# the hw is new for them. 
			query = "SELECT CodeID from " + table_name + " WHERE CodeName = %s"
			self.cur.execute(query,[hw_name])
			data_flag = self.cur.fetchone()
			try:
				useless = self.cur.fetchall()
			except:
				pass
			if(data_flag==None):

				# a new row for his new table. And I will create one more table to 
				# store their code. 
				query_insert = "INSERT INTO "+table_name+" (CodeName) VALUES(%s)"
				self.cur.execute(query_insert,[hw_name])
				self.conn.commit()
				code_table = table_name + "_" +hw_name
				self.create_hw_table(code_table)
				# to add the data into the third table.
				self.add_hw_data(code_table,info)
			else:			
			#	this is the situation that the students already have the code 
			# 	#  table, I will add the data into the table directly.
				code_table = table_name + "_" + hw_name
				self.add_hw_data(code_table,info)



		# this part I will add the code_name into the personal table. 
		# first I will check whether the corresponding code is existing or not.

		# query = "SELECT CodeName from "+ "GengRuijie_table" + " WHERE CodeName = %s"
		# self.cur.execute(query,[hw_name])
		# check = self.cur.fetchone()
		# try:
		# 	useless = self.cur.fetchall()
		# except:
		# 	pass

		# query = "INSERT INTO "+table_name+" (CodeName) VALUES (%s) "
		# self.cur.execute(query,hw_name)
		# self.conn.commit()

	def delete(self,table_name):
		query = "DELETE from "+table_name
		self.cur.execute(query)
		self.conn.commit()

	def drop(self,table_name):
		query = "DROP TABLE " + table_name
		self.cur.execute(query)
		self.conn.commit()

	# it will return the ID of the student so that we can get the ID
	# of student in the database.
	def search_student(self,student_name):
		query="SELECT PersonID from Student WHERE FirstName = %s"		
		self.cur.execute(query,[student_name])
		id_ = self.cur.fetchall()
		if(len(id_)!=1):
			rin= input("Please entre the RIN of the student")
			query="SELECT PersonID from Student WHERE RIN = %s"		
			self.cur.execute(query,[rin])
			id_ = self.fetchone()
			useless = self.cur.fetchall()
			return id_[0][0]

		else:
			return id_[0][0]


	def read_code(self,name,code_name):
		id_ = self.search_student("Ruijie")
		table_name = "student"+str(id_)+"_" +code_name
		query = "SELECT * from " + table_name 
		self.cur.execute(query)
		code = self.cur.fetchall()
		print(code)

	def up_load_code(self,student_name,code_name,file_name):
		# file name is the file I will open to read the code.
		# the student name is the data I need to get the key of the 
		# student.
		# the code name is the the name of code written by user. I will store into the
		# specific table.

		# the variable part means we have several subproof. Every subproof, I will give
		# them same part number, so we can distinguish easily.
		part = 1
		info =[] # info is the data I will pass into other function to add into the table
		file = open(file_name)

		# name = search_student(student_name)
		# print(name)
		
		for line in file:
			# the first element in the info list is the part number of data. Since 
			# part number does not appear in the file directly. I need to use code
			# to calculate.
			info.clear()
			info = [str(part)]

			# several situations we will meet in reading file part.
			if(line == "proof\n"):
				continue
			elif (line=="\n"):
				continue
			# this is one subproof end sentence. So I will increase the part number.
			elif(line=="done\n"):
				part = part +1
				continue
			# this part I will handle the true data. 
			else:
				data = line.strip().split('\t')
				info = info+data

				self.add_student_hw(student_name,code_name,info)

	def down_load_file(self,student_name,code_table_name,file_name):
		id_ = self.search_student(student_name)
		f = open(file_name,"w+")

		# table_name_second = "student"+str(id_)
		# query = "select * from "+table_name_second
		# self.cur.execute(query)
		# hw = self.cur.fetchall()
		# print(hw)
		# for i in hw:
		# 	print(i)

		table_name = "student"+str(id_)+"_"+code_table_name
		query = "select * from "+table_name

		self.cur.execute(query)

		data = self.cur.fetchall()
		part_num = data[0][3]

		f.write("proof\n")
		for element in data:
			part_alias_num = element[2]
			if (part_alias_num != part_num):
				f.write("done\n\nproof\n")
				part_num =element[2]
			f.write("{:}\t{:16}\t{:18}\t{:}\n".format(element[1],element[3],element[4],element[5]))
		f.write("done")
		f.close()

	def show_student(self):
		query="SELECT * from Student"		
		self.cur.execute(query)
		students = self.cur.fetchall()
		for i in students:
			print(i[1])

	def show_homework(self,name):
		id_ = self.search_student(name)

		table_name = "student"+str(id_)
		query = "select * from "+table_name
		self.cur.execute(query)
		hw = self.cur.fetchall()
		# print(hw)
		for i in hw:
			print(i[1])	








		
























