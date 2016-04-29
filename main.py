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
	tstPrf = util.defaultProofParser(filename)
	#print tstPrf
	[tstPrf[i].setNumbering(lambda x: x+1) for i in tstPrf]
	for proof in tstPrf:
		print tstPrf[proof]
		valid = tstPrf[proof].verify()
		if valid > 0:
			print 'Valid'
		else:
			print 'Invalid:\tError on line %d' % -valid		
	#print tstPrf['Test Proof']
	#valid = tstPrf['Test Proof'].verify()
	#if valid > 0:
		#print 'Valid'
	#else:
		#print 'Invalid:\tError on line %d' % -valid
except Exception as e:
	print e.message

#for i in tstPrf:
	#print str(tstPrf[i].verify()) + ': ' + repr(tstPrf[i])
