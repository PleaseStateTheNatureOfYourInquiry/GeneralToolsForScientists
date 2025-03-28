# distutils: language = c++

import numpy as np
import cython

cdef extern from "DataWranglingToolsCPPCore.cpp":

    pass


cdef extern from "DataWranglingToolsCPPCore.h":

    cdef cppclass DataWranglingToolsCPPCore:
    
        DataWranglingToolsCPPCore () except+
    
        void getSegmentSpecsFromDataValues ( 
            float *, #1 short dataValues [1]
            unsigned int, #2 unsigned int numberOfDataValues
            unsigned int *, #3 unsigned int segmentStartIndices [1]
            unsigned int&, #4 unsigned int& numberOfSegments
            float *, #5 int segmentAmplitudes [1]
            float *, #6 float segmentSlopes [1]
            unsigned int *, #7 unsigned int segmentDurations [1]
            unsigned int *, #8 unsigned int segmentStartIndicesNegative [1]
            unsigned int&, #9 unsigned int& numberOfSegmentsNegative
            unsigned int&, #10 unsigned int& iSteepestNegativeSlopeSegment
            unsigned int&, #11 unsigned int& iSegmentStartIndicesSteepestNegativeSlope
            unsigned int *, #12 unsigned int segmentStartIndicesPositive [1]
            unsigned int&, #13 unsigned int& numberOfSegmentsPositive
            unsigned int&, #14 unsigned int& iSteepestPositiveSlopeSegment
            unsigned int& #15 unsigned int& iSegmentStartIndicesSteepestPositiveSlope
        )

        void getAverageVarAndSD (
            double *, #1 double dataValues [1]
            int, #2 int numberOfValues
            double&, #3 double& averageValue
            double&, #4 double& standardDeviation
            double& #5 double& variance
        )


        void getMedianAndQuantiles (
            double *, #1 double dataValues [1]
            int, #2 int numberOfValues
            double&, #3 double& medianValue
            float, #4 float lowerQuantile
            double&, #5 double& lowerQuantileValue
            float, #6 float upperQuantile
            double& #7 double& upperQuantileValue
        )


        void getNearestValue (
            double *, #1 float dataValues [1]
            unsigned int, #2 unsigned int numberOfValues
            double, #3 float valueToCompare
            int&, #4 unsigned int& iSmallestDifference
            double&, #5 float& smallestDifference
            int #6 int monotonicList
            
        )



cdef DataWranglingToolsCPPCore DataWranglingToolsCPPCoreObject


def getSegmentSpecsFromDataValuesPYtoCPP (dataValues):
    '''
    
    dataValues: 
    
        converted to a short (np.short / int16)

    
    returns tuple:
    
        [0]  numberOfSegments
        [1]  segmentStartIndices [0:numberOfSegments]
        [2]  segmentAmplitudes [0:numberOfSegments]
        [3]  segmentSlopes [0:numberOfSegments]
        [4]  segmentDurations [0:numberOfSegments]
        [5]  numberOfSegmentsNegative
        [6]  segmentStartIndicesNegative [0:numberOfSegmentsNegative]
        [7]  iSteepestNegativeSlopeSegment
        [8]  iSegmentStartIndicesSteepestNegativeSlope
        [9]  numberOfSegmentsPositive
        [10] segmentStartIndicesPositive [0:numberOfSegmentsPositive]
        [11] iSteepestPositiveSlopeSegment
        [12] iSegmentStartIndicesSteepestPositiveSlope
    
    '''

    global DataWranglingToolsCPPCoreObject

    # Make sure the dataValues list is a NumPy array.
    if type (dataValues) == list or dataValues.dtype != 'single':
    
        dataValues = np.asarray (dataValues, dtype = np.single)


    # Make sure the array is stored contiguously.
    if not dataValues.flags ['C_CONTIGUOUS']:
    
        dataValues = np.ascontiguousarray (dataValues)
    
    
    cdef Py_ssize_t numberOfDataValues = dataValues.shape [0]
    cdef float [::1] dataValues_view = dataValues


    cdef unsigned int numberOfSegments = 0
    cdef unsigned int numberOfSegmentsNegative = 0
    cdef unsigned int numberOfSegmentsPositive = 0
    cdef unsigned int iSteepestNegativeSlopeSegment = 0
    cdef unsigned int iSegmentStartIndicesSteepestNegativeSlope = 0
    cdef unsigned int iSteepestPositiveSlopeSegment = 0
    cdef unsigned int iSegmentStartIndicesSteepestPositiveSlope = 0
    

    # Initialise the arrays to the length of the the  dataValues  array.
    
    # It is extremely important that the  segmentAmplitudes  array has the type np.int32 (which is int in C++)! 
    #  This is because the amplitudes are differences in the dataValues, which are of type short (-32768 - +32767), 
    #  hence the maximum difference can be + or -65535 !!!
    segmentAmplitudes = np.ascontiguousarray ( np.zeros (numberOfDataValues, dtype = np.single) )
    cdef float [::1] segmentAmplitudes_view = segmentAmplitudes

    segmentSlopes = np.ascontiguousarray ( np.zeros (numberOfDataValues, dtype = np.single) )
    cdef float [::1] segmentSlopes_view = segmentSlopes

    segmentDurations = np.ascontiguousarray ( np.zeros (numberOfDataValues, dtype = np.uintc) )
    cdef unsigned int [::1] segmentDurations_view = segmentDurations

    segmentStartIndices = np.ascontiguousarray ( np.zeros (numberOfDataValues, dtype = np.uintc ) )
    cdef unsigned int [::1] segmentStartIndices_view = segmentStartIndices
    
    segmentStartIndicesNegative = np.ascontiguousarray ( np.zeros (numberOfDataValues, dtype = np.uintc ) )
    cdef unsigned int [::1] segmentStartIndicesNegative_view = segmentStartIndicesNegative
    
    segmentStartIndicesPositive = np.ascontiguousarray ( np.zeros (numberOfDataValues, dtype = np.uintc ) )
    cdef unsigned int [::1] segmentStartIndicesPositive_view = segmentStartIndicesPositive
    
    
    # Call the C++ core function.
    DataWranglingToolsCPPCoreObject.getSegmentSpecsFromDataValues ( 
        &dataValues_view [0], #1
        numberOfDataValues, #2
        &segmentStartIndices_view [0], #3
        numberOfSegments, #4
        &segmentAmplitudes_view [0], #5
        &segmentSlopes_view [0], #6
        &segmentDurations_view [0], #7
        &segmentStartIndicesNegative_view [0], #8
        numberOfSegmentsNegative, #9
        iSteepestNegativeSlopeSegment, #10
        iSegmentStartIndicesSteepestNegativeSlope, #11
        &segmentStartIndicesPositive_view [0], #12
        numberOfSegmentsPositive, #13
        iSteepestPositiveSlopeSegment, #14
        iSegmentStartIndicesSteepestPositiveSlope #15
    )


    return numberOfSegments, \
           segmentStartIndices [0:numberOfSegments], \
           segmentAmplitudes [0:numberOfSegments], \
           segmentSlopes [0:numberOfSegments], \
           segmentDurations [0:numberOfSegments], \
           numberOfSegmentsNegative, \
           segmentStartIndicesNegative [0:numberOfSegmentsNegative], \
           iSteepestNegativeSlopeSegment, \
           iSegmentStartIndicesSteepestNegativeSlope, \
           numberOfSegmentsPositive, \
           segmentStartIndicesPositive [0:numberOfSegmentsPositive], \
           iSteepestPositiveSlopeSegment, \
           iSegmentStartIndicesSteepestPositiveSlope




def getAverageVarAndSDPYtoCPP (dataValues):
    '''
    
    dataValues: 
    
        converted to a double

    
    returns tuple:
    
        [0]  averageValue
        [1]  standardDeviation
        [2]  variance
    
    '''
    
    global DataWranglingToolsCPPCoreObject

    
    # Make sure the dataValues list is a NumPy array.
    if type (dataValues) == list:
    
        dataValues = np.asarray (dataValues, dtype = np.double)

    else:
    
        dataValues = np.ascontiguousarray (dataValues, dtype = np.double)       


#     # Make sure the array is stored contiguously.
#     if not dataValues.flags ['C_CONTIGUOUS']:
    
#         dataValues = np.ascontiguousarray (dataValues)
    
    
    cdef Py_ssize_t numberOfDataValues = dataValues.shape [0]
    cdef double [::1] dataValues_view = dataValues
    
    cdef double averageValue = 0.
    cdef double standardDeviation = 0.
    cdef double variance = 0.
    
    
    DataWranglingToolsCPPCoreObject.getAverageVarAndSD (
        &dataValues_view [0], #1
        numberOfDataValues, #2
        averageValue, #3
        standardDeviation, #4
        variance #5
    )
        
    return averageValue, \
           standardDeviation, \
           variance



def getMedianAndQuantilesPYtoCPP (
    dataValues, 
    lowerQuantile = 0.25, 
    upperQuantile = 0.75 ):
    '''
    
    dataValues: 
    
        converted to a double

    
    returns tuple:
    
        [0]  medianValue
        [1]  lowerQuantileValue
        [2]  upperQuantileValue
    
    '''
    
    global DataWranglingToolsCPPCoreObject

    
    # Make sure the dataValues list is a NumPy array.
    if type (dataValues) == list:
    
        dataValues = np.asarray (dataValues, dtype = np.double)

    else:
    
        dataValues = np.ascontiguousarray (dataValues, dtype = np.double)       


#     # Make sure the array is stored contiguously.
#     if not dataValues.flags ['C_CONTIGUOUS']:
    
#         dataValues = np.ascontiguousarray (dataValues)
    
    
    cdef Py_ssize_t numberOfDataValues = dataValues.shape [0]
    cdef double [::1] dataValues_view = dataValues
    
    cdef double medianValue = 0.
    cdef double lowerQuantileValue = 0.
    cdef double upperQuantileValue = 0.
    
        
    DataWranglingToolsCPPCoreObject.getMedianAndQuantiles (
        &dataValues_view [0], #1
        numberOfDataValues, #2
        medianValue, #3
        lowerQuantile, #4
        lowerQuantileValue, #5
        upperQuantile, #6
        upperQuantileValue #7
    )

        
    return medianValue, \
           lowerQuantileValue, \
           upperQuantileValue



def getNearestValuePYtoCPP (
    dataValues,
    valueToCompare,
    monotonicList = 1 ):
    '''

    dataValues: 
    
        converted to a double


    '''

    global DataWranglingToolsCPPCoreObject

    cdef int iSmallestDifference = 0
    cdef double smallestDifference = 0


    # Make sure the dataValues list is a NumPy array.
    if type (dataValues) == list:
    
        dataValues = np.asarray (dataValues, dtype = np.double)

    else:
    
        dataValues = np.ascontiguousarray (dataValues, dtype = np.double)       
    
    
    cdef Py_ssize_t numberOfValues = dataValues.shape [0]
    cdef double [::1] dataValues_view = dataValues
        
      
    DataWranglingToolsCPPCoreObject.getNearestValue (
        &dataValues_view [0], #1
        numberOfValues, #2
        valueToCompare, #3
        iSmallestDifference, #4
        smallestDifference, #5
        monotonicList #6
    )


    return iSmallestDifference, smallestDifference
