import sys
import os.path

import parsers
import printers

# Python 3 compatibility
#import six
#from builtins import input

def isProofValid(filenameOrString):
    try:
        tstPrf = parsers.defaultProofParser(filenameOrString)
        
        for proof in tstPrf:
            # Check that it is valid
            if tstPrf[proof].verify() is not True:
                # There is an error
                return False
        return True
    except (parsers.LineError, IOError) as e:
        return False   

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
    except ImportError:
        import Tkinter as tk
        
    try:
        import tkFileDialog as tfd
    except ImportError:
        from tkinter import filedialog as tfd
        
    root = tk.Tk()
    root.withdraw()
    filename = tfd.askopenfilename()       
        
    '''try:
        
        import tkFileDialog
        
        root = tk.Tk()
        root.withdraw()            
        filename = tkFileDialog.askopenfilename()
    except ImportError:    
        try:
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            filename = filedialog.askopenfilename()            
                
        except ImportError:
            print('Invalid file')
'''


try:
    
    printProof = lambda x: printers.defaultProofPrinter(x, sentencePrinter = printers.prefixSentencePrinter)
    
    #syntax = {'+': '({0} + {1})','*': '({0}*{1})', 'Div':'{0} divides {1}', 's':'s{0}', 'Prime':'{0} is prime', '<':'({0} < {1})'}
    #printProof = lambda x: printers.englishProofPrinter(x, howToPrint=syntax)
    
    #printProof = lambda x: printers.compressedProofPrinter(x, sentencePrinter = printers.prefixSentencePrinter)
    
    # parse the supplied file
    tstPrf = parsers.defaultProofParser(filename)

    # Set the line numbering to start at 1 (instead of the default 0)
    [tstPrf[i].setNumbering(lambda x: x+1) for i in tstPrf]

    validTracker = set([])
    for proof in tstPrf:
        # Print each proof that was parsed

        print printProof(tstPrf[proof])

        # Check that it is valid
        valid = tstPrf[proof].verify()
        if valid is True:
            validTracker.add(proof)
            # If it is valid, print it
            print('Valid\n--------------------------\n')
        else:
            # If it is not valid, print the line number of the error
            print('Invalid:\tError on line %d' % valid)
            print('--------------------------\n')

    print('%s of %s are Valid'  % (len(validTracker), len(tstPrf)))
    
    prfNamesSorted = [i for i in tstPrf]
    prfNamesSorted.sort()
    for proofName in prfNamesSorted:
        #Print the name of each proof that was parsed
        print('%-70s%s' % (proofName, proofName in validTracker))

    while not done:
        # Get the name of the proof to check
        proofName = raw_input('Which proof would you like to print?  (type done to exit) ')

        # Check to see if we should quit
        if proofName.lower() in ['done', 'q', 'quit', 'exit', '']:
            break


        elif proofName in tstPrf:
            #print(tstPrf[proofName])
            print printProof(tstPrf[proof])
            # Check that it is valid
            valid = tstPrf[proofName].verify()
            if valid is True:
                # If it is valid, print it
                print('Valid\n--------------------------\n')
            else:
                # If it is not valid, print the line number of the error
                print('Invalid:\tError on line %d\n' % valid)	

        else:
            print('A proof with the name %s does not exist\n' % proofName)

except (parsers.LineError, IOError) as e:
    print(e)
