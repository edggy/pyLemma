import copy

import util


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

class Sentence:
	'''
	A  finite sequence of symbols from a given alphabet that is part of a formal language
	
	Contains an operator and some number of arguments
	'''
	def __init__(self, op, *args):
		
		# _op is the operator
		self._op = op
		
		# _args is a tuple of arguments
		self._args = args
		
		# Use the default printer by default
		self._printer = util.prefixSentencePrinter

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
		A sentence is less than another sentence if there exists a mapping of variables to sentences such that
		when you make the subsitution in the smaller sentence it equals the larger sentence and the larger 
		sentence cannot be mapped into the smaller one
		'''
		return self <= other and other.mapInto(self) is None

	def __le__(self, other):
		'''
		A sentence is less than or equal to another sentence if there exists a mapping of variables to sentences such that
		when you make the subsitution in the smaller sentence it equals the larger sentence
		'''		
		return self.mapInto(other) is not None

	def __eq__(self, other):
		'''
		Two sentences are equal iff their hashes are equal
		'''
		return self._op == other._op and self._args == other._args

	def __ne__(self, other):
		'''
		Two sentences are not equal iff either their operators are not equal or their arguments are not equal
		'''
		return hash(self) != hash(other)

	def __gt__(self, other):  
		'''

		'''
		# self > other iff other < self
		return other < self

	def __ge__(self, other):
		'''

		'''
		# self >= other iff other <= self
		return other <= self

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
		Returns a dict of the smallest mapping of variables to sentences that if subsituted 
		into this sentence would make this sentence == other, or None if there is none 

		Examples:
		str(a) = 'and(a, b)'
		str(b) = 'and(or(p,q),iff(r,s))'
		a.mapInto(b) == {'a': 'q or p', 'b':'r iff s'}
		'''

		# Check that the main operators and the arity are the same
		if other is None or self.op() != other.op() or self.arity() != other.arity():
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

class Variable(Sentence):
	'''
	A variable is a placeholder in a sentence that matches any sentence or wff
	'''
	
	def __init__(self, name = 'A'):
		# The name of the variable, same named variables are considered to be the same variable
		self._name = ''.join(str(name).split())

	def __repr__(self):
		return self._name    

	def __str__(self):
		return self._name

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

	def op(self):
		return self

	def arity(self):
		return 0

	def mapInto(self, other):
		return {self:other}

	def subsitute(self, mapping):
		return self

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
		return self < other or self == other

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
		return None	

class InvalidSentenceError(Exception):
	pass

if __name__ == '__main__':
	# This area used for debugging
	pass
