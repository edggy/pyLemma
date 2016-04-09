import proof

class InferenceIterator:
	def __init__(self, inf):
		#self._name = inf._name
		self._conclusion = inf._conclusion
		self._premises = iter(inf._premises)

	def __iter__(self):
		return self

	def next(self):
		try:
			#if self._name:
				#data = self._name
				#self._name = None
				#return data
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
	
	def __str__(self):
		return self._name + '\n' + self._printer(self)
		
	def __repr__(self):
		return self._name + '\n' + self._printer(self)

	def getPremises(self):
		return self._premises
	
	def getConclusion(self):
		return [self._conclusion]
	
	def isValid(self, sen, ref):
		'''
		Checks wheather the sentence is a valid conclusion of the references using this inference rule 
		'''
		# A inference with no conclusion isalways true i.e. from anything you can derive nothing
		if self._conclusion is None:
			return True

		# Create a mapping of variables from the conclusion to the sentence
		conclusionMap = self._conclusion.mapInto(sen)
		if conclusionMap is None:
			# If there is no mapping, then this inference is not valid
			return False

		# put all of the sentences into a list
		senList = []
		for r in ref:
			senList.append(r().getSentence())

		#For each premise we need it to match at least one reference

		mapping = self.makeMapping(conclusionMap, self._premises, senList)
		
		return (mapping is not None)


	

class MetaInference(proof.Proof):
	def __init__(self, prf):
		self._lines = prf._lines
		self._printer = prf._printer
		self._inferences = prf._inferences
		self._proof = prf
		
	def isValid(self, sen, ref):
		# TODO
		raise NotImplemented
	
	