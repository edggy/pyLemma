import proof
import printers

class InferenceIterator:
    '''
    An iterator that goes through each premise and the conclusion of the inference.

    Note: 
    The premises may appear in any order
    The conclusion is always last
    '''
    def __init__(self, inf):
        # Keep track of the conclusion and an iterator of the premises
        self._conclusion = inf._conclusion
        self._premises = iter(inf._premises)

    def __iter__(self):
        return self

    def next(self):
        try:
            # Try to get the next premise
            data = self._premises.next()
            return data
        except StopIteration:
            # Otherwise try to get the conclusion
            if self._conclusion:
                data = self._conclusion

                # Set the conclusion to None so we know it was used
                self._conclusion = None
                return data

            raise StopIteration

class Inference(proof.Proof):
    '''
    Inference is the act or process of deriving logical conclusions from premises known or assumed to be true.
    '''

    def __init__(self, name, conclusion = None, premises = None, printer = None, newVars = None):
        # The name of this Inference rule
        # TODO: Allow a nickname to print
        self.name = name

        # The conclusion of this inference rule
        self._conclusion = conclusion

        # A set of premises
        self._premises = set(premises)

        # The printer to print the infrence rule
        if printer is None:
            # Use default printer
            self._printer = printers.defaultInferencePrinter
        else:
            self._printer = printer

        # self._newVars is a set of new variables
        self._newVars = newVars
        if self._newVars is None:
            self._newVars = set([])

    def __iter__(self):
        # Returns an iterator of itself
        return InferenceIterator(self)

    def __str__(self):
        return self._printer(self)

    def __repr__(self):
        return self._printer(self)
    
    def __hash__(self):
        return hash((tuple(self._premises), self._conclusion))

    def __eq__(self, other):
        # Two inference rules are equal if the premises are equal and the conclusions are the same
        return self.getPremises() == other.getPremises() and self.getConclusion() == other.getConclusion()

    def getPremises(self):
        '''
        Gets the premises of this inference rule

        @return - A set of sentences containing the premises
        '''
        return self._premises

    def getConclusion(self):
        '''
        Gets the conclusions of this inference rule

        @return - A list containing the conclusions of this inference rule
        '''
        return [self._conclusion]

    def isValid(self, sen, ref):
        '''
        Checks wheather the sentence is a valid conclusion of the references using this inference rule 
        '''
        # A inference with no conclusion isalways true i.e. from anything you can derive nothing
        if self._conclusion is None:
            return True

        # Create a mapping of variables from the conclusion to the sentence
        for conclusionMap in self._conclusion.mapInto(sen): #, False):
            if len(conclusionMap) == 0:
                # If there is no mapping, then this inference is not valid
                return False
    
            # Put all of the sentences into a list
            refList = []
            for r in ref:
                try:
                    refList.append(r())
                except ReferenceError:
                    return False
    
            # If we have variables that we need to be new
            #if self._newVars is not None:
                #for l in [r() for r in ref]:
                    #for var in self._newVars:
                        ## Check each line to see if it contains the "new" variable
                        #if var in l:
                            #return False
    
            # For each premise we need it to match at least one reference
            mapping = self.makeMapping(conclusionMap, self._premises, refList, False)
            
            # Return True if a mapping exists
            if len(mapping) > 0:
                return True
            
        # All mappings failed
        return False


