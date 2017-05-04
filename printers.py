def prefixSentencePrinter(sen, symbols = None, sentencePrinter = None, isInfix = None):
    '''
    A printer that prints a sentence in prefix notation

    @param sen - The sentence to print
    @param symbols - A dict with symbols to use.  Valid keys are: 'seperator', 'openParen' and 'closeParen'
    @return - The prefix representation of this string
    '''	

    if symbols is None:
        symbols = {}

    if 'seperator' not in symbols:
        symbols['seperator'] = ','

    if 'openParen' not in symbols:
        symbols['openParen'] = '('

    if 'closeParen' not in symbols:
        symbols['closeParen'] = ')'  
    
    if sentencePrinter is None:
        sentencePrinter = prefixSentencePrinter

    # If the arity is 0, then just print the operator
    if sen.arity() == 0:
        return str(sen.op())

    # Otherwise, print the operator
    string = str(sen.op())

    # Followed by an open paren
    string += symbols['openParen']
    first = True

    # Then by its arguments
    for arg in sen.args():
        string += sentencePrinter(arg, symbols, sentencePrinter, isInfix) + symbols['seperator']

    # Remove the extra comma
    string = string[:-1]

    # Followed by a close paren
    string += symbols['closeParen']

    return string

def infixSentencePrinter(sen, symbols = None, sentencePrinter = None, isInfix = None):
    '''
    A printer that prints a sentence in infix notation

    @param sen - The sentence to print
    @return - The infix representation of this string
    '''
    
    if symbols is None:
        symbols = {}

    if 'seperator' not in symbols:
        symbols['seperator'] = ','

    if 'openParen' not in symbols:
        symbols['openParen'] = '('

    if 'closeParen' not in symbols:
        symbols['closeParen'] = ')'    
        
    if 'space' not in symbols:
        symbols['space'] = ' '  
        
    if sentencePrinter is None:
        sentencePrinter = infixSentencePrinter    

    if isInfix is None:
        printInfix = ['and', 'or', '+', '*', '=']
        isInfix = lambda sen: sen.arity() == 2 and (str(sen.op()) in printInfix)
    
    # Check that the arity is 2, if so print it with the operator in the middle
    if isInfix(sen):
        return symbols['openParen'] + sentencePrinter(sen[1], symbols, sentencePrinter, isInfix) + symbols['space'] + str(sen.op()) + symbols['space'] + infixSentencePrinter(sen[2], symbols, sentencePrinter, isInfix) + symbols['closeParen']

    # Otherwise print it normally
    return prefixSentencePrinter(sen, symbols, sentencePrinter)

def defaultLinePrinter(line, sentencePrinter = None, howToPrint = None):
    
    if sentencePrinter is None:
        sentencePrinter = prefixSentencePrinter
    
    # Obtain the support line numbers
    supportLines = [i()._num for i in line._support]

    # Arrange the support line numbers in some order
    supportLines.sort()

    # Get the numbering scheme from the proof
    numbering = line._proof()._numbering

    # get this line number from the numbering scheme
    lineNum = numbering(line._num)

    # start the result as the line number and a tab then the sentence
    ret = str(lineNum) + '\t' + sentencePrinter(line._sentence, None, sentencePrinter, howToPrint)

    if line._inference is not None:
        # If the inference is set then add it's name
        ret += '\t' + str(line._inference.name)
    else:
        # Otherwise add ??? to denote it has not been set
        ret += '\t' + '???'

    # Only add the supportLines if there are 1 or more
    if len(supportLines) > 0:
        ret += '\t'
        for supportLine in supportLines:
            # For each support number get its printed value via numbering
            ret += str(numbering(supportLine)) + ', '
        # Delete the last ', '
        ret = ret[:-2]

    return ret    

def defaultInferencePrinter(inf, sentencePrinter = None, howToPrint = None):
    '''
    A printer that takes an inference and prints it in a easy to read, easy to parse format

    Note:
    defaultInferenceParser(defaultInferencePrinter(inf)) == inf should be true
    defaultInferencePrinter(defaultInferenceParser(string)) == string may be true

    @param inf - The inference rule to print
    @return - The string reprentation of the inference rule
    '''
    
    if sentencePrinter is None:
        sentencePrinter = prefixSentencePrinter

    # Start with the word 'inference' on the first line and the name on the second
    res = 'inference\n%s\n' % inf.name

    # For each line in the inference, add it on a new line
    for line in inf:
            res += sentencePrinter(line, None, sentencePrinter, howToPrint) + '\n'

    # Add 'done' to the last line
    return res + 'done'

def defaultProofPrinter(p, printedInferences = None, inferencePrinter = None, linePrinter = None, sentencePrinter = None):
    '''
    A printer that takes a proof and prints it in a easy to read, easy to parse format with all the inference ruled used

    @param p - The  proof to be printed
    @param printedInferences - A set of inference rules, used to ensure the same rule is not printed twice 
    '''

    if inferencePrinter is None:
        inferencePrinter = defaultInferencePrinter
    if linePrinter is None:
        linePrinter = defaultLinePrinter
    if sentencePrinter is None:
        sentencePrinter = prefixSentencePrinter

    # Start with an empty string
    res = ''
    if printedInferences is None:
        printedInferences = set([])

    inferences = p.getInferences()
    for inf in inferences:
        # For each inference check if we printed it alredy
        if inf not in printedInferences:
            # If it is new, print it and add it to the set
            try:
                res += inferencePrinter(inferences[inf], sentencePrinter) + '\n\n'
            except AttributeError:
                res += defaultProofPrinter(inferences[inf], printedInferences, inferencePrinter, linePrinter, sentencePrinter) + '\n\n'
            printedInferences.add(inf)

    # Print the word 'proof' to start the proof, and the name of the proof on the next line
    res += 'proof\n' + p.name + '\n'
    for n, line in enumerate(p):
        # For each line in the proof, set the line number to its appropriate number and add it on a new line
        line._num = n
        res += linePrinter(line, sentencePrinter) + '\n'

    # Add 'done' to the last line
    return res + 'done'

def englishSentencePrinter(sen, symbols = None, sentencePrinter = None, howToPrint = None):
    '''
    A printer that prints a sentence in infix notation

    @param sen - The sentence to print
    @return - The infix representation of this string
    '''
    
    if symbols is None:
        symbols = {}

    if 'seperator' not in symbols:
        symbols['seperator'] = ','

    if 'openParen' not in symbols:
        symbols['openParen'] = '('

    if 'closeParen' not in symbols:
        symbols['closeParen'] = ')'    
        
    if 'space' not in symbols:
        symbols['space'] = ' '  
        
    if sentencePrinter is None:
        sentencePrinter = englishSentencePrinter    

    notation = {}
    if isinstance(howToPrint, dict):
        notation = howToPrint
        howToPrint = None
        
    if howToPrint is None:
        if 'and' not in notation:
            notation['and'] ='({0} and {1})'
        if 'or' not in notation:
            notation['or'] = '({0} or {1})'
        if 'not' not in notation:
            notation['not'] = 'not {0}'
        if 'if' not in notation:
            notation['if'] = 'if {0} then {1}'
        if 'iff' not in notation:
            notation['iff'] = '{0} if and only if {1}'
        if '=' not in notation:
            notation['='] = '({0} = {1})'
        if 'ForAll' not in notation:
            notation['ForAll'] = 'for all {0} we have that {1}'
        if 'Exists' not in notation:
            notation['Exists'] = 'there exists a {0} such that {1}'
        if '|-' not in notation:
            notation['|-'] = 'if we assume {0} then we get {1}'
        def howToPrint(sen):
            if sen.op() in notation:
                args = []
                for arg in sen.args():
                    args.append(sentencePrinter(arg, symbols, sentencePrinter, howToPrint))
                return notation[sen.op()].format(*args)
            return(prefixSentencePrinter(sen, symbols, sentencePrinter, howToPrint))
    
        
    
    return howToPrint(sen)

def englishLinePrinter(line, sentencePrinter = None, howToPrint = None):
    import random
    
    if sentencePrinter is None:
        sentencePrinter = prefixSentencePrinter
        
    if 'Assumption' not in howToPrint:
        assumptionsPhrases = ["Let's assume that", 'Assuming', 'Suppose that']
        howToPrint['Assumption'] = '{0}) %s {1}.\n' % assumptionsPhrases[0]
    
    # Obtain the support line numbers
    supportLines = [i()._num for i in line._support]

    # Arrange the support line numbers in some order
    supportLines.sort()

    # Get the numbering scheme from the proof
    numbering = line._proof()._numbering

    # get this line number from the numbering scheme
    lineNum = numbering(line._num)
    
    if line._inference.name in howToPrint:
        lineFormat = howToPrint[line._inference.name]
    else:
        nextPhrases = ['Next we get', 'Alas,', 'Therefore', 'Thus,', 'From this', 'So', 'Hence,', 'Next,']
        inferencePhrases = ['because of', 'from', 'due to']
        
        support = ''
        if len(supportLines) == 1:
            support = 'from line {3}'
        if len(supportLines) > 1:
            support = 'from lines {3}'
        
        lineFormat = '{0}) %s {1} %s {2} %s.\n' % (random.choice(nextPhrases), random.choice(inferencePhrases), support)


    sen = sentencePrinter(line._sentence, None, sentencePrinter, howToPrint)

    if line._inference is not None:
        # If the inference is set then add it's name
        inf = str(line._inference.name)
    else:
        # Otherwise add ??? to denote it has not been set
        inf = '???'

    support = ''
    # Only add the supportLines if there are 1 or more
    if len(supportLines) > 0:
        for supportLine in supportLines:
            # For each support number get its printed value via numbering
            support += str(numbering(supportLine)) + ', '
        # Delete the last ', '
        support = support[:-2]

    return lineFormat.format(lineNum, sen, inf, support)

def englishProofPrinter(p, printedInferences = None, inferencePrinter = None, linePrinter = None, sentencePrinter = None, howToPrint = None):
    '''
    A printer that takes a proof and prints it in a easy to read, easy to parse format with all the inference ruled used

    @param p - The  proof to be printed
    @param printedInferences - A set of inference rules, used to ensure the same rule is not printed twice 
    '''

    if inferencePrinter is None:
        inferencePrinter = defaultInferencePrinter
    if linePrinter is None:
        linePrinter = englishLinePrinter
    if sentencePrinter is None:
        sentencePrinter = englishSentencePrinter

    # Start with an empty string
    res = ''
    if printedInferences is None:
        printedInferences = set([])

    inferences = p.getInferences()
    for inf in inferences:
        # For each inference check if we printed it alredy
        if inf not in printedInferences:
            # If it is new, print it and add it to the set
            try:
                res += inferencePrinter(inferences[inf], sentencePrinter, howToPrint) + '\n\n'
            except AttributeError:
                res += englishProofPrinter(inferences[inf], printedInferences, inferencePrinter, linePrinter, sentencePrinter, howToPrint) + '\n\n'
            printedInferences.add(inf)

    # Print the word 'proof' to start the proof, and the name of the proof on the next line
    res += p.name + '\n'
    for n, line in enumerate(p):
        # For each line in the proof, set the line number to its appropriate number and add it on a new line
        line._num = n
        res += linePrinter(line, sentencePrinter, howToPrint)
    # Add 'QED' to the last line
    return res + 'QED'