def prefixSentencePrinter(sen, symbols = None):
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

    try:
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
            string += prefixSentencePrinter(arg) + symbols['seperator']

        # Remove the extra comma
        string = string[:-1]

        # Followed by a close paren
        string += symbols['closeParen']

        return string

    except AttributeError:
        return str(sen)

def infixSentencePrinter(sen):
    '''
    A printer that prints a sentence in infix notation

    @param sen - The sentence to print
    @return - The infix representation of this string
    '''
    string = ''

    # Check that the arity is 2, if so print it with the operator in the middle
    if sen.arity() == 2:
        return '(' + str(sen[0]) + ' ' + str(sen.op()) + ' ' + str(sen[1]) + ')'

    # Otherwise print it normally
    return prefixSentencePrinter(sen)

def defaultProofPrinter(p, printedInferences = None):
    '''
    A printer that takes a proof and prints it in a easy to read, easy to parse format with all the inference ruled used

    @param p - The  proof to be printed
    @param printedInferences - A set of inference rules, used to ensure the same rule is not printed twice 
    '''

    # Start with an empty string
    res = ''
    if printedInferences is None:
        printedInferences = set([])

    inferences = p.getInferences()
    for inf in inferences:
        # For each inference check if we printed it alredy
        if inf not in printedInferences:
            # If it is new, print it and add it to the set
            res += str(inferences[inf]) + '\n\n'
            printedInferences.add(inf)

    # Print the word 'proof' to start the proof, and the name of the proof on the next line
    res += 'proof\n' + p.name + '\n'
    for n, i in enumerate(p):
        # For each line in the proof, set the line number to its appropriate number and add it on a new line
        i._num = n
        res += str(i) + '\n'

    # Add 'done' to the last line
    return res + 'done'

def defaultInferencePrinter(inf):
    '''
    A printer that takes an inference and prints it in a easy to read, easy to parse format

    Note:
    defaultInferenceParser(defaultInferencePrinter(inf)) == inf should be true
    defaultInferencePrinter(defaultInferenceParser(string)) == string may be true

    @param inf - The inference rule to print
    @return - The string reprentation of the inference rule
    '''

    # Start with the word 'inference' on the first line and the name on the second
    res = 'inference\n%s\n' % inf.name

    # For each line in the inference, add it on a new line
    for line in inf:
        res += str(line) + '\n'

    # Add 'done' to the last line
    return res + 'done'
