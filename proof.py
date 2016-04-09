
import line

class Proof:
	'''
	A finite sequence of sentences (called well-formed formulas in the case
	of a formal language) each of which is an axiom, an assumption, or
	follows from the preceding sentences in the sequence by a rule of
	inference
	'''	
	
	def __init__(self, name, proofPrinter = None):
		self._name = name
		self._lines = []
		if proofPrinter:
			self._printer = proofPrinter
		else:
			import util
			self._printer = util.defaultProofPrinter		
		
		self._inferences = {}
		
	def name(self):
		return self._name
	
	def addLine(self):
		'''
		Add an empty line to the end of the proof
		'''
		self._lines.append(line.Line(self))
		
	def addLines(self, amount):
		'''
		Adds an **amount** of empty lines to the end of the proof
		'''
		for i in range(amount):
			self.addLine()
	
	def insertLine(self, index):
		'''
		Inserts an empty line before **index**
		'''
		self._lines.insert(index, None)
	
	def insertLines(self, index, amount):
		'''
		Adds an **amount** of empty lines before **index**
		'''
		for i in range(amount):
			self._lines.insert(index + i, None)
	
	def removeLine(self, line_num):
		#lines.remove(line_num);
		raise NotImplemented
	
	def removeLines(self, line_num, amount):
		#for(int i = 0; i < amount; i++) {
			#removeLine(line_num);
		#}
		raise NotImplemented
	
	def setSentence(self, line_num, sen):
		self._lines[line_num] += sen

	#@Override
	#public void addSentences(int line_num, List<verifier.Sentence> sens) throws IndexOutOfBoundsException {
		#int count = 0;
		#for(verifier.Sentence sen : sens) {
			#addSentence(line_num + count++, sen);
		#}
	#}

	def getSentence(self, line_num):
		return self._lines[line_num].getSentence()

	#@Override
	#public List<verifier.Sentence> getSentences(int line_num, int amount) throws IndexOutOfBoundsException {
		#List<verifier.Sentence> ret = new LinkedList<verifier.Sentence>();
		#List<verifier.Line> sub = lines.subList(line_num, line_num + amount);
		#for(verifier.Line line : sub) {
			#ret.add(line.s);
		#}
		#return ret;
	#}

	#@Override
	#public void removeSentence(int line_num) throws IndexOutOfBoundsException {
		#lines.get(line_num).s = null;
	#}

	#@Override
	#public void removeSentences(int line_num, int amount) throws IndexOutOfBoundsException {
		#for(int i = 0; i < amount; i++) {
			#removeSentence(line_num + i);
		#}
	#}

	def setInference(line_num, inf):
		raise NotImplemented
	#@Override
	#public void addInference(int line_num, verifier.Inference inf) throws IndexOutOfBoundsException {
		#lines.get(line_num).i = inf;
		
	#}

	#@Override
	#public verifier.Inference getInference(int line_num) throws IndexOutOfBoundsException {
		#return lines.get(line_num).i;

	#}

	#@Override
	#public void removeInference(int line_num) throws IndexOutOfBoundsException {
		#lines.get(line_num).i = null;
	#}

	def addSupport(line_num, ref):
		raise NotImplemented
		#if not isinstance(ref, Line):
		#	ref = self._lines[ref]
		#self._lines[line_num].addSupport(ref)
		
	#@Override
	#public void addReference(int line_num, verifier.Reference ref) throws IndexOutOfBoundsException {
		#Line curLine = lines.get(line_num);
		#if(curLine.r == null) curLine.r = ref;
		#curLine.r.addReferences(ref.getReference());
	#}
	
	#@Override
	#public void addReference(int line_num, int ref_line) throws IndexOutOfBoundsException {
		#verifier.Reference ref = new Reference();
		#ref.addReference(lines.get(ref_line));
		
		#addReference(line_num, ref);
	#}

	#@Override
	#public verifier.Reference getReference(int line_num) throws IndexOutOfBoundsException {
		#return lines.get(line_num).r;
	#}

	#public void removeReference(int line_num, int ref_line) throws IndexOutOfBoundsException {
		#verifier.Reference curRef = lines.get(line_num).r;
		#if(curRef == null) return;
		#curRef.removeReference(lines.get(ref_line));
	#}
	
	#@Override
	#public void removeReferences(int line_num) throws IndexOutOfBoundsException {
		#lines.get(line_num).r = null;
	#}

	def verify(self):
		'''
		Verifies that the current proof is valid, i.e. each line validly follows from the previous lines
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
			
		
		# If there are no errors, return 1
		if err_line is None:		
			return 1
		
		# Since this is an invalid proof, first set all the line numbers to None
		for line in self._lines:
			line._num = None
			
		# Then return -err_line, so the user can debug
		return -err_line

	def isValid(self, sen, ref):
		'''
		Given a sentence and a set of reference lines, check that this proof proves 
		that the sentence is deductively follows from the reference lines
		'''
		
		# Check that this proof is valid, if it is not then we canot check anything
		if self.verify() < 1:
			return False
		
		metaAssumption = None
		if sen.op() == '|-':
			metaAssumption = sen[0]
			
			# We are trying to prove the second part
			sen = sen[1]
		
		# put all of the sentences into a list
		senList = []
		for r in ref:
			senList.append(r().getSentence())			

		prevSens = []
		metaSen = None
		for s in self:
			# Assume s is the conclusion
			curSen = s.getSentence()
			curInf = s.getInference()
			
			# TODO: use other lines not tle last line as the conclusion
			conclusion = curInf.getConclusion()[-1]
			
			from sentence import Variable
			
			
			
			# Check if s is an assumption
			if len(curInf.getPremises()) == 0 and conclusion <= Variable():
				
				# Check if the current sentence can map into the metaAssumption
				metaConclusionMap = curSen.mapInto(metaAssumption)
				if metaConclusionMap:
					if metaSen:
						prevSens.append(metaSen)
					metaSen = curSen
				else:
					prevSens.append(curSen)
			
			#if metaConclusionMap:
					
				# Try to map the current sentence can map into the metaAssumption
				#metaAssumption = None
				
				
			# Check if the current sentence can map into the conclusion
			conclusionMap = curSen.mapInto(sen)
			if conclusionMap and metaSen:
				# Try to map the assumptions to the senList
				mapping = self.makeMapping(conclusionMap, prevSens, senList)
				if mapping:
					# If there is a mapping then we are done
					return True
		return False
	
	def makeMapping(self, conclusionMap, premises, sentences, exact = True):
		'''
		Try to map all of the premises into the sentences in any combination while being constrained by the current conclusionMap
	
		conclusionMap - The current mapping of variables into sentences
		premises - A list of premises
		sentences - A list of sentences to be mapped into
		'''
		# If there are no premises, there is nothing else to map
		if premises is None or len(premises) == 0:
			return conclusionMap
	
		# If there are more premises than sentences, there is no mapping
		if (exact and len(premises) != len(sentences)) or len(premises) > len(sentences):
		        return None
		
		from collections import deque
	
		premiseQueue = deque(premises)
	
		return self.makeMappingHelper(conclusionMap, premiseQueue, sentences)	
	
	
	def makeMappingHelper(self, conclusionMap, premiseQueue, sentences):
		'''
		Try to map all of the premises into the sentences in any combination while being constrained by the current conclusionMap

		conclusionMap - The current mapping of variables into sentences
		premiseQueue - A queue of the premises
		sentences - A list of sentences to be mapped into
		'''	

		#print conclusionMap, premiseQueue, sentences
		#print premiseQueue.pop()
		# Base case, the queue is empty
		#if premiseQueue.empty():
		#	return conclusionMap
		try:
			# Get the first premise
			curPrem = premiseQueue.pop()
		except IndexError:
			# Base case, the queue is empty
			return conclusionMap

		for curSen in sentences:
			#print 'curPrem =', curPrem
			#print 'curSen =', curSen
			# Try find a mapping of curPrem into curSen
			mapping = curPrem.mapInto(curSen)
			#print 'mapping =', mapping
			if mapping:
				# If a mapping exists
				import util

				# try to merge this mapping into conclusionMap
				merge = util.mapMerge(conclusionMap, mapping)
				#print 'merge =', merge
				if merge:
					# If the merge is successful recursively call makeMappingHelper for the merged map, and the remainder of the premiseQueue
					remainder = self.makeMappingHelper(merge, premiseQueue, sentences)
					#print 'remainder =', remainder
					if remainder:
						# If we can map the remaining premises, this is a valid mapping, return it
						return remainder

		# If we get here then curPrem can't map inro any of the sentences  
		# Put the curPrem back into the queue in case we are still in the recursion
		premiseQueue.append(curPrem)

		# There is no valid mapping
		return None	
	#@Override
	#public int length() {
		#return lines.size();
	#}

	#@Override
	#public int size() {
		#return lines.size();
	#}

	#@Override
	#public verifier.Line getLine(int line_num) throws IndexOutOfBoundsException{
		#return lines.get(line_num);
	#}

	#@Override
	#public List<verifier.Line> getLines() {
		#return new ArrayList<verifier.Line>(lines);
	#}

	#@Override
	#public List<verifier.Line> getLines(int line_num, int amount) throws IndexOutOfBoundsException {
		#List<verifier.Line> l = new ArrayList<verifier.Line>();
		#for(int i = line_num; i < amount; i++) {
			#l.add(lines.get(i));
		#}
		#return l;
	#}
	
	#@Override
	#public Line getLastLine() {
		#return lines.get(lines.size()-1);
	#}
	
	#@Override
	#public String toString() {
		#String res = "";
		#int lineNum = 1;
		#for(Line l : lines) {
			#l.number = lineNum++;
			#res += l + "\n";
		#}
		#return res.substring(0, res.length() - 1);
	#}
	
	def __len__(self):
		'''
		The length of the proof is equal to the number of lines
		'''
		# TODO: don't count empty lines
		return len(self._lines)
	
	def __getitem__(self, key):
		return self._lines[key]
	
	def __setitem__(self, key, value):

		self._lines[key] = value
		
		'''if isinstance(value, Sentence):
			self.setSentence(key, value)
		elif isinstance(value, Inference):
			self.setInference(key, value)
		else:
			self.addSupport(key, value)'''
			
	
	def __iter__(self):
		return iter(self._lines)
	
	def __reversed__(self):
		return reversed(self._lines)
	
	def __str__(self):
		printed = set([])
		ret = ''
		for inf in self._inferences:
			if inf not in printed:
				ret += str(self._inferences[inf]) + '\n'
				printed.add(inf)
		return ret + self._name + '\n' + self._printer(self)		
		
	def __repr__(self):
		return self._name + '\n' + self._printer(self)
	
	def __iadd__(self, value):
		from inference import Inference
		if isinstance(value, Inference) and value.name() not in self._inferences:
			# If we are given an inference not in our map, add it to our map
			self._inferences[value.name()] = value
		elif isinstance(value, str):
			# If we are given a string, look it up in our inference map
			value = self._inferences[value]		
		self.addLine()
		self._lines[-1] += value
		return self
	
	def setPrinter(self, newPrinter):
		self._printer = newPrinter
		
	def getPremises(self):
		# Check if s is an assumption
		#if len(curInf.getPremises()) == 0 and conclusion <= Variable():
		from sentence import Variable
		prems = []
		for l in self._lines:
			inf = l.getInference()
			if len(inf.getPremises()) == 0 and len(inf.getConclusion()) == 1 and inf.getConclusion()[0] <= Variable():
				prems.append(l.getSentence())
		return prems
		#return filter(lambda a: a,map(lambda a: a.getSentence(), self._lines))
	
	def getConclusion(self):
		return map(lambda a: a.getSentence(), self._lines)
	

if __name__ == '__main__':
	import util
	import inference
	
	p = Proof()
	p += util.prefixSentenceParser('if(a,or(b,a))')
	p += util.prefixSentenceParser('a')
	p += util.prefixSentenceParser('or(b,a)')
	#print p
	p[2] += p[0]
	p[2] += p[1]
	#p.__setitem__(1, p.__getitem__(1).__iadd__(p.__getitem__(0)))
	#print p[1]
	#print
	print p
	
	assumption = util.defaultInferenceParser('assumption\na')
	
	mp = util.defaultInferenceParser('MP\nP\nif(P,Q)\nQ')
	mp.setPrinter(util.defaultInferencePrinter)
	print mp
	#p.__setitem__(1, p.__getitem__(1).__iadd__(??))
	p[0] += assumption
	p[1] += 'assumption'
	p[2] += mp
	print p
	print p.isValid()
	
