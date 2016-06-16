import proof

class InferenceIterator:
	'''
	An iterator that goes through each premise and the conclusion of the inference.
	
	Note: 
	The premises may appear in any order
	The conclusion is always last
	'''
	def __init__(self, inf):
		# Keep track of the conclusion and an iterator of the premises
		self._conclusion = inf._conclusion
		self._premises = iter(inf._premises)

	def __iter__(self):
		return self

	def next(self):
		try:
			# Try to get the next premise
			data = self._premises.next()
			return data
		except StopIteration:
			# Otherwise try to get the conclusion
			if self._conclusion:
				data = self._conclusion
				
				# Set the conclusion to None so we know it was used
				self._conclusion = None
				return data

			raise StopIteration

class Inference(proof.Proof):
	def __init__(self, name, conclusion = None, premises = None, printer = None):
		# The name of this Inference rule
		# TODO: Allow a nickname to print
		self.name = name
		
		# The conclusion of this inference rule
		self._conclusion = conclusion
		
		# A set of premises
		self._premises = set(premises)

		# THe printer to print the infrence rule
		self._printer = printer
		if self._printer is None:
			import util
			# Use default printer
			self._printer = util.defaultInferencePrinter

	def __iter__(self):
		# Returns an iterator of itself
		return InferenceIterator(self)

	def __str__(self):
		return self._printer(self)

	def __repr__(self):
		return self._printer(self)
	
	def __eq__(self, other):
		# Two inference rules are equal if the premises are equal and the conclusions are the same
		return self.getPremises() == other.getPremises() and self.getConclusion() == other.getConclusion()

	def getPremises(self):
		'''
		Gets the premises of this inference rule
		
		@return - A set of sentences containing the premises
		'''
		return self._premises

	def getConclusion(self):
		'''
		Gets the conclusions of this inference rule
		
		@return - A list containing the conclusions of this inference rule
		'''
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

		# Put all of the sentences into a list
		senList = []
		for r in ref:
			senList.append(r().getSentence())

		# For each premise we need it to match at least one reference
		mapping = self.makeMapping(conclusionMap, self._premises, senList)

		# Return if a mapping exists
		return (mapping is not None)


