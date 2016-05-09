#import proof

import util
import sys

import os.path
#"Examples\Excluded Middle.prf"
filename = ''
if len(sys.argv) > 1:
	filename = sys.argv[1]

if not os.path.isfile(filename):
	# python -m pip install easygui
	try:
		import easygui
		filename = easygui.fileopenbox()
	except ImportError, e:
		print 'Install easygui for a file selcct dialog box or add a command line argument for the file you want to check'



try:
	# parse the supplied file
	tstPrf = util.defaultProofParser(filename)
	
	# Set the line numbering to start at 1 (instead of the default 0)
	[tstPrf[i].setNumbering(lambda x: x+1) for i in tstPrf]
	
	for proof in tstPrf:
		# Print each proof that was parsed
		print tstPrf[proof]
		
		# Check that it is valid
		valid = tstPrf[proof].verify()
		if valid:
			# If it is valid, print it
			print 'Valid'
		else:
			# If it is not valid, print the line number of the error
			print 'Invalid:\tError on line %d' % valid	
			print
			
except util.LineError as e:
	print e.message
