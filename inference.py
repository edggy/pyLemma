import proof

class InferenceIterator:
	def __init__(self, inf):
		self._name = inf._name
		self._conclusion = inf._conclusion
		self._premises = iter(inf._premises)

	def __iter__(self):
		return self

	def next(self):
		try:
			if self._name:
				data = self._name
				self._name = None
				return data
			data = self._premises.next()
			return data
		except StopIteration:
			if self._conclusion:
				data = self._conclusion
				self._conclusion = None
				return data

			raise StopIteration

class Inference(proof.Proof):
	def __init__(self, name, conclusion = None, premises = None):
		self._name = name
		self._conclusion = conclusion
		self._premises = set(premises)
		
		import util
		self._printer = util.defaultInferencePrinter

	def __iter__(self):
		return InferenceIterator(self)

	def name(self):
		return self._name

	def isValid(self, sen, ref):
		'''
		Checks wheather the sentence is a valid conclusion of the references using this inference rule 
		'''
		# A inference with no conclusion isalways true i.e. from anything you can derive nothing
		if self._conclusion == None:
			return True

		# Create a mapping of variables from the conclusion to the sentence
		conclusionMap = self._conclusion.mapInto(sen)
		if conclusionMap == None:
			# If there is no mapping, then this inference is not valid
			return False

		# put all of the sentences into a list
		senList = []
		for r in ref:
			senList.append(r().getSentence())

		#For each premise we need it to match at least one reference

		mapping = self.makeMapping(conclusionMap, self._premises, senList)
		
		return (mapping is not None)


	def makeMapping(self, conclusionMap, premises, sentences):
		'''
		Try to map all of the premises into the sentences in any combination while being constrained by the current conclusionMap

		conclusionMap - The current mapping of variables into sentences
		premises - A list of premises
		sentences - A list of sentences to be mapped into
		'''
		# If there are no premises, there is nothing else to map
		if premises is None or len(premises) == 0:
			return conclusionMap
		
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

