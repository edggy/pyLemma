def prefixSentenceParser(string, variable = True):
    '''
    Parses a sentence from its prefix form

    @param string - A string representation of a sentence
    @param variable - Should we treat base components as variables (True) or literals (False)

    @return - A sentence parsed from the string
    '''
    from sentence import Sentence
    from sentence import Variable
    from sentence import Literal
    from sentence import InvalidSentenceError

    variableSymbol = '@'

    if variable:
        init = Variable
    else:
        init = Literal

    # Remove all the whitespace in the string
    string = "".join(string.split())

    # Count the difference in the number of open and close parenthesis
    parenCount = string.count('(') - string.count(')')

    # raise error if they are unequal
    if parenCount > 0:
        raise InvalidSentenceError('Unmatched Close Parenthesis')
    elif parenCount < 0:
        raise InvalidSentenceError('Unmatched Open Parenthesis')

    # find the first open paren
    firstP = string.find('(')

    if firstP < 0:
        # if there is no open paren, then this is a variable
        # 'A'
        return init(string)

    elif firstP == 0:
        # Count the commas
        commaCount = string.count(',')
        if commaCount == 0:
            # if the open paren is the first character, then this is also a variable surrounded by parens
            # '(A)'

            return init(string[1:-1])

        # If there are commas, then it is a sentence with no operator
        op = None
    else:
        # the operator is everthing before the first open paren
        opStr = string[:firstP]

        # If the operator starts with the variableSymbol then make it a generic operator
        if opStr.startswith(variableSymbol):
            op = Variable(opStr[len(variableSymbol):])
        else:
            # Otherwise make it a literal
            op = Literal(opStr)

    # Find the last close paren
    lastP = string.rfind(')')

    # take the operator and its parens out of the string, anything after the last paren is ignored
    string = string[firstP+1:lastP]

    # Split the arguments into tokens
    tokens = string.split(',')

    if len(tokens) == 1:
        # No commas, one argument
        var = init(string)
        return Sentence(op, var)

    # list of the arguments as sentences or variables
    args = []

    # the number of open paren that haven't been closed
    openCount = 0

    cumStr = ''
    for part in tokens:
        # Check if this is the beginning of an argument
        if len(cumStr) == 0:
            # If it is add it to the end
            cumStr += part
        else:
            # Otherwise seperate it with a comma and then add it
            cumStr += ',' + part

        # Count the number of unclosed parens
        openCount += part.count('(')
        openCount -= part.count(')')

        # If all the parens match up, then it must be a whole argument
        if openCount == 0:
            # recursively parse the argument
            args.append(prefixSentenceParser(cumStr))

            # reset cumStr to take care of the next part
            cumStr = ''

    res = Sentence(op, *args)
    return res

def defaultInferenceParser(string, sentenceParser = None):
    '''
    Parses an inference into an Inference object

    @param string - A string representation of an inference rule
    @param sentenceParser - A function that parses the sentences in the inference rule (Defaults to prefixSentenceParser)

    @return - An inference parsed from the string
    '''

    if sentenceParser is None:
        sentenceParser = prefixSentenceParser

    from inference import Inference

    # Split the sting into lines
    lines = string.split('\n')

    # Strip all the lines
    lines = map(lambda a: a.strip(), lines)

    # Remove all blank lines
    lines = filter(lambda a: not len(a) == 0, lines)

    # The name is the first line
    name = lines.pop(0)

    # The conclusion is the last line
    conclusion = sentenceParser(lines.pop())

    # Each other line is a sentence of the premises
    premises = [sentenceParser(i) for i in lines]

    return Inference(name, conclusion, premises)


def defaultProofParser(string, sentenceParser = None, inferenceParser = None):
    '''
    Takes a string or file and parses it into a proof

    @param string - The string to parse, file to use, or name of file to use
    @param sentenceParser - The parser to use to parse sentences.  Defaults to prefixSentenceParser
    @param inferenceParser - The parser to use to parse inferences.  Defaults to defaultInferenceParser
    @return - A dict of all the proofs parsed from the given input
    '''
    import os

    # Path is used as the currnt working directory for imports
    path = os.path.dirname(os.path.realpath(__file__))
    filename = None	

    # Try to open the string as if it was a file
    try:
        with open(string) as f:
            path = os.path.dirname(os.path.realpath(string))
            filename = os.path.join(path, string)
            string = f.read()


    except:
        # string is not a name of a file
        pass

    # Try to read a file if it is a file
    try:
        string = string.read()
        path = os.path.dirname(os.path.realpath(string.name))
        filename = os.path.join(path, string.name)

    except:
        # string is not a file
        pass

    # Set the default parders
    if sentenceParser is None: sentenceParser = prefixSentenceParser
    if inferenceParser is None: inferenceParser = defaultInferenceParser

    # The function to use by default
    def init(string, data):
        '''
        @param string - The current line of the proof as a string
        @param data - The data of parsing the previous lines
        '''
        # The initial state

        # Check to see if this is an 'include' statement
        if string.startswith(data['include']):
            # Get the filename to include
            filename = os.path.normpath(string[len(data['include']):].strip())

            # Check if it is a relative path, if it is get the absolute path
            if not os.path.isabs(filename):
                filename = os.path.join(data['path'], filename)

            # Check to see that we have not already included this file
            if filename not in data['imported']:
                with open(filename) as f:
                    # Add all the new lines to the beginning of the queue
                    # e.g. q = [o1,o2,o3,o4] file = '1\n2\n3\n4\n5 -> [1,2,3,4,5,o1,o2,o3,o4]
                    for n, line in enumerate(reversed(f.read().split('\n'))):
                        data['queue'].appendleft((line, n, filename))

                # Add as an included file
                data['imported'].add(filename)

        else:	
            # Set the state to the line
            data['state'] = string.strip().lower()	

    # The function to use while parsing an inference rule
    def inf(string, data):
        '''
        @param string - The current line of the proof as a string
        @param data - The data of parsing the previous lines
        '''		
        # We are in the inference parsing state

        # Check to see if we are done
        if string == data['infDone']:
            # Use the data from the previous lines to parse the proof
            inf = inferenceParser(data['curInf'], sentenceParser)

            # Add it to the data
            data['infs'][inf.name] = inf

            # Reset 'curInf'
            data['curInf'] = None

            # Set state to default
            data['state'] = None
            return

        # Check to see if we are in the middle of an infrence rule
        if 'curInf' in data and data['curInf'] is not None:
            # Add to the current rule
            data['curInf'] += '\n' + string
        else:
            # Start a new inference rule
            data['curInf'] = string

    # The function to use while parsing a proof
    def prf(string, data):
        '''
        @param string - The current line of the proof as a string
        @param data - The data of parsing the previous lines
        '''		
        from proof import Proof

        # check if we are done
        if string == data['proofDone']:
            # Set state to default
            data['state'] = None

            # Reset the current proof
            data['curProof'] = None
            return			

        # Check to see if we are in the middle of a proof
        if 'curProof' not in data or data['curProof'] is None:
            # Start a new proof
            # Name is the first line
            name = string.strip()

            # Set the current proof to name
            data['curProof'] = name

            # Create a new proof with this name
            data['proofs'][name] = Proof(name)

            # Add it as an infrence rule too
            data['infs'][name] = data['proofs'][name]

            # Create a dict to store the lines
            data['curLines'] = {}
            return

        # Retrive the current proof
        curProof = data['proofs'][data['curProof']]

        # Retrieve the current lines
        lines = data['curLines']

        # Split the line into tokens
        toks = string.split(data['proofSplit'])

        # Strip all the parts
        toks = map(lambda a: a.strip(), toks)	

        # toks[0] = Line number, toks[1] = Sentence, toks[2] = Inference rule name, toks[3] = support step
        if len(toks) < 2:
            # There should be at least two parts
            raise LineError

        # Parse the sentence
        curSen = sentenceParser(toks[1])

        # Add the sentence to the proof
        curProof += curSen

        # Adds the line to the dict using the line number as the key
        lines[toks[0]] = curProof[-1]


        if len(toks) == 2:
            # If there are exactly two parts, then this line is an assumption
            curProof[-1] += data['infs']['Assumption']
        if len(toks) >= 3:
            # If there are at least 3 parts then the third part is the name of the inference rule to use
            try:
                curProof[-1] += data['infs'][toks[2]]
            except KeyError as e:
                raise LineError('%s is not a defined inference rule or proof' % e.message)		
        if len(toks) >= 4:
            # If there are at least 4 parts then the fourth part is a list of supporting lines
            try:
                for i in toks[3].split(data['supportSplit']):
                    # Add each support as supporting steps
                    curProof[-1] += lines[i.strip()]
            except KeyError as e:
                raise LineError('%s is not a line' % e.message)


    # Finite state machine states
    fsm = {None:init, '':init, 'inference':inf, 'proof':prf}

    from collections import deque

    # Create a queue for all of the lines to process
    # An element should be a 3-tuple of (string, line number, filename)
    linequeue = deque()

    # Add all of the lines from the given input
    for n, line in enumerate(string.split('\n')):
        linequeue.append((line, n, filename))

    # Create the data, used to keep track of the state of the fsm
    data = {'queue':linequeue, 'proofs':{}, 'infs':{'Assumption':defaultInferenceParser('Assumption\nA')}, 
            'state': None, 'include':'include', 'path':path, 'imported':set([filename]), 'proofDone': 'done', 
            'infDone': 'done', 'proofSplit': '\t', 'supportSplit': ',', 'comment': '#'}

    from sentence import InvalidSentenceError

    while len(data['queue']) > 0:
        # Grab the next line off of the queue
        line, n, filename = data['queue'].popleft()

        # Retrieve the current path
        data['path'] = os.path.dirname(os.path.realpath(filename))

        try:
            # Ignore everything after the comment symbol for commenting
            line = line.split(data['comment'])[0].strip()

            # Ignore the line if it is blank
            if len(line) != 0:

                # Run the function corrosponding to the state of the FSM
                fsm[data['state']](line, data)

        except (InvalidSentenceError, LineError) as e:
            # Raise an error to tell the user that there is a parsing error
            e.message = 'Error in "%s", line %d:\t%s' % (filename, n+1, e.message)
            raise LineError(e.message)

    # Return all the proofs parsed
    return data['proofs']

class LineError(Exception):
    '''
    An Exception on a specific line while parsing the proof
    '''
    pass

