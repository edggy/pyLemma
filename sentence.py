import copy

import util
import printers

class Sentence:
    '''
    A finite sequence of symbols from a given alphabet that is part of a formal language

    Contains an operator and some number of arguments
    '''
    def __init__(self, op, args, data = None):
        '''
        @param op - The main operator of the sentence
        @param args - A tuple of the arguments of the main operator
        @param data - An optional argument to store extra data in the Sentence
        '''

        # _data is a list starting with the operator followed by the arguments
        self._data = tuple([op] + list(args))

        # Used to cache the length
        self._length = None
        self._terms = None

        # Used to store extra information
        self.extraData = data
        if self.extraData is None:
            self.extraData = {}

    def __lt__(self, other):
        '''
        A sentence is less than another sentence if there exists a mapping of 
        variables to sentences such that when you make the substitution in the 
        smaller sentence it equals the larger sentence and the larger sentence 
        cannot be mapped into the smaller one

        e.g.
        'and(?A, ?B) < and(P, Q)'
        '''
        return self <= other and len(other.mapInto(self)) == 0

    def __le__(self, other):
        '''
        A sentence is less than or equal to another sentence if there exists a 
        mapping of variables to sentences such that when you make the 
        subsitution in the smaller sentence it equals the larger sentence

        e.g.
        'and(?A, ?B) <= and(P, Q)'
        '''		
        return len(self.mapInto(other)) > 0

    def __eq__(self, other):
        '''
        Two sentences are equal iff their operators and all the arguments are
        equal
        '''
        return self._data == other._data

    def __ne__(self, other):
        '''
        Two sentences are not equal iff either their operators are not equal 
        or their arguments are not equal
        '''
        return self._data != other._data

    def __gt__(self, other):  
        '''
        e.g.
        'and(P, Q) > and(?A, ?B)'
        '''
        # self > other iff other < self
        return other.__lt__(self)

    def __ge__(self, other):
        '''
        e.g.
        'and(P, Q) >= and(?A, ?B)'
        '''
        # self >= other iff other <= self
        return other.__le__(self)

    def __repr__(self):
        return printers.prefixSentencePrinter(self, self.extraData)

    def __hash__(self):
        return hash(self._data) * hash(type(self))

    def __len__(self):
        '''
        The length of a sentence is one more than the sum of it's arguments
        '''
        if self._length is None:
            # Calculate the length
            self._length = 1
            for s in self._data[1:]:
                # recursively add the length of its arguments
                self._length += len(s)

        return self._length

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return SentenceIterator(self)

    def __contains__(self, item):
        for i in self._data:
            # If the item is an argument or the item is in the argument, then it is in this
            if item == i or item in i:
                return True
        return False

    def __copy__(self):

        # Since Sentences are immutable a copy is itsself
        return self

    def __deepcopy__(self, memo):

        # Since Sentences are immutable a deep copy is itsself
        return self

    def mapInto(self, other, replaceAll = True):
        '''
        Returns a list of dicts of the smallest mapping of variables to sentences that if substituted 
        into this sentence would make this sentence == other, or [] (empty list) if there is none 

        Examples:
        sen1 = 'and(@a, @b)'
        sen2 = 'and(or(p,q),iff(r,s))'
        sen1.mapInto(sen2) == {'and':'and', @a': 'or(p, q)', '@b':'iff(r,s)'}
        '''

        # Check that other is not none and the aritys are the same for a quick sanity check
        if other is None or self.arity() != other.arity():
            return []

        results = [{}]
        for m, n in zip(self, other):
            madeMapping = False
            newResults = []
            # For each argument, try to map it into the other argument recursively
            for mapping in m.mapInto(n):

                # If there is no mapping for a pair of arguments, then there is no maping at all
                if not mapping: 
                    continue
    
                
                for res in results:
                    # Merge the mapping into the results
                    newResult = util.mapMerge(res, mapping)
                    if len(newResult) > 0:
                        newResults.append(newResult)
                        madeMapping = True
            results = newResults
            
        if not madeMapping:
            return []
        return results

    def applyFunction(self, function, data = None):
        '''
        Apply a function recursively to this sentence and each of its arguments

        @param function - A function that takes 2 arguments, a sentence and a data object and returns a sentence
        @return - A new sentence of the funcion being applied to the original
        '''

        if data is None:
            data = {}

        args = []

        # Apply the function to this sentence
        sen = function(self, data)

        for s in sen:
            # Apply the function recursively to each of the arguments
            args.append(s.applyFunction(function, data))

        # Return a new sentence after the function has been applied
        return sf.generateSentence(args[0], args[1:])


    def subsitute(self, mapping, replaceAll = True):
        '''
        Makes a subsitution recursively

        @param mapping - The substitutions to be applied
        @return - A list of sentences with all the substitutions made
        '''

        if self in mapping:
            return [mapping[self]]

        def sub(sen, data):
            if sen in mapping:
                return mapping[sen]
            return sen

        if replaceAll:
            return [self.applyFunction(sub)]
        
        
        results = set([self])
            
        for i, s in enumerate(self):
            try:
                for sub in s.subsitute(mapping, replaceAll):
                    if s == sub:
                        continue
                    
                    if i == 0:
                        newSen = sf.generateSentence(sub, self[1:])
                    else:
                        args = list(self[1:])
                        args[i - 1] = sub
                        newSen = sf.generateSentence(self[0], args)
                    results.add(newSen)
                    results |= set(newSen.subsitute(mapping, replaceAll))
                    
            except AttributeError:
                pass
            
            
        return list(results)

    def op(self):
        '''
        Gets the main operator of this sentence
        '''
        return self._data[0]

    def args(self):
        '''
        Gets the arguments of the main operator
        '''
        return self._data[1:]

    def arity(self):
        '''
        Gets the arity of the main operator i.e. the number of arguments
        '''
        return len(self._data) - 1

    def generalize(self):
        '''
        Converts all literals into varibles

        @return - a copy of this sentence with all of the literals as variables with the same name
        '''

        retArgs = list(self._data)[1:]

        for n, arg in enumerate(retArgs):
            retArgs[n] = arg.generalize()

        return Sentence(self.op(), retArgs)

    def terms(self):
        if self._terms is None:
            self._terms = set([])
            for p in self._data:
                self._terms |= (p.terms())
        return self._terms       

    def subSentences(self):
        res = set([self])
        for s in self[1:]:
            res |= s.subSentences()
        return res

class Wff(Sentence):
    '''
    A Wff is a placeholder in a sentence that matches any sentence
    '''

    def __init__(self, name = 'A', symbol = '', data = None):
        # The name of the Wff, same named variables are considered to be the same Wff

        try:
            self._name = name._name
        except AttributeError:
            self._name = ''.join(str(name).split())

        # A Wff is an operator with no arguments
        self._data = (name)

        # The symbol used to print
        self._symbol = symbol

        # Used to store extra information
        self.extraData = data
        if self.extraData is None:
            self.extraData = {}        

    def __repr__(self):
        return self._symbol + self._name    

    def __str__(self):
        return self._symbol + self._name

    def __lt__(self, other):
        '''
        A Wff is less than a sentence as long as the sentecne cannot be mapped into a Wff
        '''

        # Ensure other is not a Wff
        return len(other.mapInto(self)) == 0

    def __le__(self, other):
        '''
        A Wff is always less than or equal to another sentence
        '''        
        # Vacuously true since {self: other} is always a valid mapping
        return True

    def __eq__(self, other):
        '''
        A Wff is equal to other if other is not a Wff or they share the same representation
        '''

        # Something is a Wff if it is less than or equal to a Wff
        return other <= self and str(self) == str(other)

    def __ne__(self, other):
        '''
        A Wff is not equal to other if other is a Wff and they dont share the same representation
        '''     

        # Something is a Wff if it is less than or equal to a Wff
        return other <= self and str(self) != str(other)

    def __hash__(self):
        return hash(self._name)

    def __len__(self):
        return 1

    def __getitem__(self, key):
        # Wff have no arguments
        if key == 0:
            return self.op()
        raise IndexError

    def __iter__(self):
        return SentenceIterator(self)

    def __contains__(self, item):
        # Wff contain no arguments
        return False

    def __copy__(self):
        # A copy of a Wff is itseelf
        return self

    def __deepcopy__(self, memo):
        # A deep copy of a Wff is itsself
        return self

    def op(self):
        return self

    def args(self):
        return ()

    def arity(self):
        return 0

    def mapInto(self, other, replaceAll = True):
        '''
        A Wff can map into anything
        '''
        return [{self: other}]

    def subsitute(self, mapping, replaceAll = True):
        if self in mapping:
            return [mapping[self]]
        return [self]

    def generalize(self):
        # Already generalized
        return sf.generateWff(self._name)

    def applyFunction(self, function, data = None):
        '''
        Apply a function recursively to this sentence and each of its arguments

        @param function - A function that takes 2 arguments, a sentence and a data object and returns a sentence
        @return - A new sentence of the funcion being applied to the original
        '''

        if data is None:
            data = {}

        # Return a new sentence after the function has been applied
        return function(self, data)

    def terms(self):
        return set([self])

    def subSentences(self):
        return set([self])

class Variable(Wff):
    '''
    A variable is a Wff but only for atomic terms
    '''
    def mapInto(self, other, replaceAll = True):
        '''
        A Variable can only map into atomic terms
        '''
        if len(other.args()) == 0 and (not isinstance(other, Wff) or isinstance(other, Variable)):
            return [{self: other}]
        return []

class Literal(Variable):
    '''
    A literal is the smallest sentence
    '''

    def __lt__(self, other):
        '''
        Vacuously false since a literal cannot be mapped except to itsself
        '''
        return False

    def __le__(self, other):
        '''
        Only true when self == other
        '''
        return self == other

    def __eq__(self, other):
        '''
        A Literal is equal if they have the same representation
        '''
        return str(self) == str(other)

    def __ne__(self, other):
        '''
        A Literal is equal if they have the different representation
        '''        
        return str(self) != str(other)	

    def mapInto(self, other, replaceAll = True):
        '''
        A literal can only map into itsself 
        '''
        if self == other:
            return [{self: other}]

        return []
    
class Operator(Sentence):

    def __len__(self):
        return 1

    def __contains__(self, item):
        return self == item

    def mapInto(self, other, replaceAll = True):
        '''
        e.g.
        '?P[?x]'.mapInto('if(A(y),B(y))')
        -> {'?P[@]':'if(A(@),B(@))', '?x':'y'}

        '?P[@a]'.mapInto('if(A(s(a)),B(s(a)))')
        -> {'?P[@]':'if(A(@),B(@))', '@a':'s(a)'}
        -> {'?P[@]':'if(A(s(@),B(s(@))))', '@a':'a'}

        '?P[@a]'.mapInto('if(A(s(a)),B(s(b)))')
        -> {'?P[@]':'if(@,B(s(b)))', '@a':'A(s(a))'}
        -> {'?P[@]':'if(A(@),B(s(b)))', '@a':'s(a)'}
        -> {'?P[@]':'if(A(s(@)),B(s(b)))', '@a':'a'}
        -> {'?P[@]':'if(A(s(a)),@)', '@a':'B(s(b))'}
        -> {'?P[@]':'if(A(s(a)),B(@))', '@a':'s(b)'}
        -> {'?P[@]':'if(A(s(a)),B(s(@)))', '@a':'b'}

        '?P[@Q(?x)]'.mapInto('if(A(s(a)),B(s(b)))')
        -> {'?P[@]':'if(A(@),B(s(b)))', '@Q':'s', '?x':'a'}
        -> {'?P[@]':'if(A(s(a)),B(@))', '@Q':'s', '?x':'b'}

        '?P[@Q(@x)]'.mapInto('if(A(s(a)),B(s(b)))')
        -> {'?P[@]':'if(@,B(s(b)))', '@Q':'A', '@x':'s(a)'}
        -> {'?P[@]':'if(A(@),B(s(b)))', '@Q':'s', '@x':'a'}
        -> {'?P[@]':'if(A(s(a)),@)', '@Q':'B', '@x':'s(b)'}
        -> {'?P[@]':'if(A(s(a)),B(@))', '@Q':'s', '@x':'b'}
        '''

        results = []

        # Example 1 -> '?P[@a]'.mapInto('if(A(s(a)),B(s(b)))')
        # Example 2 -> '?P[@Q(@x)]'.mapInto('if(A(s(a)),B(s(b)))')

        # Example 1 -> '?P'
        # Example 2 -> '?P'
        op = self[0]

        # Example 1 -> '?x'
        # Example 2 -> '@Q(@x)
        arg = self[1]

        # Example 1 & 2-> other = 'if(A(s(a)),B(s(b)))'
        for s in other.subSentences():
            # Example 1 & 2 -> 
            # s = 'if(A(s(a)),B(s(b)))'
            #   = 'A(s(a))'
            #   = 'B(s(b))'
            #   = 's(a)'
            #   = 's(b)'
            #   = 'a'
            #   = 'b'

            for mapping in arg.mapInto(s):
                # Example 1->
                # mapping = {'?x':'if(A(s(a)),B(s(b)))'}
                # ...
    
                # Example 2 -> 
                # mapping = None
                #          = {'@Q':'A', '@x:'s(a)}
                #          = {'@Q':'B', '@x:'s(b)}
                #          = {'@Q':'s', '@x:'a'}
                #          = {'@Q':'s', '@x:'b'}
                #          = None
                #          = None    
    
                # Ensure a mapping exists
                if mapping is None:
                    continue
    
                subs = arg.subsitute(mapping)[0]
                # Example 1 -> 
                # subs = 'if(A(s(a)),B(s(b)))'
                #      = 'A(s(a))'
                # ...
    
                # Example 2 ->
                # subs = N/A
                #      = 'A(s(a))'
                # ...            
                
                structs = other.subsitute({subs:sf.generateWff('')}, replaceAll)
                # Example 1 ->
                # structure = '@'
                #           = 'if(@,B(s(b)))'
                #           = ...
    
                # Example 2 -> 
                # structure = N/A
                #           = 'if(@,B(s(b)))'
                # ...
                
                for structure in structs:
                    
                    # Ensure that we can map the operators
                    if not op <= structure.op():# or len(structure.args()) == 0:
                        continue
                
                    mapping[op] = structure
                    results.append(copy.copy(mapping))
                
        return results

class SentenceIterator:
    def __init__(self, sen):

        # The sentence to iterate over
        self._sen = sen

        # Start at the beginning
        self._index = 0

    def __iter__(self):
        return self

    def next(self):
        try:
            data = self._sen[self._index]
            self._index += 1
            return data
        except IndexError:
            raise StopIteration

class InvalidSentenceError(Exception):
    pass

class SentenceFactory:
    def __init__(self):
        self._cache_sen = {}
        self._cache_wff = {}
        self._cache_var = {}
        self._cache_lit = {}
        self._cache_op = {}

    def generateSentence(self, operator, arguments, data = None):
        '''
        Constructs a sentence using the operator and arguments provided

        @param operator - The main operator of the sentence
        @param arguments - The arguments of the main operator

        @return - A sentence that is formed from the operator and the arguments
        '''

        arguments = tuple(arguments)
        # Check if the sentence is in the cache
        if (operator, arguments) in self._cache_sen:
            newSentence = self._cache_sen[(operator, arguments)]
        else:
            newSentence = Sentence(operator, arguments, data)
            self._cache_sen[(operator, arguments)] = newSentence

        return newSentence

    def generateWff(self, name, symbol = '@', data = None):
        '''
        Creates a Wff from the given name
        '''
        # Check the cache
        if name in self._cache_wff:
            newWff = self._cache_wff[name]
        else:
            newWff = Wff(name, symbol, data)
            self._cache_wff[name] = newWff

        return newWff   

    def generateVariable(self, name, symbol = '?', data = None):
        '''
        Creates a Variable from the given name
        '''
        # Check the cache
        if name in self._cache_var:
            newVariable = self._cache_var[name]
        else:
            newVariable = Variable(name, symbol, data)
            self._cache_var[name] = newVariable

        return newVariable

    def generateLiteral(self, name, symbol = '', data = None):
        '''
        Creates a Literal from the given name
        '''
        # Check the cache
        if name in self._cache_lit:
            newLiteral = self._cache_lit[name]
        else:
            newLiteral = Literal(name, symbol, data)
            self._cache_lit[name] = newLiteral

        return newLiteral
    
    def generateOperator(self, mainOperator, arguments, data = None):
        '''
        Constructs a operator using the mainOperator and arguments provided

        @param mainOperator - The main mainOperator of the operator
        @param arguments - The arguments of the main operator

        @return - A operator that is formed from the operator and the arguments
        '''

        arguments = tuple(arguments)
        # Check if the sentence is in the cache
        if (mainOperator, arguments) in self._cache_op:
            newOp = self._cache_op[(mainOperator, arguments)]
        else:
            newOp = Operator(mainOperator, arguments, data)
            self._cache_op[(mainOperator, arguments)] = newOp

        return newOp
        
sf = SentenceFactory()

if __name__ == '__main__':
    # This area used for debugging
    
    import printers2 as printers
    import parsers
    
    psp = parsers.prefixSentenceParser    
    
    printer = lambda sen: printers.prefixSentencePrinter(sen)

    sf = SentenceFactory()

    op1 = sf.generateLiteral('and')
    op2 = sf.generateVariable('P')

    var1 = sf.generateVariable('A')
    var2 = sf.generateVariable('B')

    sen1 = sf.generateSentence(op1, (var1, var2))
    sen2 = sf.generateSentence(op1, (var1, sen1))
    sen3 = sf.generateSentence(op2, (var1, var2))
    sen4 = sen1.subsitute({var1:var2, var2:var1})[0]

    def testSens(senA, senB):
        print("'%s'.mapInto('%s') = %s" % (senA, senB, senA.mapInto(senB)))
        print("'%s'.mapInto('%s') = %s" % (senB, senA, senB.mapInto(senA)))
        print('%s <  %s:' % (senA, senB), senA < senB)
        print('%s <= %s:' % (senA, senB), senA <= senB)
        print('%s == %s:' % (senA, senB), senA == senB)
        print('%s != %s:' % (senA, senB), senA != senB)
        print('%s >= %s:' % (senA, senB), senA >= senB)
        print('%s >  %s:' % (senA, senB), senA > senB	)

    print(sen1, len(sen1))
    print(sen2, len(sen2))
    print(sen3, len(sen3))
    print()
    testSens(sen1, sen2)
    print(sen1.subsitute({var1:sen1}))
    print()
    testSens(sen1, sen3)
    print()
    testSens(sen3, sen1)
    print()
    testSens(sen1, sen4)
    print()
    testSens(sen4, sen1)    

    
    sen5 = psp('if(A(s(a)),B(s(b)))')
    sen6 = psp('if(A(s(a)),B(s(a)))')
    print(sen5.terms())
    print(sen5.subSentences())
    print(sen6.terms())
    print(sen6.subSentences())
    
    sen7 = psp('@P[?x]')
    sen8 = psp('@P[@x]')
    testSens(sen7, sen3)
    testSens(sen7, sen5)
    testSens(sen8, sen3)
    testSens(sen8, sen5)    
    testSens(sen7, sen8)  
    
    sen9 = psp('@P[@b]')
    sen10 = psp('=(b, b)')
    print(sen9.mapInto(sen10))
    print(sen9.mapInto(sen10, False))
    
    sen11 = psp('@P[0]')
    sen12 = psp('=(+(0, 0), 0)')
    
    print(sen11.mapInto(sen12, False))
    
    sen13 = psp('|-(@P[?c], @P[s(?c)])')
    sen14 = psp('|-(A(B(C, a), a), A(B(C, s(a)), s(a)))')
    
    testSens(sen13, sen14)
    
    sen15 = psp('|-(@P[?a], @P[s(?a)])')
    sen16 = psp('|-(P(b, a), P(s(b), a))')    
     
    testSens(sen15, sen16)
    