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

def parseFlags(arguments):
    flags = {}
    for i, arg in enumerate(arguments):
        if arg[0] == '-' and arg[1] != '-':
            for f in arg[1:]:
                if i+1 < len(arguments):
                    flags[f] = arguments[i+1]
                else:
                    flags[f] = ''
    return flags
        
filename = ''
if len(sys.argv) > 1:
    filename = sys.argv[1]

done = False
if len(sys.argv) > 2 and sys.argv[2].lower() == 'nooutput':
    done = True

flags = parseFlags(sys.argv)

# Check if we have a valid file
if 'f' not in flags or not os.path.isfile(flags['f']):
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
    flags['f'] = tfd.askopenfilename()

try:
    prefix  = ['pre', 'prefix', 'p', '', 'default']
    infix   = ['in', 'infix', 'i']
    english = ['english', 'e', 'eng', 'hr', 'informal']
    latex   = ['latex', 'tex', 'l']
    
    for f in ['s', 'l', 'i', 'p']:
        if f not in flags:
            flags[f] = ''
    
    if flags['s'].lower() in prefix:
        senPrint = printers.prefixSentencePrinter
    elif flags['s'].lower() in infix:
        senPrint = printers.infixSentencePrinter
    elif flags['s'].lower() in english:
        senPrint = printers.englishSentencePrinter 
    elif flags['s'].lower() in latex:
        senPrint = printers.latexSentencePrinter
    else:
        senPrint = printers.prefixSentencePrinter    
    
    if flags['l'].lower() in english:
        linePrint = printers.englishLinePrinter
    elif flags['l'].lower() in latex:
        linePrint = printers.latexLinePrinter
    else:
        linePrint = printers.defaultLinePrinter
        
    if flags['i'].lower() in english:
        infPrint = printers.defaultInferencePrinter
    elif flags['i'].lower() in latex:
        infPrint = printers.latexInferencePrinter
    else:
        infPrint = printers.defaultInferencePrinter
    
    if flags['p'].lower() in english:
        syntax = {'+': '({0} + {1})','*': '({0}*{1})', 'Div':'{0} divides {1}', 's':'s{0}', 'Prime':'{0} is prime', '<':'({0} < {1})'}
        printProof = lambda x: printers.englishProofPrinter(x, howToPrint=syntax, inferencePrinter=infPrint, linePrinter=linePrint, sentencePrinter=senPrint)
    elif flags['p'].lower() in latex:
        syntax = {'+': '({0} + {1})','*': '({0} \cdot {1})', 'Div':'({0}|{1})', 's':'s({0})', 'Prime':'Prime({0})', '<':'({0} < {1})'}
        printProof = lambda x: printers.latexProofPrinter(x, howToPrint=syntax, inferencePrinter=infPrint, linePrinter=linePrint, sentencePrinter=senPrint, inline=False)        
    else:
        printProof = lambda x: printers.defaultProofPrinter(x, inferencePrinter=infPrint, linePrinter=linePrint, sentencePrinter=senPrint)
    
    #printProof = lambda x: printers.compressedProofPrinter(x, sentencePrinter = printers.prefixSentencePrinter)
    
    # parse the supplied file
    tstPrf = parsers.defaultProofParser(flags['f'])

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
    printValid = lambda x: 'Valid' if x else 'Invalid'
    for proofName in prfNamesSorted:
        #Print the name of each proof that was parsed
        print('%-70s%s' % (proofName, printValid(proofName in validTracker)))

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
