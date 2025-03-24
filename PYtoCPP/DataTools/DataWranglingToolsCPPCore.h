#ifndef DATAWRANGLINGTOOLSCPPCORE_H
#define DATAWRANGLINGTOOLSCPPCORE_H


class DataWranglingToolsCPPCore {

    public:
    
        DataWranglingToolsCPPCore ();
        ~DataWranglingToolsCPPCore ();
        
        void getSegmentSpecsFromDataValues ( 
            float dataValues [1], //1
            unsigned int numberOfDataValues, //2                          
            unsigned int segmentStartIndices [1], //3
            unsigned int& numberOfSegments, //4
            float segmentAmplitudes [1], //5
            float segmentSlopes [1], //6
            unsigned int segmentDurations [1], //7
            unsigned int segmentStartIndicesNegative [1], //8
            unsigned int& numberOfSegmentsNegative, //9
            unsigned int& iSteepestNegativeSlopeSegment, //10
            unsigned int& iSegmentStartIndicesSteepestNegativeSlope, //11
            unsigned int segmentStartIndicesPositive [1], //12
            unsigned int& numberOfSegmentsPositive, //13
            unsigned int& iSteepestPositiveSlopeSegment, //14
            unsigned int& iSegmentStartIndicesSteepestPositiveSlope //15
        );


        void getAverageVarAndSD (
            double dataValues [1], //1
            int numberOfValues, //2
            double& averageValue, //3
            double& standardDeviation, //4
            double& variance //5
        );


        void getMedianAndQuantiles (
            double dataValues [1], //1
            int numberOfValues, //2
            double& medianValue, //3
            float lowerQuantile, //4
            double& lowerQuantileValue, //5
            float upperQuantile, //6
            double& upperQuantileValue //7
        );


        void getNearestValue (
            double dataValues [1], //1
            unsigned int numberOfValues, //2
            double valueToCompare, //3
            int& iSmallestDifference, //4
            double& smallestDifference, //5   
            int monotonicList //6      
        );


        
    private:

        double getQuantileValue (
            std::vector <double> dataValuesSorted,
            int numberOfValues,
            float quantile
        );
    
    

};


#endif

