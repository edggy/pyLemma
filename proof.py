from collections import deque

import inference
import sentence
import line
import util
import printers

class Proof:
    '''
    A finite sequence of sentences (called well-formed formulas in the case
    of a formal language) each of which is an axiom, an assumption, or
    follows from the preceding sentences in the sequence by a rule of
    inference
    '''	

    def __init__(self, name, proofPrinter = None, numbering = None):
        '''
        @param name - The name of the proof
        @param proofPrinter - A function to use to print the proof in the format wanted
        '''

        # Set name to name
        self.name = name

        if proofPrinter:
            # Set the printer if given
            self._printer = proofPrinter
        else:
            # Use the default printer
            self._printer = printers.defaultProofPrinter		

        # Initally a proof has no lines
        # A list of the lines of the proof
        self._lines = []

        # Initially a proof uses no inferences
        # A dict from identifiers to inferences
        self._inferences = {}

        if numbering:
            # Set the numbering scheme if given
            self._numbering = numbering
        else:
            # Use the default numbering scheme
            self._numbering = lambda x: x

    def name(self):
        '''
        Gets the name of the proof as a string
        '''
        return self.name

    def addLine(self):
        '''
        Add an empty line to the end of the proof
        '''
        self._lines.append(line.Line(self))

    def addLines(self, amount = 1):
        '''
        Adds an **amount** of empty lines to the end of the proof
        '''
        for i in range(amount):
            self.addLine()

    def insertLine(self, index = -1):
        '''
        Inserts an empty line before the **index** line of the proof
        '''
        self._lines.insert(index, None)

    def insertLines(self, index = -1, amount = 1):
        '''
        Adds an **amount** of empty lines before **index**
        '''
        for i in range(amount):
            self._lines.insert(index + i, None)

    def removeLine(self, index = -1):
        '''
        Deletes the line at **index** from the prooff
        '''
        del self._lines[index]

    def removeLines(self, index = -1, amount = 1):
        '''
        Deletes an **amount** of empty lines at and following **index**
        '''
        for i in range(amount):
            self.removeLine(index)

    def setSentence(self, sen, index = -1):
        '''
        Sets the sentence at **index** to **sen**
        '''
        self._lines[index] += sen

    def getSentence(self, index):
        '''
        Gets the sentenced at line **index** of the proof
        '''
        return self._lines[index].getSentence()

    # TODO:
    # def getSentences
    # def removeSentence
    # def removeSentences

    def setInference(inf, index = -1):
        '''
        Set the inference rule for the line at **index**

        @param inf - The inference rule to add
        @param index - The line number to set the infrence of
        '''
        self._lines += inf

    # TODO:
    # def addInference
    # def getInference
    # def removeInference

    def addSupport(ref, index = -1):
        '''
        Adds a support to the line at **index**

        @param ref - Either a line number or a line object
        '''
        self._lines += inf

    # TODO:
    # def addReference
    # def getReference
    # def removeReference

    def verify(self):
        '''
        Verifies that the current proof is valid, i.e. each line validly follows from the previous lines

        @return - True if the proof is valid, otherwise the line number of the first invalid line
        '''

        # Assume there are no errors
        err_line = None

        # Go through each line and check that it is valid
        for line_num, line in enumerate(self._lines):			

            # inf is the inference rule used
            inf = line.getInference()

            # sen is the sentence at this line
            sen = line.getSentence()

            # if there is no rule, then this line is not valid, unless the sentence is also None (this is to allow empty lines)
            if inf is None and sen is not None:
                err_line = line_num
                break

            # sup is the set of support steps
            sup = line.getSuppprt()

            # Check each reference (which is a weakref to a line)
            for ref in sup:
                try:
                    if ref()._num is None:
                        # This implies that ref refers to a line later in the proof (or itself), not an earlier one
                        err_line = line_num
                        break
                except ReferenceError:
                    # This implies that the line no longer exists 
                    err_line = line_num
                    break

            # This is used to check if there was an error in the previous for loop
            if err_line is not None:
                break

            # Check that the sentence is a valid conclusion of the support steps using thie given inference rule
            if not inf.isValid(sen, sup):
                err_line = line_num
                break

            # Assign this line a line number since it is valid
            line._num = line_num


        # If there are no errors, return True
        if err_line is None:		
            return True

        # Since this is an invalid proof, first set all the line numbers to None
        for line in self._lines:
            line._num = None

        # Then return err_line, so the user can debug
        return self._numbering(err_line)

    def isValid(self, sen, ref, newVars = None):
        '''
        Given a sentence and a set of reference lines, check that this proof proves 
        that the sentence is deductively follows from the reference lines

        @return - True iff the proof proves that given sentence 
        '''

        # Check that this proof is valid, if it is not then we canot check anything
        if self.verify() is not True:
            return False

        # put all of the reference sentences into a list
        refLines = []
        for r in ref:
            try:
                refLines.append(r())
            except ReferenceError:
                return False            

        premises = self.getPremises()

        # Generalize the premises
        genPrem = set([])
        for prem in premises:
            genPrem.add(prem.generalize())

        # TODO: Use other symbols for subproof
        if sen.op() == '|-':
            # Add the subproof assumption to the reference list
            if str(sen.args()[0]) != '':
                assumption = line.Line(self)
                assumption.setSentence(sen.args()[0])
                refLines.append(assumption)

            # We are trying to prove the second part
            sen = sen.args()[1]		

        ## If we have variables that we need to be new
            #if newVars is not None:
                #for s in refSenList:
                    #for var in newVars:
                        ## Check each sentence to see if it contains the "new" variable
                        #if var in s:
                            #return False	

        prevSens = []
        metaSen = None
        for s in self:
            # Assume s is the conclusion
            curSen = s.getSentence().generalize()

            # Check if the current sentence can map into the conclusion
            for conclusionMap in curSen.mapInto(sen):
                # Try to map the assumptions to the refSenList
                mapping = self.makeMapping(conclusionMap, genPrem, refLines)
                if len(mapping) > 0:
                    # If there is a mapping then we are done
                    return True
        return False

    def makeMapping(self, conclusionMap, premises, references, exact = True):
        '''
        Try to map all of the premises into the references in any combination while being constrained by the current conclusionMap

        @param conclusionMap - The current mapping of variables into references
        @param premises - A list of premises
        @param references - A list of references (lines) to be mapped into

        @return - A map of subsitutions of variables in premises that will make premises match all the references
        '''
        # If there are no premises, there is nothing else to map
        if premises is None or len(premises) == 0:
            return conclusionMap

        # If there are more premises than references, there is no mapping
        if (exact and len(premises) != len(references)):
            return {}

        # Add all the premises to the queue
        premiseQueue = deque(premises)

        # Call the makeMappingHelper that will recursively find a mapping
        return self.makeMappingHelper(conclusionMap, premiseQueue, references)	


    def makeMappingHelper(self, conclusionMap, premiseQueue, references):
        '''
        Try to map all of the premises into the references in any combination while being constrained by the current conclusionMap
        @param conclusionMap - The current mapping of variables into references
        @param premiseQueue - A queue of the premises
        @param references - A list of references (lines) to be mapped into
        @return - A map of subsitutions of variables in premises that will make premises match all the references
        '''	

        try:
            # Get the first premise
            curPrem = premiseQueue.pop()
        except IndexError:
            # Base case, the queue is empty
            return conclusionMap

        for curLine in references:
            
            # Try find a mapping of curPrem into curLine
            for mapping in curPrem.mapInto(curLine.getSentence(), False):

                if 'extra' in curPrem.extraData and 'newVars' in curPrem.extraData['extra']:
                    newVars = curPrem.extraData['extra']['newVars']
                    if not curLine.isNew([mapping[v] for v in newVars]):
                        continue                

                # try to merge this mapping into conclusionMap
                merge = util.mapMerge(conclusionMap, mapping)
    
                if len(merge) == 0:
                    continue
                
                # If the merge is successful recursively call makeMappingHelper for the merged map, and the remainder of the premiseQueue
                remainder = self.makeMappingHelper(merge, premiseQueue, references)
    
                if len(remainder) == 0:
                    continue
                
                # If we can map the remaining premises, this is a valid mapping, return it
                return remainder

        # If we get here then curPrem can't map inro any of the references  
        # Put the curPrem back into the queue in case we are still in the recursion
        premiseQueue.append(curPrem)

        # There is no valid mapping
        return {}	

    def __len__(self):
        '''
        The length of the proof is equal to the number of lines
        '''
        # TODO: don't count empty lines
        return len(self._lines)

    def __getitem__(self, key):
        '''
        Gets the specified line of the proof
        '''
        return self._lines[key]

    def __setitem__(self, key, value):
        '''
        Sets the specified line of the proof
        '''		
        self._lines[key] = value

    def __iter__(self):
        '''
        An interator of a proof is an iterator of it's lines
        '''
        return iter(self._lines)

    def __reversed__(self):
        '''
        The lines of the proof starting from the end
        '''
        return reversed(self._lines)

    def __str__(self):
        '''
        Prints the proof using the supplied printer
        '''
        return self._printer(self)		

    def __repr__(self):
        return self._printer(self)

    def __iadd__(self, value):
        '''
        Adds lines to the proof
        '''
        if isinstance(value, inference.Inference) and value.name not in self._inferences:
            # If we are given an inference not in our map, add it to our map
            self._inferences[value.name] = value
        elif isinstance(value, str):
            # If we are given a string, look it up in our inference map
            value = self._inferences[value]
        self.addLine()
        self._lines[-1] += value
        return self

    def setPrinter(self, newPrinter):
        '''
        Sets the printer for this proof

        A printer should take in a proof and return its string representation
        '''
        self._printer = newPrinter

    def setNumbering(self, newNumbering):
        '''
        Sets the numbering scheme for the lines

        A numbering scheme should take a line number starting at 0 and return what it should look like

        Example:

        if newNumbering is 'lambda x: x+1' the numbering will start at 1 instaed of 0
        '''
        self._numbering = newNumbering

    def getPremises(self):
        '''
        Returns a list of premises this proof assumes

        @return - A set of sentences containing the premises
        '''
        # Check if s is an assumption
        prems = set([])
        for l in self._lines:
            inf = l.getInference()
            # An inference rule is an assumption iff it has no premises, has exactly one conclusion,
            # and its conclusion can be mapped into a variable
            #
            # ---
            # A
            if len(inf.getPremises()) == 0 and len(inf.getConclusion()) == 1 and inf.getConclusion()[0] <= sentence.Variable():
                prems.add(l.getSentence())
        return prems

    def getConclusion(self):
        '''
        Gets the conclusions of this proof

        @return - A list containing the conclusions
        '''

        # Every line is a valid conclusion
        return map(lambda a: a.getSentence(), self._lines)

    def getInferences(self):
        '''
        Gets the inference rules used in this proof

        @return - A dict of inferece rule names to the associated inference rule
        '''
        return self._inferences


if __name__ == '__main__':
    # This area used for debugging
    pass
