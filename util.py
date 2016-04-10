def prefixSentenceParser(string, variable = True):
	from sentence import Sentence
	from sentence import Variable
	from sentence import Literal
	from sentence import InvalidSentenceError
	
	if variable:
		init = Variable
	else:
		init = Literal
	# string = 'or(and(A, B), C)'

	# Remove all the whitespace in the string
	string = "".join(string.split())
	
	parenCount = len(string.replace('(', '')) - len(string.replace(')', ''))
	if parenCount > 0:
		raise InvalidSentenceError('Unmatched Close Parentheses')
	elif parenCount < 0:
		raise InvalidSentenceError('Unmatched Open Parentheses')
	
	# find the first open paren
	firstP = string.find('(')

	if firstP < 0:
		# if there is no open paren, then this is a variable
		# 'A'
		return init(string)

	elif firstP == 0:
		# if the open paren is the first character, then this is also a variable surrounded by parens
		# '(A)'
		
		return init(string[1:-1])

	# the operator is everthing before the first open paren
	op = Literal(string[:firstP])

	# take the operator and its parens out of the string
	string = string[firstP+1:-1]
	tokens = string.split(',')
	if len(tokens) == 1:
		# No commas
		var = init(string)
		return Sentence(op, var)

	# list of the arguments as sentences or variables
	args = []

	# the number of open paren that haven't been closed
	openCount = 0

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
	
	# Strip all the lines
	lines = map(lambda a: a.strip(), lines)
	
	# Remove all blank lines
	lines = filter(lambda a: not len(a) == 0, lines)
	
	# The name is the first line
	name = lines.pop(0)

	# The conclusion is the last line
	conclusion = sentenceParser(lines.pop())
	
	# Each other line is a sentence of the premises
	premises = [sentenceParser(i) for i in lines]
	
	return Inference(name, conclusion, premises)


def defaultProofParser(string, sentenceParser = None, inferenceParser = None):
	import os
	path = os.path.dirname(os.path.realpath(__file__))
	filename = None	
	try:
		with open(string) as f:
			path = os.path.dirname(os.path.realpath(string))
			filename = os.path.join(path, string)
			string = f.read()
			
			
	except:
		pass
	try:
		# Try to read a file if it is one
		string = string.read()
		path = os.path.dirname(os.path.realpath(string.name))
		filename = os.path.join(path, string.name)
		
	except:
		pass	
	# Set the default parders
	if sentenceParser is None: sentenceParser = prefixSentenceParser
	if inferenceParser is None: inferenceParser = defaultInferenceParser
	
	def init(string, data):
		# The initial state

		if string.startswith(data['include']):
			filename = os.path.join(data['path'], string[len(data['include']):].strip())
			with open(filename) as f:
				for n, line in enumerate(reversed(f.read().split('\n'))):
					data['queue'].appendleft((line, n, filename))
		
		else:	
			# Set the state to the line
			data['state'] = string.strip().lower()	
	
	def inf(string, data):
		# We are in the inference parsing state
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
			data['curProof'] = None
			return			
		
		if 'curProof' not in data or data['curProof'] is None:
			name = string.strip()
			data['curProof'] = name
			#data['proofs'][name] = {'proof':Proof(), 'lines':{}}
			data['proofs'][name] = Proof(name)
			data['infs'][name] = data['proofs'][name]
			data['curLines'] = {}
			return
		
		curProof = data['proofs'][data['curProof']]
		lines = data['curLines']
		
		toks = string.split('\t')
		
		# Strip all the parts
		toks = map(lambda a: a.strip(), toks)	
		
		# toks[0] = Line number, toks[1] = Sentence, toks[2] = Inference rule name, toks[3] = support step
		
		curSen = sentenceParser(toks[1])
		
		curProof += curSen
		
		lines[toks[0]] = curProof[-1]
		if len(toks) < 2:
			raise LineError
		
		if len(toks) == 2:
			curProof[-1] += data['infs']['Assumption']
		if len(toks) >= 3:
			try:
				curProof[-1] += data['infs'][toks[2]]
			except KeyError as e:
				raise LineError('%s is not a defined inference rule or proof' % e.message)		
		if len(toks) >= 4:
			try:
				for i in toks[3].split(','):
					curProof[-1] += lines[i.strip()]
			except KeyError as e:
				raise LineError('%s is not a line' % e.message)

		
	fsm = {None:init, '':init, 'inference':inf, 'proof':prf}
	
	from collections import deque
	
	linequeue = deque()
	
	for n, line in enumerate(string.split('\n')):
	        linequeue.append((line, n, filename))
	
	
	
	data = {'queue':linequeue, 'proofs':{}, 'infs':{'Assumption':defaultInferenceParser('Assumption\nA')}, 'state': None, 'include':'include', 'path':path}
	
	from sentence import InvalidSentenceError

	while len(data['queue']) > 0:
		line, n, filename = data['queue'].popleft()
		try:
			# Ignore everything after a '#'
			line = line.split('#')[0].strip()
			if len(line) != 0:
				fsm[data['state']](line, data)
		except (InvalidSentenceError, LineError) as e:
			e.message = 'Error in "%s", line %d:\t%s' % (filename, n+1, e.message)
			raise LineError(e.message)
	
	return data['proofs']
			
		
		

def prefixSentencePrinter(sen):
	if sen.arity() == 0:
		return str(sen.op())
	string = ''
	string += str(sen.op())
	string += '('
	first = True
	for arg in sen:
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

	return prefixSentencePrinter(sen)

def defaultProofPrinter(p, printedInferences = set([])):
	res = ''
	inferences = p.getInferences()
	for inf in inferences:
		if inf not in printedInferences:
			res += str(inferences[inf]) + '\n\n'
			printedInferences.add(inf)
	
	res += 'proof\n' + p.name() + '\n'
	for n, i in enumerate(p):
		i._num = n
		res += str(i) + '\n'
	return res + 'done'

def defaultInferencePrinter(inf):
	res = 'inference\n'
	for line in inf:
		res += str(line) + '\n'
	return res + 'done'

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

class LineError(Exception):
	pass

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