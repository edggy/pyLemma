import weakref

import sentence
import proof
import printers

class Line:
    '''
    A line of a Proof
    '''

    def __init__(self, proof):
        # The proof that this line is in as a weak ref
        self._proof = weakref.ref(proof)

        # The sentence at this line
        self._sentence = None

        # The inference rule used at this line
        self._inference = None

        # A set of weak refs to the lines that support this line
        self._support = set([])

        # The current line number. Used for printing
        self._num = None

        # Other data that this line may have
        self._data = {}

    def __iadd__(self, other):
        '''
        Adds something to this line

        Acts as a shortcut to setSentence, addSupport, and setInference
        '''
        if isinstance(other, sentence.Sentence):
            # If we add a sentence, add it as a sentence
            self.setSentence(other)
        elif isinstance(other, Line):
            # If it is a line add it as a support step
            self.addSupport(other)  
        elif isinstance(other, (int, long)):
            # If it is an int or long get that line and add it to the support set
            self.addSupport(self._proof()[other]) 
        elif isinstance(other, proof.Proof):
            # If it is an inference rule or proof
            infs = self._proof()._inferences

            # Check to see if it is in the proof's inference dict
            if other.name not in infs:
                # If it is new, add it to the dict
                infs[other.name] = other

            # set the inference
            self.setInference(other)
        elif isinstance(other, str):
            # If it is a string, search for it in the proof's inference rules and add that rule to this line
            self.setInference(self._proof()._inferences[other])
        else:
            # Otherwise we don't know how to deal with this
            raise TypeError('other is a ' + str(type(other)))
        return self

    def __str__(self):
        return printers.defaultLinePrinter(self)

    def __hash__(self):
        # The hash is the hash of its sentence and inference
        return hash((self._sentence, self._inference))

    def __contains__(self, item):
        # This checks weather item was assumed in this line
        for i in self._support:
            sen = i()._sentence

            # If the item is the sentence or the item is in the sentence, then it is in this
            if item == sen or item in sen:
                return True

        # If the sentence is a subproof, check the first argument too
        if self._sentence.op() == '|-' and (item == self._sentence[0] or item in self._sentence[0]):
            return True

        return False	

    def setSentence(self, sen):
        '''
        Set the sentence of this line
        '''
        # Reset the line number since the line has chaged. Used for verification caching
        self._num = None

        # set the sentence
        self._sentence = sen
        
        self._data['sen'] = self._sentence.extraData

    def getSentence(self):
        '''
        Gets the sentence of this line
        '''
        return self._sentence

    def setInference(self, inf):
        '''
        Set the inference rule that this line uses
        '''
        # Reset the line number since the line has chaged. Used for verification caching
        self._num = None
        self._inference = inf

    def getInference(self):
        '''
        Get the inference rule that this line uses
        '''		
        return self._inference

    def addSupport(self, line):
        '''
        Adds another line as a supporting line
        '''
        # Reset the line number since the line has chaged. Used for verification caching
        self._num = None

        # Add the lines as a weak reference
        self._support.add(weakref.ref(line))

    def discardSuppprt(self, line):
        '''
        Removes another line as a supporting line
        '''		
        # Reset the line number since the line has chaged. Used for verification caching
        self._num = None

        # discard the line from the set
        self._support.discard(line)

    def getSuppprt(self):
        '''
        Returns the set of support steps
        '''
        return self._support
    
    def isNew(self, variables = None):
        if variables is None:
            variables = self._data['sen']['newVars']
            
        for ref in self._support:
            try:
                refLine = ref()
                for var in variables:
                    if var in refLine._sentence:
                        return False
            except ReferenceError:
                pass
            
        return True
            
        

