# Lemma
PROOF SUPPORT SYSTEMS
---------------------

LEMMA is comprised of several components:

**A proof verifier:**
>	Input:	a proof file, a setting file, and an inferences file.

>	Output:	boolean value to whether the proof is valid or not. May include info on where the error occurs.

**A lemma maker:**
>	Input:	a valid proof file, a setting file, and an inferences file.

>	Output:	a lemma file which is an abbreviated proof file without all the data of the proof.

**A proof transformer:**
>	Input:	2 setting files and a proof or inferences file.

>	Output:	the proof or inferences file converted from the first setting file to the second.

**An autograder:**
>	This will enable students to submit files online and if they are valid notify the professor that they completed the assignment.
>
>	_Student:_
>>		Input:	a proof file, a setting file, and an inferences file.
>>		Output:	a boolean value to whether the proof is verified and credit has been given.

>	_Instructor:_
>>		Output:	a list of students and for each student what assignment have been attempted or completed and the time of submission for each.
