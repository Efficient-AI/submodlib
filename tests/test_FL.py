#Currently it contains test for only evaluate() and marginalGain() of dense because C++ implementaion is currently
#for dense mode only.
import pytest
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import cosine_distances
from sklearn.neighbors import NearestNeighbors
from scipy import sparse
import scipy
from submodlib.functions.facilityLocation import FacilityLocationFunction
from submodlib import ClusteredFunction
from submodlib.helper import create_kernel
import math
import random
from sklearn.datasets import make_blobs
random.seed(1)


@pytest.fixture
def f_1():# A simple easy to calculate test case
    M = np.array([
        [1,3,2],
        [5,4,3],
        [4,7,5]
        ]) 
    obj = FacilityLocationFunction(n=3, sijs=M)
    return obj

@pytest.fixture
def f_2(): #Boundary case of just one element
    M = np.array([-0.78569]) 
    obj = FacilityLocationFunction(n=1, sijs=M)
    return obj

@pytest.fixture
def f_3(): #more realistic test case 
    M = np.array([ 
        [-0.78569, 0.75, 0.9, -0.56, 0.005], 
        [0.00006, 0.400906, -0.203, 0.9765, -0.9], 
        [0.1, 0.3, 0.5, 0.0023, 0.9], 
        [-0.1, 0.1, 0.1405, 0.0023, 0.3], 
        [-0.123456, 0.0789, 0.00456, 0.001, -0.9]
        ]) 
    obj = FacilityLocationFunction(n=5, sijs=M)
    return obj



'''This is the similarity matrix corrosponding to data matrix created in f_5() below
[[ 1.        ,  0.18480505,  0.31649794,  0.01689587,  0.34060725],
[ 0.18480505,  1.        ,  0.32673257, -0.09584317, -0.03871451],
[ 0.31649794,  0.32673257,  1.        , -0.01977083,  0.14792658],
[ 0.01689587, -0.09584317, -0.01977083,  1.        ,  0.94295957],
[ 0.34060725, -0.03871451,  0.14792658,  0.94295957,  1.        ],]
'''
@pytest.fixture
def f_5():
    data=np.array([
    [100, 21, 365, 5], 
    [57, 18, -5, -6], 
    [16, 255, 68, -8], 
    [2,20,6, 2000], 
    [12,20,68, 200]
    ])
    obj = FacilityLocationFunction(n=5, data=data, mode="dense", metric="cosine")
    return obj

@pytest.fixture
def f_6():
    data=np.array([
    [100, 21, 365, 5], 
    [57, 18, -5, -6], 
    [16, 255, 68, -8], 
    [2,20,6, 2000], 
    [12,20,68, 200]
    ])

    obj = FacilityLocationFunction(n=5, data=data, mode="sparse", metric="cosine")
    return obj

@pytest.fixture
def f_7():
    data=np.array([
    [100, 21, 365, 5], 
    [57, 18, -5, -6], 
    [16, 255, 68, -8], 
    [2,20,6, 2000], 
    [12,20,68, 200]
    ])

    num_cluster=2
    obj = FacilityLocationFunction(n=5, data=data, mode="clustered", metric="euclidean", num_cluster=num_cluster)
    return obj

@pytest.fixture
def f_test_content(): #Using the data in Basic_Usage Notebook for testing (tests 8,9,10)       
    num_clusters = 10
    cluster_std_dev = 4
    points, cluster_ids = make_blobs(n_samples=500, centers=num_clusters, n_features=2, cluster_std=cluster_std_dev, center_box=(0,100))
    data = list(map(tuple, points))
    dataArray = np.array(data)
    #Set1
    cluster1Indices = [index for index, val in enumerate(cluster_ids) if val == 1]
    subset1 = random.sample(cluster1Indices, 6)
    #Set2
    subset2 = []
    for i in range(6):
        #find the index of first point that belongs to cluster i
        diverse_index = cluster_ids.tolist().index(i)
        subset2.append(diverse_index)
    
    return (dataArray, subset1, subset2, cluster_ids)

@pytest.fixture
def f_8(f_test_content): #For C++ Dense VS Python Dense
    dataArray, subset1, subset2, _ = f_test_content
    set1 = set(subset1[:-1])
    set2 = set(subset2[:-1])
    obj1 = FacilityLocationFunction(n=500, data=dataArray, mode="dense", metric="euclidean")
    _, K_dense = create_kernel(dataArray, 'dense','euclidean')
    obj2 = FacilityLocationFunction(n=500, sijs = K_dense)
    return (obj1, obj2)

@pytest.fixture
def f_9(f_test_content): #For C++ Sparse VS Python Sparse
    dataArray, subset1, subset2, _ = f_test_content
    set1 = set(subset1[:-1])
    set2 = set(subset2[:-1])
    obj1 = FacilityLocationFunction(n=500, data=dataArray, mode="sparse", metric="euclidean", num_neigh=10)
    _, K_dense = create_kernel(dataArray, "sparse",'euclidean', num_neigh=10)
    obj2 = FacilityLocationFunction(n=500, sijs = K_dense, num_neigh=10)
    return (obj1, obj2)


@pytest.fixture
def f_10(f_test_content): #For FL clustered mode VS ClusteredFunction (When clusterng is done internally)
    dataArray, subset1, subset2, cluster_ids = f_test_content
    set1 = set(subset1[:-1])
    set2 = set(subset2[:-1])
    obj1 = FacilityLocationFunction(n=500, data=dataArray, mode="clustered", metric="euclidean", num_cluster=10)
    obj2 = ClusteredFunction(n=500, f_name='FacilityLocation', metric='euclidean', data=dataArray, num_cluster=10)
    return (obj1, obj2)



@pytest.fixture
def f_11(f_test_content): #For FL clustered mode VS ClusteredFunction (When clusterng is done internally)
    dataArray, subset1, subset2, cluster_ids = f_test_content
    set1 = set(subset1[:-1])
    set2 = set(subset2[:-1])
    obj1 = FacilityLocationFunction(n=500, data=dataArray, mode="clustered", metric="euclidean", num_cluster=10)
    obj2 = ClusteredFunction(n=500, f_name='FacilityLocation', metric='euclidean', data=dataArray, num_cluster=10)
    return (obj1, obj2)

@pytest.fixture
def f_12(f_test_content): #For FL clustered mode VS ClusteredFunction (When clusters are provided by user)
    dataArray, subset1, subset2, cluster_ids = f_test_content
    set1 = set(subset1[:-1])
    set2 = set(subset2[:-1])
    obj1 = FacilityLocationFunction(n=500, data=dataArray, cluster_lab=cluster_ids.tolist(), mode="clustered", metric="euclidean", num_cluster=10)
    obj2 = ClusteredFunction(n=500, f_name='FacilityLocation', metric='euclidean', data=dataArray, cluster_lab=cluster_ids.tolist(), num_cluster=10)
    return (obj1, obj2)


class TestFL:

    #Testing wrt similarity matrix
    def test_1_1(self, f_1):
        X = {1}
        assert f_1.evaluate(X)==14

    def test_1_2(self, f_1):
        X = {0,2}
        assert f_1.evaluate(X)==12

    def test_1_3(self, f_1):
        X = {0,2}
        item =1
        assert f_1.marginalGain(X, item)==3

    def test_2_1(self, f_2):
        X = {0}
        assert math.isclose(round(f_2.evaluate(X),5), -0.78569)

    
    def test_2_2(self, f_2):
        X = {0}
        item = 0
        assert f_2.marginalGain(X, item)==0

    def test_3_1(self, f_3):
        X = {0,2,4}
        assert math.isclose(round(f_3.evaluate(X),5), 2.10462)
    
    def test_3_2(self, f_3):
        X = {1,3}
        assert math.isclose(round(f_3.evaluate(X),4), 2.2054)

    def test_3_3(self, f_3):
        X = {0,2,4}
        item =1
        assert math.isclose(round(f_3.marginalGain(X, item),6), 0.475186)


    #Testing wrt data
    def test_5_1(self, f_5): 
        X = {1}
        assert math.isclose(round(f_5.evaluate(X),2), 1.38)
    
    def test_5_2(self, f_5):
        X = {0,2}
        assert math.isclose(round(f_5.evaluate(X),2), 2.68)

    def test_5_3(self, f_5):
        X = {0,2}
        item = 1
        assert math.isclose(round(f_5.marginalGain(X, item),3), 0.673)

    def test_6_1(self, f_6): 
        X = {1}
        assert math.isclose(round(f_6.evaluate(X),2), 1.38)
    
    def test_6_2(self, f_6):
        X = {0,2}
        assert math.isclose(round(f_6.evaluate(X),2), 2.68)

    def test_6_3(self, f_6):
        X = {0,2}
        item = 1
        assert math.isclose(round(f_6.marginalGain(X, item),3), 0.673)

    def test_7_1(self, f_7): 
        X = {1}
        assert math.isclose(round(f_7.evaluate(X),2), 1)
    
    def test_7_2(self, f_7):
        X = {0,2}
        assert math.isclose(round(f_7.evaluate(X),2), 2)

    def test_7_3(self, f_7):
        X = {0,2}
        item = 1
        assert math.isclose(round(f_7.marginalGain(X, item),2), 1)

    def test_8_1(self, f_test_content, f_8): #eval on set1
        obj1, obj2 = f_8
        dataArray, subset1, subset2, _ = f_test_content
        set1 = set(subset1[:-1])
        set2 = set(subset2[:-1])
        assert math.isclose(round(obj1.evaluate(set1),2), round(obj2.evaluate(set1),2))

    def test_8_2(self, f_test_content, f_8):#eval on set2
        obj1, obj2 = f_8
        dataArray, subset1, subset2, _ = f_test_content
        set1 = set(subset1[:-1])
        set2 = set(subset2[:-1])
        assert math.isclose(round(obj1.evaluate(set2),2), round(obj2.evaluate(set2),2))

    def test_8_3(self, f_test_content, f_8):#marginal on same cluster
        obj1, obj2 = f_8
        dataArray, subset1, subset2, _ = f_test_content
        set1 = set(subset1[:-1])
        set2 = set(subset2[:-1])
        assert math.isclose(round(obj1.marginalGain(set1, subset1[-1]),2), round(obj2.marginalGain(set1, subset1[-1]),2))

    def test_8_4(self, f_test_content, f_8):#marginal on different cluster
        obj1, obj2 = f_8
        dataArray, subset1, subset2, _ = f_test_content
        set1 = set(subset1[:-1])
        set2 = set(subset2[:-1])
        assert math.isclose(round(obj1.marginalGain(set1, subset2[-1]),2), round(obj2.marginalGain(set1, subset2[-1]),2))

    def test_9_1(self, f_test_content, f_9): #eval on set1
        obj1, obj2 = f_9
        dataArray, subset1, subset2, _ = f_test_content
        set1 = set(subset1[:-1])
        set2 = set(subset2[:-1])
        assert math.isclose(round(obj1.evaluate(set1),2), round(obj2.evaluate(set1),2))

    def test_9_2(self, f_test_content, f_9):#eval on set2
        obj1, obj2 = f_9
        dataArray, subset1, subset2, _ = f_test_content
        set1 = set(subset1[:-1])
        set2 = set(subset2[:-1])
        assert math.isclose(round(obj1.evaluate(set2),2), round(obj2.evaluate(set2),2))

    def test_9_3(self, f_test_content, f_9):#marginal on same cluster
        obj1, obj2 = f_9
        dataArray, subset1, subset2, _ = f_test_content
        set1 = set(subset1[:-1])
        set2 = set(subset2[:-1])
        assert math.isclose(round(obj1.marginalGain(set1, subset1[-1]),2), round(obj2.marginalGain(set1, subset1[-1]),2))

    def test_9_4(self, f_test_content, f_9):#marginal on different cluster
        obj1, obj2 = f_9
        dataArray, subset1, subset2, _ = f_test_content
        set1 = set(subset1[:-1])
        set2 = set(subset2[:-1])
        assert math.isclose(round(obj1.marginalGain(set1, subset2[-1]),2), round(obj2.marginalGain(set1, subset2[-1]),2))
    

    def test_10_1(self, f_test_content, f_10): #eval on set1
        obj1, obj2 = f_10
        dataArray, subset1, subset2, _ = f_test_content
        set1 = set(subset1[:-1])
        set2 = set(subset2[:-1])
        assert math.isclose(round(obj1.evaluate(set1),2), round(obj2.evaluate(set1),2))

    def test_10_2(self, f_test_content, f_10):#eval on set2
        obj1, obj2 = f_10
        dataArray, subset1, subset2, _ = f_test_content
        set1 = set(subset1[:-1])
        set2 = set(subset2[:-1])
        assert math.isclose(round(obj1.evaluate(set2),2), round(obj2.evaluate(set2),2))

    def test_10_3(self, f_test_content, f_10):#marginal on same cluster
        obj1, obj2 = f_10
        dataArray, subset1, subset2, _ = f_test_content
        set1 = set(subset1[:-1])
        set2 = set(subset2[:-1])
        assert math.isclose(round(obj1.marginalGain(set1, subset1[-1]),2), round(obj2.marginalGain(set1, subset1[-1]),2))

    def test_10_4(self, f_test_content, f_10):#marginal on different cluster
        obj1, obj2 = f_10
        dataArray, subset1, subset2, _ = f_test_content
        set1 = set(subset1[:-1])
        set2 = set(subset2[:-1])
        assert math.isclose(round(obj1.marginalGain(set1, subset2[-1]),2), round(obj2.marginalGain(set1, subset2[-1]),2))



    def test_11_1(self, f_test_content, f_11): #eval on set1
        obj1, obj2 = f_11
        dataArray, subset1, subset2, _ = f_test_content
        set1 = set(subset1[:-1])
        set2 = set(subset2[:-1])
        assert math.isclose(round(obj1.evaluate(set1),2), round(obj2.evaluate(set1),2))

    def test_11_2(self, f_test_content, f_11):#eval on set2
        obj1, obj2 = f_11
        dataArray, subset1, subset2, _ = f_test_content
        set1 = set(subset1[:-1])
        set2 = set(subset2[:-1])
        assert math.isclose(round(obj1.evaluate(set2),2), round(obj2.evaluate(set2),2))

    def test_11_3(self, f_test_content, f_11):#marginal on same cluster
        obj1, obj2 = f_11
        dataArray, subset1, subset2, _ = f_test_content
        set1 = set(subset1[:-1])
        set2 = set(subset2[:-1])
        assert math.isclose(round(obj1.marginalGain(set1, subset1[-1]),2), round(obj2.marginalGain(set1, subset1[-1]),2))

    def test_11_4(self, f_test_content, f_11):#marginal on different cluster
        obj1, obj2 = f_11
        dataArray, subset1, subset2, _ = f_test_content
        set1 = set(subset1[:-1])
        set2 = set(subset2[:-1])
        assert math.isclose(round(obj1.marginalGain(set1, subset2[-1]),2), round(obj2.marginalGain(set1, subset2[-1]),2))
    
    def test_12_1(self, f_test_content, f_12): #eval on set1
        obj1, obj2 = f_12
        dataArray, subset1, subset2, _ = f_test_content
        set1 = set(subset1[:-1])
        set2 = set(subset2[:-1])
        assert math.isclose(round(obj1.evaluate(set1),2), round(obj2.evaluate(set1),2))

    def test_12_2(self, f_test_content, f_12):#eval on set2
        obj1, obj2 = f_12
        dataArray, subset1, subset2, _ = f_test_content
        set1 = set(subset1[:-1])
        set2 = set(subset2[:-1])
        assert math.isclose(round(obj1.evaluate(set2),2), round(obj2.evaluate(set2),2))

    def test_12_3(self, f_test_content, f_12):#marginal on same cluster
        obj1, obj2 = f_12
        dataArray, subset1, subset2, _ = f_test_content
        set1 = set(subset1[:-1])
        set2 = set(subset2[:-1])
        assert math.isclose(round(obj1.marginalGain(set1, subset1[-1]),2), round(obj2.marginalGain(set1, subset1[-1]),2))

    def test_12_4(self, f_test_content, f_12):#marginal on different cluster
        obj1, obj2 = f_12
        dataArray, subset1, subset2, _ = f_test_content
        set1 = set(subset1[:-1])
        set2 = set(subset2[:-1])
        assert math.isclose(round(obj1.marginalGain(set1, subset2[-1]),2), round(obj2.marginalGain(set1, subset2[-1]),2))


    #Negative Test cases:
    def test_4_1(self): #Non-square dense similarity matrix 
        M = np.array([[1,2,3], [4,5,6]])
        try:
            FacilityLocationFunction(n=2, sijs=M)
        except Exception as e:
            assert str(e)=="ERROR: Dense similarity matrix should be a square matrix if ground and master datasets are same"

    def test_4_2(self): #Inconsistency between n and no of examples in M
        M = np.array([[1,2,3], [4,5,6]])
        try:
            FacilityLocationFunction(n=1, sijs=M)
        except Exception as e:
            assert str(e)=="ERROR: Inconsistentcy between n and no of examples in the given similarity matrix"

    def test_4_3(self): # X not a subset of ground set for evaluate()
        M = np.array([[1,2], [3,4]])
        obj = FacilityLocationFunction(n=2, sijs=M)
        X={0,2}
        try:
            obj.evaluate(X)
        except Exception as e:
            assert str(e)=="ERROR: X is not a subset of ground set"

    def test_4_4(self): # X not a subset of ground set for marginalGain()
        M = np.array([[1,2], [3,4]])
        obj = FacilityLocationFunction(n=2, sijs=M)
        X={0,2}
        try:
            obj.marginalGain(X, 1)
        except Exception as e:
            assert str(e)=="ERROR: X is not a subset of ground set"

    def test_4_5(self): # If sparse matrix is provided but without providing number of neighbors that were used to create it
        data = np.array([[1,2], [3,4]])
        num_neigh, M = create_kernel(data, 'sparse','euclidean', num_neigh=1)
        try:
            FacilityLocationFunction(n=2, sijs=M) #its important for user to pass num_neigh with sparse matrix because otherwise
                                              #there is no way for Python FL and C++ FL to know how many nearest neighours were
                                              #reatined in sparse matrix
        except Exception as e:
            assert str(e)=="ERROR: num_neigh for given sparse matrix not provided"

        
    def test_4_6(self): # n==0
        data = np.array([[1,2], [3,4]])
        num_neigh, M = create_kernel(data, 'sparse','euclidean', num_neigh=1)
        try:
            FacilityLocationFunction(n=0, sijs=M, num_neigh=num_neigh)
        except Exception as e:
            assert str(e)=="ERROR: Number of elements in ground set can't be 0"
    

    



    



    
    





        