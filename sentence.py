class SentenceIterator:
	def __init__(self, sen):
		self._sen = sen
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
	def __init__(self, op, *args):
		self._op = op
		self._args = args
		self._printer = None

	def __repr__(self):
		return str(self)

	def __str__(self):
		if self._printer == None:
			from util import prefixSentencePrinter
			self._printer = prefixSentencePrinter
		return self._printer(self)

	def __lt__(self, other):
		return self.mapInto(other) is not None

	def __le__(self, other):
		return self == other or self < other

	def __eq__(self, other):
		'''
		Two sentences are equal iff their hashes are equal
		'''
		return hash(self) == hash(other)

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
		# TODO: Make better hash
		return hash(str(self))

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
		import copy
		newOp = copy.copy(self._op)
		newArgs = copy.copy(self._args)

		return sentence(newOp, *newArgs)    

	def __deepcopy__(self, memo):
		import copy
		newOp = copy.deepcopy(self._op)
		newArgs = copy.deepcopy(self._args)
		return sentence(newOp, *newArgs)

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
		import util
		for m, n in zip(self, other):
			# For each argument, try to map it into the other argument recursively
			mapping = m.mapInto(n)
			
			# If there is no mapping for a pair of arguments, then there is no maping at all
			if not mapping: return None
			
			result = util.mapMerge(result, mapping)
		return result
	
	def applyFunction(self, function, data = None):
		args = []
		sen = function(self, data)
		for s in sen:
			args.append(s.applyFunction(function, data))
		return Sentence(sen.op(), *args)
			
	
	def subsitute(self, mapping):
		
		if self in mapping:
			return mapping[self]
		
		args = []
		for s in self:
			if s in mapping:
				args.append(mapping[s])
			else:
				args.append(s.subsitute(mapping))
				
		sen = Sentence(self.op(), *args)
		sen._printer = self._printer
		return sen

	def op(self):
		return self._op

	def setPrinter(self, printer):
		self._printer = printer
		for arg in self:
			arg.setPrinter(printer)

	def arity(self):
		return len(self._args)

class Variable(Sentence):
	def __init__(self, name = 'A'):
		self._name = ''.join(str(name).split())

	def __repr__(self):
		return self._name    

	def __str__(self):
		return self._name

	def __lt__(self, other):
		'''
		Vacuously true since {self: other} is always a valid mapping
		'''
		return True

	def __le__(self, other):
		'''
		Vacuously true since {self: other} is always a valid mapping
		'''        
		return True

	def __eq__(self, other):
		'''
		A variable is equal to other if other is not a variable or they share the same representation
		'''
		return not isinstance(other, Variable) or str(self) == str(other)

	def __ne__(self, other):
		'''
		A variable is not equal to other if other is a variable and they dont share the same representation
		'''        
		return isinstance(other, Variable) and str(self) != str(other)

	def __hash__(self):
		return hash(self._name)

	def __len__(self):
		return 1

	def __getitem__(self, key):
		raise IndexError

	def __iter__(self):
		return SentenceIterator(self)

	def __contains__(self, item):
		return False

	def __copy__(self):
		return self

	def __deepcopy__(self, memo):
		return self    
	
	def op(self):
		return self
	
	def arity(self):
		return 0

	def mapInto(self, other):
		return {self:other}
	
	def subsitute(self, mapping):
		return self
	
class Literal(Variable):
	def __lt__(self, other):
		'''
		Vacuously false since a literal cannot be mapped except to itsself
		'''
		return False
	
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
	
	def mapInto(self, other):
		return None	

class InvalidSentenceError(Exception):
	pass

if __name__ == '__main__':
	def infix(sen):
		if isinstance(sen, Variable):
			return str(sen)
		try:
			first = infix(sen[0])
		except IndexError:
			first = str(sen)
		second = str(sen.op())
		try:
			third = infix(sen[1])
		except IndexError:
			third = str(sen)
		return '(' + first + ' ' + second + ' ' + third + ')'

	import util

	a = Variable('A')
	b = Variable('B')
	c = Variable('C')
	sen = Sentence('&', a, b)
	sen2 = Sentence('|', sen, c)
	print sen
	print sen2
	print infix(sen2)
	sen3 = util.prefixSentenceParser('or(and(A, B), C)')
	print sen3
	sen3.setPrinter(util.infixSentencePrinter)
	print sen3
	
	mapIntoTest = []
	mapIntoTest.append((util.prefixSentenceParser('or(and(A, B), C)'), util.prefixSentenceParser('or(and(P, Q), R)')))
	mapIntoTest.append((util.prefixSentenceParser('or(and(A, B), C)'), util.prefixSentenceParser('and(and(P, Q), R)')))
	mapIntoTest.append((util.prefixSentenceParser('or(and(A, B), C)'), util.prefixSentenceParser('or(and(P, Q), if(P,Q))')))
	mapIntoTest.append((util.prefixSentenceParser('or(and(A, B), A)'), util.prefixSentenceParser('or(and(P, Q), if(P,Q))')))
	mapIntoTest.append((util.prefixSentenceParser('or(and(A, B), A)'), util.prefixSentenceParser('or(and(if(P,Q), Q), if(P,Q))')))
	mapIntoTest.append((util.prefixSentenceParser('and(and(A, B), A)'), util.prefixSentenceParser('and(and(and(P,Q), Q), and(P,Q))')))
	
	for a,b in mapIntoTest:
		print a, b, a.mapInto(b)
	#import copy
	#print copy.copy(sen2)
	#print copy.deepcopy(sen2)

'''
package verifier.impl;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

import verifier.Sentence;
import verifier.Variable;

public abstract class AbstractSentence implements Sentence {
	/**
	 * 
	 */
	private static final long serialVersionUID = 1324374494088588165L;

	public abstract Sentence clone();

	@Override
	public Map<verifier.Variable, Sentence> mapInto(verifier.Sentence sen) {
		// TODO Auto-generated method stub
		Map<verifier.Variable, Sentence> result = new HashMap<verifier.Variable, Sentence>();
		if(this instanceof verifier.Variable) {
			result.put((Variable) this, sen);
			return result;
		}
		if(getOperator() != null) {
			if(!getOperator().equals(sen.getOperator())) return null;
		}
		else if(sen.getOperator() != null) return null;
		if(this.parts().size() != sen.parts().size()) return null;
		Iterator<Sentence> thisPartsi = this.parts().iterator();
		Iterator<Sentence> senPartsi = sen.parts().iterator();
		while(thisPartsi.hasNext() && senPartsi.hasNext()) {
			Sentence thisPart = thisPartsi.next();
			Sentence senPart = senPartsi.next();
			Map<verifier.Variable, Sentence> m = thisPart.mapInto(senPart);
			if(m == null) return null;
			result = Util.mapMerge(result, m);
			if(result == null) return null;
		}
		return result;
	}

	@Override
	public boolean canMapInto(verifier.Sentence sen) {
		return mapInto(sen) != null;
	}

	@Override
	public boolean equals(Object o) {
		if(!(o instanceof Sentence)) return false;
		Sentence s = (Sentence)o;
		if(this.getOperator() == null) {
			if(s.getOperator() != null) return false;
		}
		else {
			if(!this.getOperator().equals(s.getOperator())) {
				return false;
			}
		}
		return this.parts().equals(s.parts());
	}

	@Override
	public int hashCode() {
		return this.toString().hashCode();
	}
}
'''