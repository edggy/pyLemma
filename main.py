import sys
import os.path

import parsers

filename = ''
if len(sys.argv) > 1:
    filename = sys.argv[1]

# Check if we have a valid file
if not os.path.isfile(filename):
    # python -m pip install easygui
    try:
        import easygui
        filename = easygui.fileopenbox()
    except ImportError, e:
        print 'Usage %s [filename]'
        print 'Install easygui for a file selcct dialog box or add a command line argument for the file you want to check'
        print 'The pip command is "python -m pip install easygui"'



try:
    # parse the supplied file
    tstPrf = parsers.defaultProofParser(filename)

    # Set the line numbering to start at 1 (instead of the default 0)
    [tstPrf[i].setNumbering(lambda x: x+1) for i in tstPrf]

    for proof in tstPrf:
        # Print each proof that was parsed
        print tstPrf[proof]

        # Check that it is valid
        valid = tstPrf[proof].verify()
        if valid is True:
            # If it is valid, print it
            print 'Valid\n--------------------------\n'
        else:
            # If it is not valid, print the line number of the error
            print 'Invalid:\tError on line %d' % valid
            print '--------------------------\n'

    for proofName in tstPrf:
        #Print the name of each proof that was parsed
        print proofName	

    done = False
    while not done:
        # Get the name of the proof to check
        proofName = raw_input('Which proof would you like to print?  (type done to exit) ')

        # Check to see if we should quit
        if proofName.lower() in ['done', 'q', 'quit', 'exit']:
            break


        elif proofName in tstPrf:
            print tstPrf[proofName]
            # Check that it is valid
            valid = tstPrf[proofName].verify()
            if valid is True:
                # If it is valid, print it
                print 'Valid\n--------------------------\n'
            else:
                # If it is not valid, print the line number of the error
                print 'Invalid:\tError on line %d\n' % valid		

        else:
            print 'A proof with the name %s does not exist\n' % proofName

except parsers.LineError as e:
    print e.message
