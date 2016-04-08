def prefixSentenceParser(string):
	from sentence import Sentence
	from sentence import Variable
	# string = 'or(and(A, B), C)'

	# Remove all the whitespace in the string
	string = "".join(string.split())
	# find the first open paren
	firstP = string.find('(')

	if firstP < 0:
		# if there is no open paren, then this is a variable
		# 'A'
		return Variable(string)

	elif firstP == 0:
		# if the open paren is the first character, then this is also a variable surrounded by parens
		# '(A)'
		return Variable(string[1:-1])

	# the operator is everthing before the first open paren
	op = string[:firstP]

	# take the operator and its parens out of the string
	string = string[firstP+1:-1]
	tokens = string.split(',')
	if len(tokens) == 1:
		var = Variable(string)
		return Sentence(op, var)

	# list of the arguments as sentences or variables
	args = []

	# the number of open paren that haven't been closed
	openCount = 0

	# The 
	cumStr = ''
	for part in tokens:
		# Check if this is the beginning of an argument
		if len(cumStr) == 0:
			# If it is add it to the end
			cumStr += part
		else:
			# Otherwise seperate it with a comma and then add ir
			cumStr += ',' + part

		# Count the number of unclosed parens
		openCount += part.count('(')
		openCount -= part.count(')')

		# If all the parens match up, then it must be a whole argument
		if openCount == 0:
			# recursively parse the argument
			args.append(prefixSentenceParser(cumStr))

			# reset cumStr to take care of the next part
			cumStr = ''

	res = Sentence(op, *args)
	return res

def defaultInferenceParser(string, sentenceParser = None):
	if sentenceParser is None:
		sentenceParser = prefixSentenceParser

	from inference import Inference

	# Split the sting into lines
	lines = string.split('\n')

	lines = filter(lambda a: not (a.isspace() or len(a) == 0), lines)
	# The name is the first line
	name = lines.pop(0)

	# The conclusion is the last line
	conclusion = sentenceParser(lines.pop())
	premises = [sentenceParser(i) for i in lines]
	#print '79:', name
	#print '80:', premises
	#print '81:', conclusion
	return Inference(name, conclusion, premises)


def defaultProofParser(string, sentenceParser = None, inferenceParser = None):
	if sentenceParser is None: sentenceParser = prefixSentenceParser
	if inferenceParser is None: inferenceParser = defaultInferenceParser
	
	def init(string, data):
		data['state'] = string.strip().lower()	
	
	def inf(string, data):
		if string == 'done':
			inf = inferenceParser(data['curInf'], sentenceParser)
			data['infs'][inf.name()] = inf
			data['curInf'] = None
			data['state'] = None
			return
		
		if 'curInf' in data and data['curInf'] is not None:
			data['curInf'] += '\n' + string
		else:
			data['curInf'] = string
	
	def prf(string, data):
		from proof import Proof
		
		if string == 'done':
			data['state'] = None
			return			
		
		if 'curProof' not in data or data['curProof'] is None:
			name = string.strip()
			data['curProof'] = name
			data['proofs'][name] = Proof()
			return
		
		curProof = data['proofs'][data['curProof']]
		toks = string.split('\t')
		curProof += sentenceParser(toks[1])
		if len(toks) > 2:
			curProof[-1] += data['infs'][toks[2]]
			for i in toks[3].split(','):
				curProof[-1] += int(i)
		else:
			curProof[-1] += data['infs']['assumption']

		
	fsm = {None:init, '':init, 'inference':inf, 'proof':prf}
	
	
	
	
	data = {'proofs':{}, 'infs':{'assumption':defaultInferenceParser('assumption\na')}, 'state': None}
	for line in string.split('\n'):
		
		# Ignore everything after a '#'
		line = line.split('#')[0]
		#print line
		fsm[data['state']](line, data)
		#print data
	
	return data['proofs']
			
		
		

def prefixSentencePrinter(sen):
	string = ''
	string += str(sen._op)
	string += '('
	first = True
	for arg in sen._args:
		if not first:
			string += ',' + str(arg)
		else:
			string += str(arg)
			first = False
	string += ')'
	return string

def infixSentencePrinter(sen):
	string = ''
	if sen.arity() == 2:
		return '(' + str(sen[0]) + ' ' + str(sen.op()) + ' ' + str(sen[1]) + ')'

	return prefixPrinter(sen)

def defaultProofPrinter(p):
	res = ''
	for n, i in enumerate(p):
		i._num = n
		res += str(i) + '\n'
	return res

def defaultInferencePrinter(inf):
	res = ''
	for line in inf:
		res += str(line) + '\n'
	return res

def mapMerge(mappingA, mappingB):
	'''
	Merge two dictionaries such that the result is a superset of both, or None if there is a conflict

	Example:
	mapMerge({}, {B:P|Q}) -> {B:P|Q}
	mapMerge({A:P&Q}, {B:P|Q}) -> {A:P&Q, B:P|Q}
	mapMerge({A:P, B:P|Q}, {B:P|Q}) -> {A:P, B:P|Q}
	mapMerge({A:P, B:P|Q}, {A:P&Q, B:P|Q}) -> None

	'''

	# Base case either map is empty, trivially return the other
	if not mappingA or len(mappingA) == 0: return mappingB
	if not mappingB or len(mappingB) == 0: return mappingA

	from copy import copy

	# Make merge a copy of mappingA
	merge = copy(mappingA)

	# For each entry in mappingB
	for b in mappingB:
		# If it is already in the merge and their values are not equal then no merge exists
		if b in merge and mappingB[b] != merge[b]:
			return None
		# Otherwise add it to the merge
		merge[b] = mappingB[b]

	return merge



'''package verifier.impl;

import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;

import verifier.Sentence;
import verifier.Variable;

public class Util {
	public static Map<verifier.Variable, Sentence> mapMerge(Map<Variable, Sentence> a, Map<Variable, Sentence> b) {
		if(a == null) return b;
		if(b == null) return a;
		Map<verifier.Variable, Sentence> merge = new HashMap<verifier.Variable, Sentence>();
		//For each entry in a
		for(Entry<verifier.Variable, Sentence> e : a.entrySet()) {
			//If b contains it
			if(b.containsKey(e.getKey())) {
				//And they are not equal
				if(!a.get(e.getKey()).equals(b.get(e.getKey()))) {
					//No mapping found
					return null;
				}
			}
			//Put it in the map
			merge.put(e.getKey(), e.getValue());
		}
		//For each entry in b
		for(Entry<verifier.Variable, Sentence> e : b.entrySet()) {
			//If it is not in a (ignore repeats)
			if(!a.containsKey(e.getKey())) {
				//Put it in the map
				merge.put(e.getKey(), e.getValue());
			}
		}
		return merge;
	}
}
'''