import sys
import os.path

import parsers

filename = ''
if len(sys.argv) > 1:
    filename = sys.argv[1]

done = False
if len(sys.argv) > 2 and sys.argv[2].lower() == 'nooutput':
    done = True


# Check if we have a valid file
if not os.path.isfile(filename):
    # Try to open a file select box
    try:
        import tkinter as tk
        if six.PY2:
            import tkFileDialog
            
            root = tk.Tk()
            root.withdraw()            
            filename = tkFileDialog.askopenfilename()
        elif six.PY3:
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            filename = filedialog.askopenfilename()            
            
    except ImportError, e:
        print('Invalid file')



try:
    # parse the supplied file
    tstPrf = parsers.defaultProofParser(filename)

    # Set the line numbering to start at 1 (instead of the default 0)
    [tstPrf[i].setNumbering(lambda x: x+1) for i in tstPrf]

    validTracker = set([])
    for proof in tstPrf:
        # Print each proof that was parsed
        print tstPrf[proof]

        # Check that it is valid
        valid = tstPrf[proof].verify()
        if valid is True:
            validTracker.add(proof)
            # If it is valid, print it
            print 'Valid\n--------------------------\n'
        else:
            # If it is not valid, print the line number of the error
            print 'Invalid:\tError on line %d' % valid
            print '--------------------------\n'

    print '%s of %s are Valid'  % (len(validTracker), len(tstPrf))
    
    prfNamesSorted = [i for i in tstPrf]
    prfNamesSorted.sort()
    for proofName in prfNamesSorted:
        #Print the name of each proof that was parsed
        print '%-50s%s' % (proofName, proofName in validTracker)

    while not done:
        # Get the name of the proof to check
        proofName = raw_input('Which proof would you like to print?  (type done to exit) ')

        # Check to see if we should quit
        if proofName.lower() in ['done', 'q', 'quit', 'exit', '']:
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

except (parsers.LineError, IOError) as e:
    print e
