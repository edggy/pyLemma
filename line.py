import sentence
#import inference
import proof

class Line:
    '''
    A line of a Proof
    '''
    
    def __init__(self, proof):
        import weakref
        self._proof = weakref.ref(proof)
        self._sentence = None
        self._inference = None
        self._support = set([])
        self._num = None
        self._data = None
            
    def __iadd__(self, other):
        if isinstance(other, sentence.Sentence):
            self.setSentence(other)
        elif isinstance(other, Line):
            self.addSupport(other)  
        elif isinstance(other, (int, long)):
            self.addSupport(self._proof()[other]) 
        elif isinstance(other, proof.Proof):
            infs = self._proof()._inferences
            if other.name() not in infs:
                infs[other.name()] = other
            self.setInference(other)
        elif isinstance(other, str):
            self.setInference(self._proof()._inferences[other])
        else:
            raise TypeError('other is a ' + str(type(other)))
        return self
    
    def __str__(self):
        supportLines = [i()._num for i in self._support]
        supportLines.sort()
        ret = str(self._num) + '\t' + str(self._sentence)
        if self._inference is not None:
            ret += '\t' + str(self._inference.name())
        else:
            ret += '\t' + '???'
        
        if len(supportLines) > 0:
            ret += '\t' + str(supportLines)[1:-1]
            
        return ret
    
    def __hash__(self):
        return hash(str(self))
        
    def setSentence(self, sen):
        self._num = None
        self._sentence = sen
        
    def getSentence(self):
        return self._sentence
        
    def setInference(self, inf):
        self._num = None
        self._inference = inf
        
    def getInference(self):
        return self._inference
        
    def addSupport(self, line):
        import weakref
        self._num = None
        self._support.add(weakref.ref(line))
        
    def discardSuppprt(self, line):
        self._num = None
        self._support.discard(line)
        
    def getSuppprt(self):
        return self._support
        
