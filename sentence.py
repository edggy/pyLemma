import copy

import util
import printers


class Sentence:
    '''
    A finite sequence of symbols from a given alphabet that is part of a formal language

    Contains an operator and some number of arguments
    '''
    def __init__(self, op, args, printer = None):
        '''
        @param op - The main operator of the sentence
        @param args - A tuple of the arguments of the main operator
        @param printer - The printer to use to print this Sentence
        '''
        # _op is the operator
        self._op = op

        # _args is a tuple of arguments
        self._args = args

        # Set the printer
        self._printer = printer

        # Use the default printer by default
        if self._printer == None:
            self._printer = printers.prefixSentencePrinter

    def __repr__(self):
        return str(self)

    def __str__(self):
        try:
            # Try to use the printer to print the sentence
            return self._printer(self)
        except TypeError:
            return ''

    def __lt__(self, other):
        '''
        A sentence is less than another sentence if there exists a mapping of 
        variables to sentences such that when you make the substitution in the 
        smaller sentence it equals the larger sentence and the larger sentence 
        cannot be mapped into the smaller one

        e.g.
        'and(?A, ?B) < and(P, Q)'
        '''
        return self <= other and other.mapInto(self) is None

    def __le__(self, other):
        '''
        A sentence is less than or equal to another sentence if there exists a 
        mapping of variables to sentences such that when you make the 
        subsitution in the smaller sentence it equals the larger sentence

        e.g.
        'and(?A, ?B) <= and(P, Q)'
        '''		
        return self.mapInto(other) is not None

    def __eq__(self, other):
        '''
        Two sentences are equal iff their operators and all the arguments are
        equal
        '''
        return self.op() == other.op() and self._args == other._args

    def __ne__(self, other):
        '''
        Two sentences are not equal iff either their operators are not equal or their arguments are not equal
        '''
        return self.op() != other.op() or self._args != other._args

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

    def __hash__(self):
        return hash((self._op, self._args))

    def __len__(self):
        '''
        The length of a sentence is one more than the sum of it's parts
        '''
        length = 1
        for s in self._args:
            # recursively add the length of its arguments
            length += len(s)
        return length

    def __getitem__(self, key):
        return self._args[key]

    def __iter__(self):
        return SentenceIterator(self)

    def __contains__(self, item):
        for i in self._args:
            # If the item is an argument or the item is in the argument, then it is in this
            if item == i or item in i:
                return True
        return False



    def __copy__(self):
        # Make a shallow copy of the operator
        newOp = copy.copy(self._op)

        # Make a shallow copy of the arguments
        newArgs = tuple(self._args)

        ret = Sentence(newOp, *newArgs)    
        ret.setPrinter(self._printer)
        return ret

    def __deepcopy__(self, memo):
        # Make a deep copy of the operator
        newOp = copy.deepcopy(self._op)

        # Make a deep copy of each of the arguments
        newArgs = tuple([copy.deepcopy(i) for i in self._args])

        ret = Sentence(newOp, *newArgs)
        ret.setPrinter(self._printer)
        return ret	

    def mapInto(self, other):
        '''
        Returns a dict of the smallest mapping of variables to sentences that if substituted 
        into this sentence would make this sentence == other, or None if there is none 

        Examples:
        sen1 = 'and(?a, ?b)'
        sen2 = 'and(or(p,q),iff(r,s))'
        sen1.mapInto(sen2) == {'?a': 'q or p', '?b':'r iff s'}
        '''

        if other is None:
            return None

        if isinstance(self.op(), Variable):
            pass

        # Check that the main operators and the arity are the same unless self.op() is a variable
        if self.op() != other.op() or self.arity() != other.arity():
            return None

        result = {}
        for m, n in zip(self, other):
            # For each argument, try to map it into the other argument recursively
            mapping = m.mapInto(n)

            # If there is no mapping for a pair of arguments, then there is no maping at all
            if not mapping: return None

            result = util.mapMerge(result, mapping)
        return result

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
        ret = Sentence(sen.op(), *args)
        ret.setPrinter(self._printer)
        return ret


    def subsitute(self, mapping):
        '''
        Makes a subsitution recursively

        @param mapping - The substitutions to be applied
        @return - A new sentence with all the substitutions made
        '''

        # TODO: use the applyFunction method

        # Base case: check if this sentence is in the mapping, if so we are done
        if self in mapping:
            return mapping[self]

        args = []
        for s in self:
            # For each argument in self, check if it is in the mapping
            if s in mapping:
                # If it is, make the subsitution
                args.append(mapping[s])
            else:
                # If it is not, recursively make more subsitutions
                args.append(s.subsitute(mapping))

        sen = Sentence(self.op(), *args)
        sen.setPrinter(self._printer)
        return sen

    def op(self):
        '''
        Gets the main operator of this sentence
        '''
        return self._op

    def setPrinter(self, printer):
        '''
        Sets the printer for this sentence and its arguments
        '''
        self._printer = printer
        for arg in self:
            arg.setPrinter(printer)

    def arity(self):
        '''
        Gets the arity of the main operator i.e. the number of arguments
        '''
        return len(self._args)

    def generalize(self):
        '''
        Converts all literals into varibles

        @return - a copy of this sentence with all of the literals as variables with the same name
        '''

        retArgs = list(self._args)

        for n, arg in enumerate(retArgs):
            retArgs[n] = arg.generalize()

        return Sentence(self.op(), *retArgs)


class Wff(Sentence):
    '''
    A Wff (Well formed formula) is a sentence that may contain more arguments

    e.g.
    phi <= 'A'
    phi <= 'and(A,B)'
    phi <= phi(x) <= P(x)
    phi(x) <= and(A, P(x))
    phi(x) <= phi(x, y) <= or(R(x), P(x,y))
    phi(x, y) == phi(y, x)
    '''
    def __lt__(self, other):
        '''
        A Wff is less than a sentence as long as the sentecne 
        '''


    def __le__(self, other):
        '''
        A variable is always less than or equal to another sentence
        '''        
        pass

    def __eq__(self, other):
        '''
        A variable is equal to other if other is not a variable or they share the same representation
        '''

        pass

    def __ne__(self, other):
        '''
        A variable is not equal to other if other is a variable and they dont share the same representation
        '''     
        pass

    def mapInto(self, other):
        '''
        Returns a dict of the smallest mapping of variables to sentences that if subsituted 
        into this sentence would make this sentence == other, or None if there is none

        e.g.
        Note: '@symbol' is the Wff, '?symbol' is a variable

        '@and'.mapInto('and(A, B)') == {'@and':'and(A, B)'}
        '@and(A)'.mapInto('and(A, B)') == {'@and':'and', 'A':'(A, B)'}
        '@and(A)'.mapInto('and(or(A, C), B)') == {'@and':'and', 'A':'(or(A, C), B)'}
        '@and(A)'.mapInto('and(or(D, C), B)') == None
        '@and(?x)'.mapInto('and(or(D, C), B)') == {'@and':'and', '?x':'(or(D, C), B)'}
        '@?f(?x)'.mapInto('and(A(a),A(a))') == {'@?f':'and', '?x':'(A(a),A(a))'}
        '@?f(?X(?x))'.mapInto('and(A(a),A(a))') == {'@?f':'and', '?X(?x)':'(A(a),A(a))'}
        '?X(?x)'.mapInto('(A(a),A(a))') == {}


        '''
        return {self: other}    


class Variable(Sentence):
    '''
    A variable is a placeholder in a sentence that matches any sentence or wff
    '''

    def __init__(self, name = 'A'):
        # The name of the variable, same named variables are considered to be the same variable

        try:
            self._name = name._name
        except AttributeError:
            self._name = ''.join(str(name).split())

        # Not used for Variables
        self._printer = None

        # A variable is an operator with no arguments
        self._op = self
        self._args = ()

    def __repr__(self):
        return '?' + self._name    

    def __str__(self):
        return '?' + self._name

    def __lt__(self, other):
        '''
        A variable is less than a sentence as long as the sentecne cannot be mapped into a variable
        '''

        #Ensure other is not a variable
        return other.mapInto(self) is None

    def __le__(self, other):
        '''
        A variable is always less than or equal to another sentence
        '''        
        # Vacuously true since {self: other} is always a valid mapping
        return True

    def __eq__(self, other):
        '''
        A variable is equal to other if other is not a variable or they share the same representation
        '''

        # Something is a variable if it is less than or equal to a variable
        return not other <= self or str(self) == str(other)

    def __ne__(self, other):
        '''
        A variable is not equal to other if other is a variable and they dont share the same representation
        '''     

        # Something is a variable if it is less than or equal to a variable
        return other <= self and str(self) != str(other)

    def __hash__(self):
        return hash(self._name)

    def __len__(self):
        return 1

    def __getitem__(self, key):
        # Variables have no arguments
        raise IndexError

    def __iter__(self):
        return SentenceIterator(self)

    def __contains__(self, item):
        # Variables contain no arguments
        return False

    def __copy__(self):
        # A copy of a variable is itseelf
        return self

    def __deepcopy__(self, memo):
        # A deep copy of a variable is itseelf
        return Variable(self._name)

    #def op(self):
    #	return self

    def arity(self):
        return 0

    def mapInto(self, other):
        '''
        A variable can map into anything
        '''
        return {self: other}

    def subsitute(self, mapping):
        return self

    def generalize(self):
        # Already generalized
        return Variable(self)

    def getFree(self):
        # This is a free variable
        return set([self])

class Literal(Variable):
    '''
    A literal is the smallest sentence
    '''

    def __repr__(self):
        return self._name    

    def __str__(self):
        return self._name


    def __lt__(self, other):
        '''
        Vacuously false since a literal cannot be mapped except to itsself
        '''
        return False

    def __le__(self, other):
        return self == other

    def __eq__(self, other):
        '''
        A Literal is equal if they have the same representation
        '''
        return str(self._name) == str(other)

    def __ne__(self, other):
        '''
        A Literal is equal if they have the different representation
        '''        
        return str(self) != str(other)	

    def mapInto(self, other):
        '''
        A literal can only map into itsself 
        '''
        if self == other:
            return {self: other}

        return None	

    def generalize(self):
        return Variable(self)

    def getFree(self):
        return set([])

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
        self._cache = {}

    def generate(self, operator, arguments, printer = None):
        '''
        Constructs a sentence using the operator and arguments provided

        @param operator - The main operator of the sentence
        @param arguments - The arguments of the main operator
        @param printer- The sentence printer to use when printing this sentence 
        '''

        # Check if the sentence is in the cache
        if (operator, arguments) in self._cache:
            newSentence = self._cache[(operator, arguments)]
        else:
            newSentence = Sentence(operator, arguments, printer)
            self._cache[(operator, arguments)] = newSentence

        return newSentence

if __name__ == '__main__':
    # This area used for debugging
    pass
