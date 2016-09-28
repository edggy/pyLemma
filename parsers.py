import sentence

sf = sentence.sf

def prefixSentenceParser(string, symbols = None):
    '''
    Parses a sentence from its prefix form

    @param string - A string representation of a sentence
    @param symbols - A dict of symbols to use.  Valid keys are: 'variable', 'wff', 'openParen', 'closeParen', 'seperator'

    @return - A sentence parsed from the string
    '''

    if symbols is None:
        symbols = {}

    if 'variable' not in symbols:
        symbols['variable'] = '?'

    if 'wff' not in symbols:
        symbols['wff'] = '@'    

    if 'openParen' not in symbols:
        symbols['openParen'] = '('   

    if 'closeParen' not in symbols:
        symbols['closeParen'] = ')'
        
    if 'openOpParen' not in symbols:
        symbols['openOpParen'] = '['   
       
    if 'closeOpParen' not in symbols:
        symbols['closeOpParen'] = ']'    

    if 'seperator' not in symbols:
        symbols['seperator'] = ','
        
    if 'newVar' not in symbols:
        symbols['newVar'] = '$'


    def init(string):
        # ForAll[?x](...)
        #if symbols['openOpParen'] in string and symbols['openParen'] != symbols['openOpParen']:
            #newSymbols = dict(symbols)
            #newSymbols['openParen'] = symbols['openOpParen']
            #newSymbols['closeParen'] = symbols['closeOpParen']
            #newSymbols['openOpParen'] = symbols['openParen']
            #newSymbols['closeOpParen'] = symbols['closeParen']    
            #return prefixSentenceParser(string, newSymbols)
        
        # If the operator starts with the variableSymbol then make it a generic operator
        # @P
        if string.startswith(symbols['wff']):
            return sf.generateWff(string[len(symbols['wff']):], symbols['wff'])
        
        # ?x
        if string.startswith(symbols['variable']):
            return sf.generateVariable(string[len(symbols['variable']):], symbols['variable'])
        else:
            # Otherwise make it a literal
            return sf.generateLiteral(string)
        
    def findMatch(string, pos, endSymbol, direction = 1):
        depth = 1
        startSymbol = string[pos]
        while depth > 0:
            pos += direction
            if string[pos] == startSymbol:
                depth += 1
            elif string[pos] == endSymbol:
                depth -= 1
        return pos
            
    def splitArgs(string, symbols):
        # A                     -> ['A']
        # (A)                   -> ['A']
        # (not(A))              -> ['not', 'A']
        # not(A)                -> ['not', 'A']
        # and(A, B)             -> ['and', 'A', 'B']
        # and(not(A), B)        -> ['and', 'not(A)', 'B']
        # and(not(A), or(B, C)) -> ['and', 'not(A)', 'or(B, C)']
        # P[x]                  -> ['P', 'x']
        # P[s(x)]               -> ['P', 's(x)']
        # P[s(x, y)]            -> ['P', 's(x, y)']
        # ForAll(x, P(x))
        # ForAll(x, P(s(x)))
        # ForAll(x, P[x])
        # ForAll(x, P[s(x)])
        # ForAll(x, P(x, a))
        # ForAll(x, P(x, A(a)))
        # ForAll(x, P(x, A(a, b)))
        
        # Remove whitespace
        string = "".join(string.split())
        
        # Find the first paren
        firstP = string.find(symbols['openParen'])
        firstOpP = string.find(symbols['openOpParen'])
        
        # Find the matching paren
        try:
            otherP = findMatch(string, firstP, symbols['closeParen'])
        except IndexError:
            otherP = -1
            
        try:
            otherOpP = findMatch(string, firstOpP, symbols['closeOpParen']) 
        except IndexError:
            otherOpP = -1        
        
        result = []
        oper = False
        
        if firstOpP < 0 or (firstP < firstOpP and firstP >= 0):
            # A                     -> ['A']
            # (A)                   -> ['A']
            # (not(A))              -> ['not', 'A']
            # not(A)                -> ['not', 'A']
            # and(A, B)             -> ['and', 'A', 'B']
            # and(not(A), B)        -> ['and', 'not(A)', 'B']
            # and(not(A), or(B, C)) -> ['and', 'not(A)', 'or(B, C)']    
            # |-(@P[?a], @P[s(?a)])
            # ForAll(x, P(x))
            # ForAll(x, P(s(x)))
            # ForAll(x, P[x])
            # ForAll(x, P[s(x)])
            # ForAll(x, P(x, a))
            # ForAll(x, P(x, A(a)))
            # ForAll(x, P(x, A(a, b)))            
            
            if firstP < 0:
                # A                     -> ['A']
                return string, [], '', oper
            
            elif firstP == 0:
                # (A)                   -> ['A']
                # (not(A))              -> ['not', 'A']
                
                return splitArgs(string[1:-1], symbols)
            else:
                # not(A)                -> ['not', 'A']
                # and(A, B)             -> ['and', 'A', 'B']
                # and(not(A), B)        -> ['and', 'not(A)', 'B']
                # and(not(A), or(B, C)) -> ['and', 'not(A)', 'or(B, C)']   
                # ForAll(x, P(x))       -> ['ForAll', 'x', 'P(x)']
                # ForAll(x, P(s(x)))
                # ForAll(x, P[x])
                # ForAll(x, P[s(x)])
                # ForAll(x, P(x, a))
                # ForAll(x, P(x, A(a)))
                # ForAll(x, P(x, A(a, b)))     
                # |-(@P[?a], @P[s(?a)])
                
                
                # take the operator and its parens out of the string, anything after the last paren is extra
                opStr, string, extra = string[:firstP], string[firstP + 1:otherP], string[otherP + 1:]
        else:
            # P[x]                  -> ['P', 'x']
            # P[s(x)]               -> ['P', 's(x)']
            # P[s(x, y)]            -> ['P', 's(x, y)']
            
            
            #if otherOpP < firstP:
                # ForAll(x, P(x))       -> ['ForAll', 'P(x)']
                # ForAll(x, P(s(x)))
                # ForAll(x, P[x])
                # ForAll(x, P[s(x)])
                # ForAll(x, P(x, a))
                # ForAll(x, P(x, A(a)))
                # ForAll(x, P(x, A(a, b)))
                # ForAll[x](P(x, A(a, b)))   
            #    opStr, string, extra = string[:firstP], string[firstP + 1:otherP], string[otherP + 1:]
                
            #else:
                # P[x]                  -> ['P', 'x']
                # P[Q[x]]               -> ['P', 'Q[x]']
                # P[s(x)]               -> ['P', 's(x)']
                # P[s(x, y)]            -> ['P', 's(x, y)']                
            opStr, string, extra = string[:firstOpP], string[firstOpP + 1:otherOpP], string[otherOpP + 1:]
            oper = True
                
        curStr = ''
        for tok in string.split(','):
            curStr += tok
            parenCount = curStr.count(symbols['openParen']) - curStr.count(symbols['closeParen']) + \
                curStr.count(symbols['openOpParen']) - curStr.count(symbols['closeOpParen'])
            
            if parenCount == 0:
                result.append(curStr)
                curStr = ''
            else:
                curStr += ','
                
        return opStr, result, extra, oper
            

    # Remove all the whitespace in the string
    string = "".join(string.split())

    # Count the difference in the number of open and close parenthesis
    parenCount = string.count(symbols['openParen']) - string.count(symbols['closeParen'])
    parenOpCount = string.count(symbols['openOpParen']) - string.count(symbols['closeOpParen'])

    # raise error if they are unequal
    if parenCount > 0:
        raise sentence.InvalidSentenceError('Unmatched Close Parenthesis' + symbols['closeParen'])
    elif parenCount < 0:
        raise sentence.InvalidSentenceError(symbols['openParen'] + 'Unmatched Open Parenthesis')
    elif parenOpCount > 0:
        raise sentence.InvalidSentenceError('Unmatched Close Parenthesis' + symbols['closeOpParen'])
    elif parenOpCount < 0:
        raise sentence.InvalidSentenceError(symbols['openOpParen'] + 'Unmatched Open Parenthesis')        
    
    opStr, argStr, extra, oper = splitArgs(string, symbols)
    
    data = dict(symbols)
    data['extra'] = {}
    
    if extra.startswith(symbols['newVar']):
        data['extra']['newVars'] = [prefixSentenceParser(s) for s in extra.split(symbols['newVar'])[1:]]
    
    if oper:
        
        data['openParen'] = symbols['openOpParen']
        data['closeParen'] = symbols['closeOpParen']   
        
        op = prefixSentenceParser(opStr, data)
        args = [prefixSentenceParser(arg, symbols) for arg in argStr]  
        return sf.generateOperator(op, args, data)
    
    if len(argStr) == 0:
        return init(opStr)
        
    op = prefixSentenceParser(opStr, data)
    try:
        op = sf.generateSentence(op[0], op[1:])
    except IndexError:
        pass
    args = [prefixSentenceParser(arg, symbols) for arg in argStr]      
    return sf.generateSentence(op, args, data) 

'''
    # find the first open paren
    firstP = string.find(symbols['openParen'])
    firstOpP = string.find(symbols['openOpParen'])

    if firstP < 0:
        # if there is no open paren, then this is a variable or an operator
        # 'A'
        # 'A[?x]'
        # 'A[P[?x]]'
        if firstOpP >= 0 in string:
            newSymbols = dict(symbols)
            newSymbols['openParen'] = symbols['openOpParen']
            newSymbols['closeParen'] = symbols['closeOpParen']
            #newSymbols['openOpParen'] = symbols['openParen']
            #newSymbols['closeOpParen'] = symbols['closeParen']            
            sen = prefixSentenceParser(string, newSymbols)      
            return sf.generateOperator(sen[0], sen[1:], newSymbols)
        
        return init(string)

    elif firstP == 0:
        # At least one paren, and the string starts with '(...'
        # '(A)'
        # '(A, B)'
        # '(A[?x])'
        # '(A, B[?x])'
        
        # Count the commas
        commaCount = string.count(',')
        if commaCount == 0:
            # if the open paren is the first character and there are no commas, then this is a sentence surrounded by parens
            # '(A)'

            # Re-parse without the parens
            return prefixSentenceParser(string[1:-1], symbols)

        # If there are commas, then it is a sentence with no operator
        # (A, B)
        op = init('')
    else:
        # At least one paren, and the string starts with '?(...'
        # 'P(A)'
        # 'P(A, B)'
        # 'P(A[x])'
        # 'P[A(x)]'
        # 'P[A(x, y)]'
        
        if firstP < firstOpP:
            # 'P(A)'
            # 'P(A, B)'
            # 'P(A[x])'            

            # the operator is everthing before the first open paren
            opStr = string[:firstP]
            
        else:
            # 'P[A(x)]'
            # 'P[A(x, y)]'            
            opStr = string[:firstP]
            
        # Parse the operator
        op = init(opStr)        
            
    # Find the last close paren
    lastP = string.rfind(symbols['closeParen'])

    # take the operator and its parens out of the string, anything after the last paren is ignored
    string, extra = string[firstP+1:lastP], string[lastP + 1:]

    # Split the arguments into tokens
    tokens = string.split(',')

    if len(tokens) == 1:
        # No commas, one argument
        # e.g. 'not(A)'
        var = prefixSentenceParser(string)
        data = dict(symbols)
        data['extra'] = extra        
        return sf.generateSentence(op, (var,), data)

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
        openCount += part.count(symbols['openParen'])
        openCount -= part.count(symbols['closeParen'])

        # If all the parens match up, then it must be a whole argument
        if openCount == 0:
            # recursively parse the argument
            args.append(prefixSentenceParser(cumStr))

            # reset cumStr to take care of the next part
            cumStr = ''

    data = dict(symbols)
    data['extra'] = extra
    res = sf.generateSentence(op, args, data)
    return res
    '''

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

    def include(string, data):
        toks = string.split(data['split'])
        toks = filter(None, toks)
    
        keepLines = None
        if len(toks) > 2:
            keepLines = set([])
            subToks = [s.strip() for s in toks[2].split(data['subSplit'])]
            for num in subToks:
                if data['range'] in num:
                    start, end = [int(s.strip()) for s in num.split(data['range'])]
                    for i in range(start, end + 1):
                        keepLines.add(i)
                else:
                    keepLines.add(int(num))
    
        if len(toks) > 1:
            # Get the filename to include
            filename = os.path.normpath(os.path.expandvars(toks[1].strip()))
        else:
            filename = os.path.normpath(os.path.expandvars(string[len(data['include']):].strip()))
    
        # Check if it is a relative path, if it is get the absolute path
        if not os.path.isabs(filename):
            filename = os.path.join(data['path'], filename)
    
        # Check to see that we have not already included this file
        if filename not in data['imported'] or keepLines is not None:
            with open(filename) as f:
                # Add all the new lines to the beginning of the queue
                # e.g. q = [o1,o2,o3,o4] file = '1\n2\n3\n4\n5 -> [1,2,3,4,5,o1,o2,o3,o4]
                lines = f.read().split('\n')
                for n, line in enumerate(reversed(lines)):
                    lineNum = len(lines) - n
                    if keepLines is None or lineNum in keepLines:
                        data['queue'].appendleft((line, lineNum, filename))
    
            # Add as an included file
            data['imported'].add(filename)        
    
    # The function to use by default
    def init(string, data):
        '''
        @param string - The current line of the proof as a string
        @param data - The data of parsing the previous lines
        '''
        # The initial state

        if string.startswith(data['assign']):
            toks = string.split(data['split'])
            toks = filter(None, toks)
            if len(toks) >= 3:
                data[toks[1]] = toks[2]
            
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

        # Remove empty strings, this is used to allow multiple tabs between entries
        toks = filter(None, toks)

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
    data = {'queue':linequeue, 'proofs':{}, 'infs':{'Assumption':defaultInferenceParser('Assumption\n@A')}, 
            'state': None, 'include':'include', 'assign':'set', 'split':'\t', 'subSplit':',', 'path':path, 'imported':set([filename]), 'proofDone': 'done', 
            'infDone': 'done', 'proofSplit': '\t', 'supportSplit': ',', 'comment': '#', 'range':'-'}

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
                # Check to see if this is an 'include' statement
                if line.startswith(data['include']):
                    include(line, data)
                else:
                    # Run the function corrosponding to the state of the FSM
                    fsm[data['state']](line, data)

        except (sentence.InvalidSentenceError, LineError) as e:
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

if __name__ == '__main__':

    formatStr = '%-40sExpected:  %s'
    
    sen1 = prefixSentenceParser('A')
    sen2a = prefixSentenceParser('?B')
    sen2b = prefixSentenceParser('@C')

    print formatStr % (sen1, 'A')
    print formatStr % (sen2a, '?B')
    print formatStr % (sen2b, '@C')

    print formatStr % (sen1.mapInto(sen2a), '[]')
    print formatStr % (sen1.mapInto(sen2b), '[]')
    print formatStr % (sen2a.mapInto(sen1), '[{?B:A}]')
    print formatStr % (sen2a.mapInto(sen2b), '[]')
    print formatStr % (sen2b.mapInto(sen1), '[{@C:A}]')
    print formatStr % (sen2b.mapInto(sen2a), '[{@C:?B}]')    

    sen3 = prefixSentenceParser('not(@A)')
    sen4 = prefixSentenceParser('not(or(A,not(A)))')

    print formatStr % (sen3, 'not(@A)')
    print formatStr % (sen4, 'not(or(A,not(A)))')
    print formatStr % (sen4.generalize(), 'not(or(@A,not(@A)))')

    print formatStr % (sen3.mapInto(sen4), '[{not: not, @A: or(A,not(A))}]')
    print formatStr % (sen4.mapInto(sen3), '[]') 

    sen5 = prefixSentenceParser('not(not(@A))')

    print formatStr % (sen5, 'not(not(@A))')

    sen6 = prefixSentenceParser('=(+(?x, ?y), ?x)')

    sen7 = prefixSentenceParser('=(+(?a, ?b), ?a)')

    print sen6 < sen7, sen6 <= sen7, sen6 == sen7, sen6 >= sen7, sen6 > sen7
    print sen7 < sen6, sen7 <= sen6, sen7 == sen6, sen7 >= sen6, sen7 > sen6

    import sentence2 as sentence

    def normalize(sen, data):
        if 'index' not in data:
            data['index'] = 0
            data['map'] = {}

        if isinstance(sen, sentence.Variable) and not isinstance(sen, sentence.Literal):
            if sen not in data['map']:
                newSen = sf.generateVariable(chr(data['index'] + ord('a')))
                data['index'] += 1
                data['map'][sen] = newSen
            return data['map'][sen]
            
        return sen


    print sen6.applyFunction(normalize)

    def subsitute(sen, data):
        if sen in data:
            return data[sen]
        return sen

    print sen7.applyFunction(subsitute, {prefixSentenceParser('?a'):prefixSentenceParser('*(2,3)')})

    emptySen = prefixSentenceParser('')

    print emptySen, emptySen.op(), emptySen.arity()

    emptyArg = prefixSentenceParser('|-(,A)')

    print "'%r', '%r', '%r'" % (emptyArg, emptyArg[0], emptyArg[1])

    sen8 = prefixSentenceParser('ForAll[?x](?P[?x])')

    sen9 = prefixSentenceParser('ForAll[x](if(A(x),B(x)))')

    print sen8, prefixSentenceParser('?x') in sen8
    print sen8[1].subsitute({prefixSentenceParser('?x'):prefixSentenceParser('a')})

    print sen8 < sen9

    def cornner(sen, data):
        data['str'] += '<' + str(sen) + '>'
        return sen

    data = {'str':''}
    sen8.applyFunction(cornner, data)
    print data['str']
    
    sen10 = prefixSentenceParser('@P[s(@x)]')
    
    print sen10
