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
    if howToPrint is None:
        howToPrint = {}
        
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

def latexSentencePrinter(sen, symbols = None, sentencePrinter = None, howToPrint = None):
    # \pline[<Line ID>]{<Sentence>}[<Justification>]
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
        sentencePrinter = latexSentencePrinter 
        
    notation = {}
    if isinstance(howToPrint, dict):
        notation = howToPrint
        howToPrint = None
        
    if howToPrint is None:
        if 'and' not in notation:
            notation['and'] ='({0} \\land {1})'
        if 'or' not in notation:
            notation['or'] = '({0} \\lor {1})'
        if 'not' not in notation:
            notation['not'] = '\\lnot {0}'
        if 'if' not in notation:
            notation['if'] = '({0} \\lif {1})'
        if 'iff' not in notation:
            notation['iff'] = '({0} \\liff {1})'
        if '=' not in notation:
            notation['='] = '({0} = {1})'
        if 'ForAll' not in notation:
            notation['ForAll'] = '\\uni{{{0}}}{{{1}}}'
        if 'Exists' not in notation:
            notation['Exists'] = '\\exi{{{0}}}{{{1}}}'
        if '|-' not in notation:
            notation['|-'] = '{0} \\vdash {1}'
            # notation['|-'] = '\subproof{{{0}}}{{{1}}}'
        if 'Contradiction' not in notation:
            notation['Contradiction'] = '\\bot'
        def howToPrint(sen):
            if sen.op() in notation:
                args = []
                for arg in sen.args():
                    args.append(sentencePrinter(arg, symbols, sentencePrinter, howToPrint))
                return notation[sen.op()].format(*args)
            return(prefixSentencePrinter(sen, symbols, sentencePrinter, howToPrint))
        
    return howToPrint(sen)

def latexInferencePrinter(inf, sentencePrinter = None, howToPrint = None):
    proofStructure = '%s\\\\\n\\fitchprf{%s}{%s}'
    lineStructure = '\\pline{%s}\\\\\n'
    
    assumptions = ''
    deductions = ''    
    
    for sen in inf._premises:
        assumptions += lineStructure % sentencePrinter(sen, sentencePrinter = sentencePrinter, howToPrint = howToPrint)
    for sen in inf.getConclusion():
        deductions += lineStructure % sentencePrinter(sen, sentencePrinter = sentencePrinter, howToPrint = howToPrint)
    
    return proofStructure % (inf.name, assumptions[:-3], deductions[:-3])
    

def latexSubproofPrinter(p, printedInferences = None, inferencePrinter = None, linePrinter = None, sentencePrinter = None, howToPrint = None, linestart = 0, inline = False):
    structure = '\\subproof{{{0}}}{{{1}}}'
    if not inline:
        structure = '{2}\\\\\n\\fitchprf{{{0}}}{{{1}}}'
    assumptions = ''
    deductions = ''
    
    if not inline:
        inferenceList = []
        if printedInferences is None:
            printedInferences = set([])
    
        inferences = p.getInferences()
        for inf in inferences:
            # For each inference check if we printed it alredy
            if inf not in printedInferences:
                # If it is new, print it and add it to the set
                try:
                    inferenceList.append(inferencePrinter(inferences[inf], sentencePrinter, howToPrint))
                except AttributeError:
                    subproof = latexSubproofPrinter(inferences[inf], printedInferences, inferencePrinter, linePrinter, sentencePrinter, howToPrint, inline)
                    inferenceList.append(subproof)
                printedInferences.add(inf)    
    
    n = linestart
    for line in p:
        line._num = n
        line._data['length'] = 1
        if inline:
            try:
                line._data['length'] = line._inference.lengthr()
            except AttributeError:
                pass
        
        n += line._data['length']        
        
        lineStr = linePrinter(line, sentencePrinter, howToPrint, inline)  
        if line._inference.name == 'Assumption':
            assumptions += lineStr
        else:
            deductions += lineStr
            
    if not inline:
        inferencesString = ''
        for infStr in inferenceList:
            inferencesString += infStr + '\\\\\n\n'    
        return inferencesString + structure.format(assumptions[:-3], deductions[:-3], p.name)
    
    return structure.format(assumptions[:-3], deductions[:-3])
        
    
def printSupport(line, inline = False):
    # Obtain the support line numbers
    supportLines = [i() for i in line._support]

    # Arrange the support line numbers in some order
    supportLines.sort(key=lambda x: x._num)
    
    # Get the numbering scheme from the proof
    numbering = line._proof()._numbering    
    
    support = ''
    # Only add the supportLines if there are 1 or more
    if len(supportLines) > 0:
        for supportLine in supportLines:
            if not inline or supportLine._data['length'] == 1:
                # For each support number get its printed value via numbering
                support +=  '%s, ' % numbering(supportLine._num)
            else:
                support +=  '%s-%s, ' % (numbering(supportLine._num), numbering(supportLine._num + supportLine._data['length'] - 1))
        # Delete the last ', '
        support = support[:-2]
        
    return support
    

def latexLinePrinter(line, sentencePrinter = None, howToPrint = None, inline = False):
    # \pline[<Line ID>]{<Sentence>}[<Justification>]
    if sentencePrinter is None:
        sentencePrinter = latexSentencePrinter
    if howToPrint is None:
        howToPrint = {}
        
    if 'Assumption' not in howToPrint:
        howToPrint['Assumption'] = '\\pline[{0}]{{{1}}}'
    
    try:
        if not inline:
            raise AttributeError()
    
        # Assume this line is a subproof
        return latexSubproofPrinter(line._inference, linePrinter = latexLinePrinter, sentencePrinter = sentencePrinter, howToPrint = howToPrint, linestart = line._num, inline = inline) + '\n'
    
    except (AttributeError, TypeError):
        # This line is an inference rule
    
        # Get the numbering scheme from the proof
        #numbering = line._proof()._numbering
    
        # get this line number from the numbering scheme
        #lineNum = numbering(line._num)
        
        lineNum = '*'
        
        if line._inference.name in howToPrint:
            lineFormat = howToPrint[line._inference.name]
        else:
            lineFormat = '\\pline[{0}]{{{1}}}[{2}: {3}]'
    
    
        sen = sentencePrinter(line._sentence, None, sentencePrinter, howToPrint)
    
        if line._inference is not None:
            # If the inference is set then add it's name
            inf = str(line._inference.name)
            replacements = {'Contradiction Intro':'$\\bot$ Intro', 'Contradiction Elim':'$\\bot$ Elim',
                            'And Intro':'$\land$ Intro', 'And Elim Left':'$\land$ Elim', 'And Elim Right':'$\land$ Elim',
                            'Or Intro Left':'$\lor$ Intro', 'Or Intro Right':'$\lor$ Intro', 'Or Elim':'$\lor$ Elim',
                            'Not Intro':'$\lnot$ Intro', 'Not Elim':'$\lnot$ Elim',
                            'If Intro':'$\lif$ Intro', 'If Elim':'$\lif$ Elim',
                            'Iff Intro':'$\liff$ Intro', 'Iff Elim Left':'$\liff$ Elim', 'Iff Elim Right':'$\liff$ Elim',
                            'ForAll Intro':'$\lall$ Intro', 'ForAll Elim':'$\lall$ Elim',
                            'Exists Intro':'$\lis$ Intro', 'Exists Elim':'$\lis$ Elim'}
            if inf in replacements:
                inf = replacements[inf]
        else:
            # Otherwise add ??? to denote it has not been set
            inf = '???'
    
        support = printSupport(line, inline)
    
        return lineFormat.format(lineNum, sen, inf, support) + '\\\\\n'

def latexProofPrinter(p, printedInferences = None, inferencePrinter = None, linePrinter = None, sentencePrinter = None, howToPrint = None, inline = False):
    if inferencePrinter is None:
        inferencePrinter = latexInferencePrinter
    if linePrinter is None:
        linePrinter = latexLinePrinter
    if sentencePrinter is None:
        sentencePrinter = latexSentencePrinter
        
    if inline:
        structure = '''%%%s
\\documentclass[11pt]{article}
\\usepackage{lplfitch}
\\setlength{\\textheight}{9in} \\setlength{\\headheight}{.2in}
\\setlength{\\headsep}{0in} \\setlength{\\topmargin}{0in}
\\usepackage[margin=0.5in]{geometry}
\\setlength{\\fitchprfwidth}{5.5in}
\\begin{document}
\\fitchprf{%s}{%s}
\\end{document}
'''
    
        assumptions = ''
        deductions = ''
        
        n = 0
        
        for line in p:
            line._num = n
            line._data['length'] = 1
            try:
                line._data['length'] = line._inference.lengthr()
            except AttributeError:
                pass
            
            n += line._data['length']
            
            lineStr = linePrinter(line, sentencePrinter, howToPrint, inline)  
            if line._inference.name == 'Assumption':
                assumptions += lineStr
            else:
                deductions += lineStr
                
        latexString = (structure % (p.name, assumptions[:-3], deductions[:-3]))
        count = 0
        result = ''
        for n, char in enumerate(latexString):
            if char == '*':
                result += str(p._numbering(count))
                count += 1
            else:
                result += char
            
        return result

    else:
        structure = '''%%%s
\\documentclass[11pt]{article}
\\usepackage{lplfitch}
\\setlength{\\textheight}{9in} \\setlength{\\headheight}{.2in}
\\setlength{\\headsep}{0in} \\setlength{\\topmargin}{0in}
\\usepackage[margin=0.5in]{geometry}
\\setlength{\\fitchprfwidth}{4.5in}
\\begin{document}
%s
\\end{document}
'''
        proofStructure = '%s\\\\\n\\fitchprf{%s}{%s}'
        
        inferenceList = []
        if printedInferences is None:
            printedInferences = set([])
    
        inferences = p.getInferences()
        for inf in inferences:
            # For each inference check if we printed it alredy
            if inf not in printedInferences:
                # If it is new, print it and add it to the set
                try:
                    inferenceList.append(inferencePrinter(inferences[inf], sentencePrinter, howToPrint))
                except AttributeError:
                    subproof = latexSubproofPrinter(inferences[inf], printedInferences, inferencePrinter, linePrinter, sentencePrinter, howToPrint, inline)
                    inferenceList.append(subproof)
                printedInferences.add(inf)
    
        assumptions = ''
        deductions = ''
        for n, line in enumerate(p):
            # For each line in the proof, set the line number to its appropriate number and add it on a new line
            line._num = n
            lineStr = linePrinter(line, sentencePrinter, howToPrint)  
            if line._inference.name == 'Assumption':
                assumptions += lineStr
            else:
                deductions += lineStr
        
        inferencesString = ''
        for infStr in inferenceList:
            inferencesString += infStr + '\\\\\n\n'
        proofStr = proofStructure % (p.name, assumptions[:-3], deductions[:-3])
        return structure % (p.name, inferencesString + proofStr)
    
    


def compressedSentencePrinter(sen, symbols = None, sentencePrinter = None, data = None):
    '''
    Outputs a sentence in the least number of bytes as a BitStream
    
    @param data - A dict of strings to BitStrems
    '''
    from copy import copy
    from BitStream.bitStream import BitStream
    
    # If the arity is 0, then just return the operator
    if sen.arity() == 0:
        return copy(data[str(sen.op())])

    # Otherwise, print the operator
    stream = copy(data[str(sen.op())])

    # Then its arguments
    for arg in sen.args():
        stream += compressedSentencePrinter(arg, symbols, sentencePrinter, data)

    return stream    
    
    
def compressedProofPrinter(p, printedInferences = None, inferencePrinter = None, linePrinter = None, sentencePrinter = None, howToPrint = None):
    '''
    Outputs the Proof in the least number of bytes
    '''
    from BitStream.bitStream import BitStream
    
    checkedInferences = set([])
    sentences = []
    
    inference_queue = p.getInferences().values()
    while len(inference_queue) > 0:
        inf = inference_queue.pop()
        # For each inference check if we printed it alredy
        if inf not in checkedInferences:
            # If it is new
            try:
                # Assume it's a Proof and add its Inferences to the queue
                inference_queue += inf.getInferences().values()
                # Add each sentence to the set of sentences
                for sen in inf:
                    sentences.append(sen.getSentence())
                    
            except AttributeError:
                # It must be an Inference
            
                # Add each sentence to the set of sentences
                for sen in inf:
                    sentences.append(sen)
                
            # Add the inference to the checkedInferences set
            checkedInferences.add(inf)    
    
    freqCount = {}
    aritys = {}
    for sen in sentences:
        if str(sen.op()) not in freqCount:
            freqCount[str(sen.op())] = 1
        else:
            freqCount[str(sen.op())] += 1
        if str(sen.op()) not in aritys:
            aritys[str(sen.op())] = sen.arity()
        for subsen in sen.args():
            sentences.append(subsen)
            
    print freqCount