# graphCutMutualInformation.py
# Author: Vishal Kaushal <vishal.kaushal@gmail.com>
import numpy as np
import scipy
from .setFunction import SetFunction
import submodlib_cpp as subcp
from submodlib_cpp import GraphCutMutualInformation 
from submodlib.helper import create_kernel

class GraphCutMutualInformationFunction(SetFunction):
	"""Implementation of the Graph Cut Mutual Information (GCMI) function.

	Given a :ref:`functions.submodular-mutual-information` function, Graph Cut Mutual Information function is its instantiation using a :class:`~submodlib.functions.graphCut.GraphCutFunction`. Mathematically, it takes the following form:

	.. math::
			I_f(A; Q) = 2\\lambda \\sum\\limits_{i \\in A} \\sum\\limits_{j \\in Q} s_{ij}
	
	.. note::
			GCMI lies at one end of the spectrum favoring only query-relevance. Thus it models a pure retrieval function.
		
	.. note::
			The graph-cut based query-relevance term in :cite:`vasudevan2017query,lin2012submodularity,li2012multi` is actually GCMI.
	
	Parameters
	----------

	n : int
		Number of elements in the ground set. Must be > 0.
	
	num_queries : int
		Number of query points in the target.

	query_sijs : numpy.ndarray, optional
		Similarity kernel between the ground set and the queries. Shape: n X num_queries. When not provided, it is computed using imageData, queryData and metric.
	
	imageData : numpy.ndarray, optional
		Matrix of shape n X num_features containing the ground set data elements. imageData[i] should contain the num-features dimensional features of element i. Mandatory, if either if image_sijs or private_sijs is not provided. Ignored if both image_sijs and private_sijs are provided.
	
	queryData : numpy.ndarray, optional
		Matrix of shape num_queries X num_features containing the query elements. queryData[i] should contain the num-features dimensional features of query i. It is optional (and is ignored if provided) if query_sijs has been provided.

	metric : str, optional
		Similarity metric to be used for computing the similarity kernels. Can be "cosine" for cosine similarity or "euclidean" for similarity based on euclidean distance. Default is "cosine". 
	
	"""

	def __init__(self, n, num_queries, query_sijs=None, imageData=None, queryData=None, metric="cosine"):
		self.n = n
		self.num_queries = num_queries
		self.metric = metric
		self.query_sijs = query_sijs
		self.imageData = imageData
		self.queryData = queryData
		self.cpp_obj = None
		self.cpp_query_sijs = None
		self.cpp_content = None
		self.effective_ground = None

		if self.n <= 0:
			raise Exception("ERROR: Number of elements in ground set must be positive")

		if self.num_queries < 0:
			raise Exception("ERROR: Number of queries must be >= 0")

		if self.metric not in ['euclidean', 'cosine']:
			raise Exception("ERROR: Unsupported metric. Must be 'euclidean' or 'cosine'")

		if type(self.query_sijs) != type(None): # User has provided query kernel
			if type(self.query_sijs) != np.ndarray:
				raise Exception("Invalid query kernel type provided, must be ndarray")
			if np.shape(self.query_sijs)[0]!=self.n or np.shape(self.query_sijs)[1]!=self.num_queries:
				raise Exception("ERROR: Query Kernel should be n X num_queries")
			if (type(self.imageData) != type(None)) or (type(self.queryData) != type(None)):
				print("WARNING: similarity query kernel found. Provided image and query data matrices will be ignored.")
		else: #similarity query kernel has not been provided
			if (type(self.imageData) == type(None)) or (type(self.queryData) == type(None)):
				raise Exception("Since query kernel is not provided, data matrices are a must")
			if np.shape(self.imageData)[0]!=self.n:
				raise Exception("ERROR: Inconsistentcy between n and no of examples in the given image data matrix")
			if np.shape(self.queryData)[0]!=self.num_queries:
				raise Exception("ERROR: Inconsistentcy between num_queries and no of examples in the given query data matrix")
			
		    #construct queryKernel
			self.query_sijs = np.array(subcp.create_kernel_NS(self.queryData.tolist(),self.imageData.tolist(), self.metric))
		
		#Breaking similarity matrix to simpler native data structures for implicit pybind11 binding
		self.cpp_query_sijs = self.query_sijs.tolist() #break numpy ndarray to native list of list datastructure
		
		if type(self.cpp_query_sijs[0])==int or type(self.cpp_query_sijs[0])==float: #Its critical that we pass a list of list to pybind11
																			#This condition ensures the same in case of a 1D numpy array (for 1x1 sim matrix)
			l=[]
			l.append(self.cpp_query_sijs)
			self.cpp_query_sijs=l

		self.cpp_obj = GraphCutMutualInformation(self.n, self.num_queries, self.cpp_query_sijs)
		self.effective_ground = set(range(n))

	