# DataTools: a Python pseudo-class
# Author: Maarten Roos-Serote
# ORCID author: 0000 0001 5001 1347

DataToolsVersion = '20240828'

# Standard imports.
import os
import sys
import shutil
separatorCharacter = '\\' if sys.platform == 'win32' else '/'


from pathlib import Path

import datetime
import time

import matplotlib.pyplot as plt
import numpy as np

from scipy import signal


# Custom imports of the Python to C++ libraries.
import DataWranglingToolsPYtoCPP
import FilterToolsPYtoCPP



class DataTools:
    """
    DataTools is a pseudo-class (no instantiation, no 'self'), bundling a couple of functions to work with all sorts of data.
    """


    # Used in the  getUncertaintyLevelInElectrode  method and by  AnnotationTool  in te NoiseViewer method.
    # Determine the list of amplitude segments for the electrogram.
    @staticmethod
    def getSegmentSpecsFromDataValues (dataValues, PYtoCPP = True):
        '''    
        :param dataValues: list (one dimension) of data values. The values in the ``dataValues`` list are converted to int16 type (for now).
        :type dataValues: list

        :param PYtoCPP: at the time of writing, the user can still chose to use Python to analyse the ``dataValues`` by setting ``PYtoCPP`` to ``False``. The result is less comprehensive and the runtime significantly longer.
        :type PYtoCPP: boolean; default = True

        :return: all the characteristics of the segments comprised by the list of ``dataValues`` (see **Description** below) when ``PYtoCPP = True``, or list of amplitudes and start indices when ``PYtoCPP = False``.
        :rtype: tuple when ``PYtoCPP = True`` or two lists, first list [same type as ``dataValues``] and second list [int]


        **Description:**
        With this function a list of (wiggling) data values is analysed to determine all the specifications in terms of its segments. A segment in a wiggling data values line is a section of the line from a local minimum to the next local maximum or a local maximum to the next local minimum. The specifications are returned in terms of a tuple of NumPy arrays and numbers:
    
            | [0]  numberOfSegments
            | [1]  segmentStartIndices - the start indices of each segment (the local minima and maxima).
            | [2]  segmentAmplitudes - the corresponding amplitudes between local extremes in units of ADU.
            | [3]  segmentSlopes - the corresponding slopes in units of ADU / time sample.
            | [4]  segmentDurations - the number of time samples between local extremes.
            | [5]  numberOfSegmentsNegative - subsection of the list above with only the segments from local maxima to the next local minima.
            | [6]  segmentStartIndicesNegative [0:numberOfSegmentsNegative]
            | [7]  iSteepestNegativeSlopeSegment
            | [8]  iSegmentStartIndicesSteepestNegativeSlope
            | [9]  numberOfSegmentsPositive - subsection of the list above with only the segments from local minima to the next local maxima.
            | [10] segmentStartIndicesPositive [0:numberOfSegmentsPositive]
            | [11] iSteepestPositiveSlopeSegment
            | [12] iSegmentStartIndicesSteepestPositiveSlope
 
        When calling this function with :code:`PYtoCPP = False`, only list of segment amplitudes and segment start indices is being returned.           
        '''

        # Run this function with the C++ core per default.
        if PYtoCPP:

            return DataWranglingToolsPYtoCPP.getSegmentSpecsFromDataValuesPYtoCPP (dataValues)


        # Run the Python version (which needs updating to match the C++ code!).
        else:
                
            np.seterr (all = 'ignore')

            segmentAmplitudes = []
            segmentAmplitudes.append (int (dataValues [1]) - int (dataValues [0]))

            segmentStartindices = []
            segmentStartindices.append (0)

            for iSample in range (1, len (dataValues) - 1):
            
                deltaValue = int (dataValues [iSample + 1]) - int (dataValues [iSample])

                if (segmentAmplitudes [-1] > 0 and deltaValue >= 0) or (segmentAmplitudes [-1] < 0 and deltaValue <= 0):

                    segmentAmplitudes [-1] += deltaValue

                else:

                    segmentAmplitudes.append (deltaValue)
                    segmentStartindices.append (iSample)


            segmentAmplitudes = np.asarray (segmentAmplitudes)        
            segmentStartindices = np.asarray (segmentStartindices)
                
            return segmentAmplitudes, segmentStartindices


    #
    @staticmethod
    def passAverageFilter (dataValues, windowWidth):
        '''
        :param dataValues: list (one dimension) of data values that represent the signal to be filtered.
        :type dataValues: list 

        :param windowWidth: width of the window: number of values in the averaging window including the central value. This is always an uneven number.
        :type windowWidth: int

        :return: signal ``dataValues`` filtered with a running average. 
        :rtype: list 


        **Description:**
        Use this function to perform a running average filtering of a list (one dimension) of data values. The total number of point in the averaging window is :code:`2 * windowWidth + 1`. At the beginning and the end of the list, filtering is done with the available data values. For example, the result for the first data value is the average of the first data value and the :code:`width` data values to the right. 
        
        The noise level of the filtered set can be easily calculated from the noise level of the original data values, by dividing by the square root of the total number of data values in the averaging window. 
        '''

        if windowWidth <= 0:

            print ()
            print ('---WARNING---')
            print (' Window width needs to be an uneven number larger than 0!')
        
            return dataValues
        
        else:
              
            if not windowWidth % 2:
            
                windowWidth += 1
                
                print ()
                print ('---WARNING---')
                print (' Window width needs to be uneven number: reset to {} samples.'.format (windowWidth) )
    
                
            return FilterToolsPYtoCPP.passAverageFilterPYtoCPP (dataValues, windowWidth // 2)
        


    # Pass a given input signal through a median filter.
    @staticmethod
    def passMedianFilter (dataValues, windowWidth = 3):
        '''
        :param dataValues: list (one dimension) of data values that represent the signal to be filtered.
        :type dataValues: list 

        :param windowWidth: width of the window: number of values in the averaging window including the central value. This is always an uneven number.
        :type windowWidth: int

        **Description:**
        Pass a given input signal through a median filter, using signal.medfilt method.
        '''

        if windowWidth <= 0:

            print ()
            print ('---WARNING---')
            print (' Window width needs to be an uneven number larger than 0!')
        
            return (dataValues)
        
        else:
               
            if not windowWidth % 2:
            
                windowWidth += 1
                
                print ()
                print ('---WARNING---')
                print (' Window width needs to be uneven number: reset to {} samples.'.format (windowWidth) )

    
            return signal.medfilt (dataValues, windowWidth)         

           

    # Pass a given input signal through a Butterworth notch filter.
    @staticmethod
    def passButterworthNotchFilter ( inputSignal = [], 
                                     bNotch = [],
                                     aNotch = [], 
                                     applyFilter = True,
                                     samplingFrequency = 1000, 
                                     notchFrequency = 50, 
                                     qualityFactor = 2, 
                                     getFilterSettings = True ):
        '''
        :param inputSignal: list (one dimension) of data values that represent the signal to be filtered.
        :type inputSignal: list 

        :param bNotch: filter parameters.
        :type bNotch: float

        :param aNotch: filter parameters.
        :type aNotch: float

        :param applyFilter: True if the filter needs to be applied to the signal.
        :type applyFilter: bool

        :param samplingFrequency: the sampling frequency of the data in Hz.
        :type samplingFrequency: float

        :param notchFrequency: the notch frequency in Hz, default is 50Hz.
        :type notchFrequency: float

        :param qualityFactor: a quality factor, default is 2.
        :type qualityFactor: float

        :param getFilterSettings: True (default) if the filter settings are to be calculated.
        :type getFilterSettings: bool

        :return: If getFilterSettings = True and applyFilter = True, then return outputSignal, bNotch, aNotch, filterFrequency, amplitudedB. If getFilterSettings = True and applyFilter = False, then return bNotch, aNotch, filterFrequency, amplitudedB. If getFilterSettings = False and applyFilter = True, then return outputSignal.
        :rtype: list, NumPy array, NumPy array, NumPy array, NumPy array
        
        
        **Description:**
        Pass a given input signal through a notch filter. 
        The `scipy.signal.iirnotch <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.iirnotch.html>`_ method 
        is used to calculate the filter parameters :code:`bNotch` and :code:`aNotch`,
        followed by the `signal.filtfilt <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.filtfilt.html>`_ method 
        to apply the filter to the data.
        
        To use this filter, two steps are involved.
        The first step is to calculate the filter parameters:
        
        .. code-block:: Python
        
            dataSampleFrequency = 200 #Hz
            notchFrequency = 50 #Hz
            filterParameters = DataTools.passButterworthBandPassOrStopFilter ( applyFilter = False,
                                                                               samplingFrequency = dataSampleFrequency,
                                                                               notchFrequency = notchFrequency,
                                                                               qualityFactor = 2,
                                                                               getFilterSettings = True )
        

        This only needs to be done once for given settings. After that, the filter can be applied to the data:
        
        .. code-block:: Python
        
            someData = [a list of data values]
            someDataFiltered = DataTools.passButterworthNotchFilter ( inputSignal = someData, 
                                                                      bNotch = filterParameters [0],
                                                                      aNotch = filterParameters [1],
                                                                      getFilterSettings = False )
        
            
        
        '''

        
        # Calculate the bNotch and aNotch parameters of the filter.
        if getFilterSettings:
             
            # Design a notch filter using the signal.iirnotch method (Infinite Impulse Response)
            bNotch, aNotch = signal.iirnotch (notchFrequency, qualityFactor, samplingFrequency)
     
            # Compute magnitude response of the designed filter
            filterFrequency, amplitudedB = signal.freqz (bNotch, aNotch, fs = samplingFrequency)
        

        # Apply the filter to the input signal.
        if applyFilter and len (bNotch) and len (aNotch):
        
            outputSignal = signal.filtfilt (bNotch, aNotch, inputSignal)


        # If no valid filter parameters were given, then issue a warning.
        elif applyFilter and ( not len (bNotch) or not len (aNotch) ):
        
            print ()
            print ('---WARNING---')
            print (' Filter settings bNotch and/or aNotch have not been given or calculated.')
            
            return []

        
        # Return the correct variables.
        if getFilterSettings and applyFilter:        

            return outputSignal, bNotch, aNotch, filterFrequency, amplitudedB
            
        elif getFilterSettings and not applyFilter:
        
            return bNotch, aNotch, filterFrequency, amplitudedB
            
        elif not getFilterSettings and applyFilter:
        
            return outputSignal



    # Pass a given input signal through a Butterworth Band Pass or Band Stop filter.
    @staticmethod
    def passButterworthBandPassOrStopFilter ( inputSignal = [],
                                              secondfilterOrderSections = [],
                                              applyFilter = True,
                                              samplingFrequency = 1000, 
                                              filterType = 'lowpass', 
                                              filterOrder = 10,
                                              cutoffFrequency = 10,
                                              getFilterSettings = True ):
       
        '''
        :param inputSignal: list (one dimension) of data values that represent the signal to be filtered.
        :type inputSignal: list 
        
        :param secondfilterOrderSections: SOS or Second-Order Sections.
        :type secondfilterOrderSections: 

        :param applyFilter: True if the filter needs to be applied to the signal.
        :type applyFilter: bool
        
        :param samplingFrequency: the sampling frequency of the data in Hz.
        :type samplingFrequency: float

        :param filterType: 'lowpass', 'highpass' or 'bandstop', default is 'lowpass'
        :type filterType: str

        :param filterOrder: quality factor, default is 10.
        :type filterOrder: float

        :param cutoffFrequency: filter cutoff frequency, one number for low and high pass filters, a list of two numbers for band stop filter.
        :type cutoffFrequency: float or list [float, float]

        :return: If getFilterSettings = True and applyFilter = True, then return outputSignal, secondfilterOrderSections. If getFilterSettings = True and applyFilter = False, then return secondfilterOrderSections. If getFilterSettings = False and applyFilter = True, then return outputSignal.
        :rtype: list, NumPy array, NumPy array
        
        
        **Description:**
        Pass a given input signal through a **Butterworth band pass** (low pass or high pass) or a **Butterworth band stop** filter, 
        using the `signal.butter <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html>`_ and 
        `signal.sosfilt <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfilt.html>`_ methods. 
        It is recommended to use *SOS* (= *Second-Order Sections*).
        
        To use this filter, two steps are involved.
        The first step is to calculate the filter parameters.
        For a bandpass filter this could look like:
        
        .. code-block:: Python
        
            dataSampleFrequency = 200 #Hz
            cutoffFrequency = 100 #Hz
            filterParameters = DataTools.passButterworthBandPassOrStopFilter ( applyFilter = False,
                                                                               samplingFrequency = dataSampleFrequency,
                                                                               filterType = 'lowpass',
                                                                               filterOrder = 10,
                                                                               cutoffFrequency = cutoffFrequency,
                                                                               getFilterSettings = True )

        For a bandstop filter this could look like:
        
        .. code-block:: Python
        
            dataSampleFrequency = 200 #Hz
            cutoffFrequency = [40, 60] #Hz
            filterParameters = DataTools.passButterworthBandPassOrStopFilter ( applyFilter = False,
                                                                               samplingFrequency = dataSampleFrequency,
                                                                               filterType = 'lowpass',
                                                                               filterOrder = 10,
                                                                               cutoffFrequency = cutoffFrequency,
                                                                               getFilterSettings = True )
        


        The first step needs to be done once for given settings. After that, the filter can be applied to the data:
        
        .. code-block:: Python
        
            someData = [a list of data values]
            someDataFiltered = DataTools.passButterworthNotchFilter ( inputSignal = someData, 
                                                                      secondfilterOrderSections = filterParameters,
                                                                      getFilterSettings = False )

        '''
         
        # Calculate the filter parameters.
        if getFilterSettings:

            # For Band Stop filtering, the  cutoffFrequency  has to be a list of two numbers, the low and the high end of the band stop.
            # For Band Pass filtering, the  cutoffFrequency  has to be a number, not a list.
            if (filterType == 'bandstop' and type (cutoffFrequency) == list) or (filterType != 'bandstop' and type (cutoffFrequency) != list):
             
                # Design the filter using the signal.butter method (Second Order Sequence).
                secondfilterOrderSections = signal.butter (filterOrder, cutoffFrequency, btype = filterType, fs = samplingFrequency, output = 'sos')

     
        
        # Apply the filter to the input signal.
        if applyFilter and len (secondfilterOrderSections):
        
            outputSignal = signal.sosfiltfilt (secondfilterOrderSections, inputSignal)


        # If no valid filter parameters were given, then issue a warning.
        elif applyFilter and ( not len (secondfilterOrderSections) ):
        
            print ()
            print ('---WARNING---')
            print (' Filter settings secondfilterOrderSections have not been given or calculated.')
            
            return []

        
        # Return the correct variables.
        if getFilterSettings and applyFilter:        

            return outputSignal, secondfilterOrderSections
            
        elif getFilterSettings and not applyFilter:
        
            return secondfilterOrderSections
            
        elif not getFilterSettings and applyFilter:
        
            return outputSignal

    

    # Determine the values of the variables a and b for the linear least square solution y  =  a * x  +  b.
    @staticmethod
    def linearLeastSquare ( xInput, yInput, weights = [], fractionBeyondXRange = 0.1 ):
        '''
        :param xInput: the x-values of the data to fit.
        :type xInput: list [float]

        :param yInput: the y-values of the data to fit.
        :type yInput: list [float]

        :param weights: the weights of the data to fit.
        :type weights: list [float]
        
        :param fractionBeyondXRange: the fraction of the xInput range beyond which to calculate the fitting line (default = 0.1).
        :type fractionBeyondXRange: float
        
        

        :return: a, b, uncertaintyA, uncertaintyB, rSquared, xValuesFitLine, yValuesFitLine
        :rtype: float, float, float, float, float, NumPy array (2), NumPy array (2)
        
        
        **Description:**
        Determine the values of the variables a and b for the linear least square solution y (x) =  ax + b, along with their uncertainties, for a set of data points described by the x- and y-values. An indication of the quality of the fit is given by the so-called `coefficient of determination <https://en.wikipedia.org/wiki/Coefficient_of_determination>`_ (r-squared), a value between 0 and 1, and is evaluated here. The closer r-square to 1, the better the fit.
        '''
    
        
        xInput = np.asarray (xInput)
        yInput = np.asarray (yInput)

        if not len (weights):

            weights = np.ones ( len (xInput) )


        
        # do not take into account any NaN values in yInput
        iValid = np.where ( np.isfinite (yInput) )
        
        x = xInput [iValid]
        y = yInput [iValid]

        numberOfValues = len (x)
        
        sumX = np.sum (x)
        sumX2 = np.sum (x * x)
        
        sumY = np.sum (y)
        sumXY = np.sum (x * y)
        
        determinant = numberOfValues * sumX2 - sumX * sumX
        
        a = ( numberOfValues * sumXY - sumX * sumY ) / determinant
        b = ( sumX2 * sumY - sumX * sumXY ) / determinant

        
        residu = y - ( a * x + b )
        sumResidu2 = np.sum (residu * residu)
        
        averageErrorY = sumResidu2 / (numberOfValues - 2)
        averageErrorA = averageErrorY * numberOfValues / determinant
        averageErrorB = averageErrorY * sumX2 / determinant
        
        uncertaintyA = np.sqrt (averageErrorA)
        uncertaintyB = np.sqrt (averageErrorB)
        
        
        # Calculate the r-squared value, an indication for the goodness of the fit. The closer to 1, the better the fit.
        squaredSumResiduals = np.sum ( (y - (a * x + b)) ** 2 )        
        dataAverage = np.sum (y) / numberOfValues
        squaredSumTotal = np.sum ( (y - dataAverage) ** 2 ) 
        rSquared = 1 - squaredSumResiduals / squaredSumTotal
       
       
        # Calculate and return the fitted line with two points slightly outside the range of the xInput values.       
        xRange =  max (xInput) - min (xInput)
        xValuesFitLine = np.asarray ( [ min (xInput) - fractionBeyondXRange * xRange, max (xInput)  + fractionBeyondXRange * xRange ] )
        yValuesFitLine = a * xValuesFitLine + b        
              
        
        return a, b, uncertaintyA, uncertaintyB, rSquared, xValuesFitLine, yValuesFitLine



    # Calculate and plot the QQ-plot (or Quantile-Quantile plot) and the histogram of a given list of input values.
    @staticmethod
    def QQPlot (xInput, xlabelToPrint = 'input values', ylabelToPrint = 'z (sigma)',
                QQTitleToPrint = 'DataTools version ' + DataToolsVersion + ': QQ-plot of input data',
                HistTitleToPrint = 'DataTools version ' + DataToolsVersion + ': Histogram of input data', 
                plotTextAverageMedian = True,
                savePlots = False,
                plotBaseFileName = 'QQPlot.png'):
        '''
        :param xInput: the list of data points.
        :type xInput: list [float]

        :param xlabelToPrint: the x-label to print on the QQ-plot.
        :type xlabelToPrint: str

        :param ylabelToPrint: the x-label to print on the QQ-plot.
        :type ylabelToPrint: str

        :param QQTitleToPrint: the title to print on the QQ-plot.
        :type QQTitleToPrint: str

        :param HistTitleToPrint: the title to print on the histogram.
        :type HistTitleToPrint: str

        :param plotTextAverageMedian: if True then plot the values of the average, median and standar deviation in the plot.
        :type plotTextAverageMedian: bool

        :param savePlots: if True then the plots will be saved to files, the default is .png format.
        :type savePlots: bool

        :param plotBaseFileName: file name of the plots. It can be given with or without file  type extension (.png, .jpg, .jpeg or .gif). Spaces in the file name are replaced with :file:`_`.  
        :type plotBaseFileName: str

                
        **Description:**
        Calculate and plot the QQ-plot (or Quantile-Quantile plot), as well as the histogram, of a given list of data values.
        If the user has opted to save the plots, then the plotBaseFileName is used to determine the file names of the plots.
        The strings :file:`_QQPlot` and :file:`_Histogram` are automatically added at the end of the file name.
        The default plot image file type is .png, if the user does not indicate any (.jpg, .jpeg or .gif).
        '''


        # Make sure the plotBaseFileName has no space in the name and determine the extension.
        if savePlots:

            plotBaseFileName = plotBaseFileName.replace (' ', '_')
       
            extension = ' '
            if '.png' in plotBaseFileName:
            
                extension = '.png'
            
            if '.jpg' in plotBaseFileName:

                extension = '.jpg'
                
            if '.jpeg' in plotBaseFileName:
            
                extension = '.jpeg'

            if '.gif' in plotBaseFileName:
            
                extention = '.gif'
                
            plotFileNameQQ = plotBaseFileName.split (extension)[0] + '_QQPlot'
            plotFileNameQQ += '.png'  if extension == ' ' else  extension

            plotFileNameHistogram = plotBaseFileName.split (extension)[0] + '_Histogram'
            plotFileNameHistogram += '.png'  if extension == ' ' else  extension
            


        xInput = np.array (xInput)
        xInputMean = np.mean (xInput)
        xInputMedian = np.median (xInput)
        xInputStd = np.std (xInput)

        x, cumulativeNormalDistribution = DataTools.getCumulativeNormalDistribution (xInputMean, xInputStd)

        xInputfilterOrdered = xInput.copy ()
        xInputfilterOrdered.sort ()

        xInputCumulativeNormalDistribution = [ (i-1) / len (xInputfilterOrdered) for i in range (1,len (xInputfilterOrdered)+1) ]

        xValues = []

        # Search for the indices in the true normally distributed cumulativeNormalDistribution between which
        #  the estimated cumulative distrbution value of the input (xInputCumulativeNormalDistribution) values lie
        #  and calculate the true normally distributed cumulative value that would correspond to the this iDataPoint
        #  by interpolation.
        for i, xInputCumulativeNormalDistributionValue in enumerate (xInputCumulativeNormalDistribution):

            cumulativeNormalDistributionAdded = cumulativeNormalDistribution.copy ()
            cumulativeNormalDistributionAdded.append (xInputCumulativeNormalDistributionValue)
            cumulativeNormalDistributionAdded.sort ()
            valueIndex = np.where ( np.array (cumulativeNormalDistributionAdded) == xInputCumulativeNormalDistributionValue )[0][-1]

            if valueIndex == 0:

                xValue = x [0]

            if valueIndex == len (x):

                xValue = x [-1]

            else:

                xValue = x [valueIndex-1] + (xInputCumulativeNormalDistributionValue - cumulativeNormalDistribution [valueIndex-1]) * \
                         (x [valueIndex] - x [valueIndex-1]) / \
                         (cumulativeNormalDistribution [valueIndex] - cumulativeNormalDistribution [valueIndex-1])



            xValues.append (xValue)


        zValues = (np.array (xValues) - xInputMean) / xInputStd
        phiValues = np.array (zValues) * xInputStd + xInputMean
        phiValuesStandard = (phiValues - xInputMean) / xInputStd

        zValuesxInputfilterOrdered = (np.array (xInputfilterOrdered) - xInputMean) / xInputStd

        # Plot the QQ-plot in figure 1 and the histogram in figure 2
        plt.figure (1)
        plt.clf ()

        labelMeanToPrint = 'mean, median = {:g}, {:g}'.format (xInputMean, xInputMedian)
        labelSTDToPrint = 'sd = {:g}'.format (xInputStd)

        plt.scatter (zValuesxInputfilterOrdered, zValues, s=1, color = 'green')
        plt.xlim (-3,3)
        # Plot the vertical 1-sigma reference lines
        plt.plot ([-1,-1], [-3,3], color = 'green', linewidth = 0.5)
        plt.plot ([1,1], [-3,3], color = 'green', linewidth = 0.5)

        plt.plot (phiValuesStandard, zValues, color = 'orange')
        plt.ylim (-3,3)
        # Plot the horizontal 1-sigma reference lines
        plt.plot ([-3,3], [-1,-1], color = 'orange', linewidth = 0.5)
        plt.plot ([-3,3], [1,1], color = 'orange', linewidth = 0.5)

        plt.xlabel (xlabelToPrint + ' - normalised to N(mu,sigma)', fontsize = 12)
        plt.ylabel (ylabelToPrint, fontsize = 12)
        plt.title (QQTitleToPrint)

        if plotTextAverageMedian:

            plt.text (-2.8,2.6, labelMeanToPrint, color = 'green')
            plt.text (-2.8,2.3, labelSTDToPrint, color = 'green')


        # Save the QQPlot if the user has selected this option.
        if savePlots:
        
            plt.savefig (plotFileNameQQ)
            plt.close ()

        
        
        plt.figure (2)
        plt.clf ()

        xInputMin = np.min (xInput)
        xInputMax = np.max (xInput)
        xInputRange = xInputMax - xInputMin
        xInputBinSize = xInputRange / 100

        bins = [ (xInputMin + i * xInputBinSize)  for i in range (-1, 102) ]
        xInputHistogram = np.histogram (xInput, bins = bins)
        xInputHistogramMax = np.max (xInputHistogram [0])

        plt.hist (xInput, bins = bins, color = 'green')
        plt.xlim (xInputMin - 10 * xInputBinSize, xInputMax + 10 * xInputBinSize)
        plt.ylim (0, xInputHistogramMax * 1.17)
        plt.xlabel (xlabelToPrint, fontsize = 12)
        plt.ylabel ('frequency', fontsize = 12)

        plt.title (HistTitleToPrint)

        if plotTextAverageMedian:
        
            plt.text (xInputMin - 5 * xInputBinSize, 1.10 * xInputHistogramMax , labelMeanToPrint, color = 'green')
            plt.text (xInputMin - 5 * xInputBinSize, 1.04 * xInputHistogramMax, labelSTDToPrint, color = 'green')

        
        # Save the histogram plot if the user has selected this option.
        if savePlots:
        
            plt.savefig (plotFileNameHistogram)
            plt.close ()

        else:            
        
            plt.show ()



    # Calculate the gaussian normal cumulative distribution curve N(mu,sigma) between -5*sigma and +5*sigma at stepsize 0.05*sigma.
    @staticmethod
    def getCumulativeNormalDistribution (mu,sigma):
        '''
        :param mu: the average values of the data values.
        :type mu: list [float]

        :param sigma: the standard deviation of the data values.
        :type sigma: float.
        
        :return: x and 
        :rtype: list [float], list [float]
        
        
        **Description:**
        Calculate the gaussian normal cumulative distribution curve N(mu,sigma) between -5 x sigma and +5 x sigma at stepsize 0.05 x sigma.
        The results of the :py:meth:`~.getNormalDistribution` function call is used. 
        This function is called from the :py:meth:`~.QQPlot` function.
        '''

        x, normalDistribution = DataTools.getNormalDistribution (mu, sigma)

        cumulativeNormalDistribution = []

        cumulativeNormalDistribution.append ( normalDistribution [0] )

        for i in range ( 1, len (x) - 1 ):

            cumulativeNormalDistribution.append ( cumulativeNormalDistribution [-1] + 
                                                  ( x [i]- x [i-1] ) * ( normalDistribution [i] + normalDistribution [i-1] ) / 2 )

        cumulativeNormalDistribution.append ( cumulativeNormalDistribution [-1] )

        return x, cumulativeNormalDistribution



    # Calculate the gaussian normal distribution curve N(mu,sigma) between -5*sigma and +5*sigma at stepsize 0.05*sigma.
    @staticmethod
    def getNormalDistribution (mu,sigma):
        '''
        :param mu: the average values of the data values.
        :type mu: float

        :param sigma: the standard deviation of the data values.
        :type sigma: float
 
        :return: the equally separated x values along the gaussian distribution and the corresponding values of a pure normal distribution.
        :rtype: list [float], list [float]
               
        **Description:**
        Calculate the gaussian normal distribution curve N (mu,sigma) between -5 x sigma and +5 x sigma at stepsize 0.05 x sigma.
        This function calls the :py:meth:`~.getNormalDistributionValue` function and it is called by the :py:meth:`~.getCumulativeNormalDistribution` function.
        '''

        constant = 1 / (sigma * np.sqrt (2 * np.pi))

        x = [ (mu + i*sigma / 20) for i in range (-100, 101) ]

        normalDistribution = [ constant * DataTools.getNormalDistributionValue (x [i], mu, sigma)  for i in range ( len (x) ) ]

        return x, normalDistribution



    # The value of the gaussian normal distribution defined by N(mu, sigma) at xi.
    @staticmethod
    def getNormalDistributionValue (xi,mu,sigma):
        '''
        :param xi: the x-value to calculate the normal distribution value for.
        :type xi: float

        :param mu: the average values of the data values.
        :type mu: float

        :param sigma: the standard deviation of the data values.
        :type sigma: float
 
        :return: the normal distribution value for the point x-i in the normal distribution with average mu and standard deviation sigma.
        :rtype: float
        
        
        **Description:**
        The value of the gaussian normal distribution defined by N (mu, sigma) at xi.
        This function is called by the :py:meth:`~.getNormalDistribution` function.
        '''

        normalValue = np.exp ( -0.5 * (xi - mu) * (xi - mu) / sigma / sigma )

        return normalValue



    #
    @staticmethod
    def getAverageVarAndSDPYtoCPP (dataValues = [], removeNaN = False):
        '''
        :param dataValues: list of data values.
        :type dataValues: list [float] or NumPy array (one dimension)

        :param removeNaN: if True then remove any NaN values from the list of data values.
        :type removeNaN: bool
        
        :return: average, standard deviation and variance of the list of data values.
        :rtype: float, float, float.
        
        **Description:**
        Calculate the average, standard deviation and variance of the list of data values using C++ code.   
        If :code:`removeNaN = True`, then call the :py:meth:`~.getNanFreeNumpyArray` function to remove any NaN values from the data list.     
        '''

        if removeNaN:
              
            dataValues = DataTools.getNanFreeNumpyArray (dataValues)

    
        if len (dataValues):
                    
            averagevalues, standardDeviation, variance = DataWranglingToolsPYtoCPP.getAverageVarAndSDPYtoCPP (dataValues)
            return averagevalues, standardDeviation, variance

        else:
        
            return None, None, None


    #
    @staticmethod
    def getMedianAndQuantilesPYtoCPP ( dataValues = [], 
                                       lowerQuantilePercentage = 25, 
                                       upperQuantilePercentage = 75, 
                                       removeNaN = False,
                                       uncertainties = [],
                                       numberOfUncertaintyExperiments = 1000 ):
        '''
        :param dataValues: list of data values.
        :type dataValues: list [float] or NumPy array (one dimension)

        :param lowerQuantilePercentage: the lower quantile.
        :type lowerQuantilePercentage: float

        :param upperQuantilePercentage: the upper quantile.
        :type upperQuantilePercentage: float

        :param removeNaN: if True then remove any NaN values from the list of data values.
        :type removeNaN: bool

        :param uncertainties: list of uncertainties for each data point.
        :type uncertainties: list [float] or NumPy array (one dimension)

        :param numberOfUncertaintyExperiments: number of experiments to perform to create gaussian-randomised dataValues for the determination of the uncertainty in the median.
        :type numberOfUncertaintyExperiments: int

        
        :return: median, lower and upper quantile as defined by lowerQuantilePercentage and upperQuantilePercentage, uncertainty in the median.
        :rtype: float, float, float, float
        
        **Description:**
        Calculate the median, lower and upper quantiles of the list of data values using C++ code.   
        If :code:`removeNaN = True`, then call the :py:meth:`~.getNanFreeNumpyArray` function to remove any NaN values from the data list.
        
        If there are uncertainties associated with the data values, then the uncertainty in the median can be estimated from running a number of experiments. In each experiment, a new set of data values is created from the original set by adding random gaussian noise (using the NumPy random.normal method) with a standard deviation equal to the uncertainty in each data value. The medians of these experiments are collected and at the end, the standard deviation of these medians is returned. This value can be considered a good approximation of the uncertainty in the median of the original set due to the uncertainties in the data values. The default number of experiments is 1000, and this is only done if the uncertainties in the data values are passed as a list to the :code:`uncertainties` variable.
        '''

        if removeNaN:
              
            dataValues = DataTools.getNanFreeNumpyArray (dataValues)
            uncertainties = DataTools.getNanFreeNumpyArray (uncertainties)
            
 
    
        numberOfDataValues = len (dataValues)
        numberOfUncertainties = len (uncertainties)
        if numberOfDataValues:
    
            medianValue, lowerQuantileValue, upperQuantileValue = \
             DataWranglingToolsPYtoCPP.getMedianAndQuantilesPYtoCPP (dataValues, lowerQuantilePercentage / 100, upperQuantilePercentage / 100)   

            medianValueUncertainty = 0
            # If there are uncertainties associated with every data values, then use these to run experiments to determine the uncertainty in the median value.
            if numberOfUncertainties and numberOfUncertainties == numberOfDataValues:
            
                if numberOfUncertainties == 1: 
                
                    medianValueUncertainty = uncertainties [0]

                else:
                
            
                    medianValuesExperiments = []
                    for iExperiment in range (numberOfUncertaintyExperiments):
    
                        # Assume that the uncertainty in each data value represents the standard deviation of a normal distribution around this data value.                 
                        dataValuesRandomised = DataTools.getDataValuesWithGaussianNoise (dataValues, uncertainties)
                       
                        medianValuesExperiments.append ( DataWranglingToolsPYtoCPP.getMedianAndQuantilesPYtoCPP (dataValuesRandomised, 0, 1)[0] )
                
                    medianValueUncertainty = DataTools.getAverageVarAndSDPYtoCPP (medianValuesExperiments) [1]
                

            return medianValue, lowerQuantileValue, upperQuantileValue, medianValueUncertainty

        else:
        
            return None, None, None, None



    #
    @staticmethod
    def getNanFreeNumpyArray (dataValues, replaceWithValue = False, valueToReplace = 0.):
        '''
        :param dataValues: complete list of data values.
        :type dataValues: list [float] or NumPy array (one dimension)
        
        :param replaceWithValue: replace NaN element with zero value if :code:`True`, default :code:`False`.
        :type replaceWithValue: bool
        
        :param valueToReplace: value to replace NaN elements if :code:`replaceWithZero == True`, default = 0.
        :type valueToReplace: float
        
        :return: list of data values with any NaN values removed or replaced with :code:`valueToReplace`. value.
        :rtype: NumPy array 
        
        **Description:**
        Remove or replace with zero values all the NaN values from a list of data values and return the cleansed list as a NumPy array (one dimension).
        '''
        
        if type (dataValues) == list:
                
            iNaNValues = np.isnan ( np.asarray (dataValues) )  
            
            if replaceWithValue:
            
                dataValues = np.asarray (dataValues)
                dataValues [iNaNValues] = valueToReplace
                return dataValues
               
            else:
              
                return np.asarray (dataValues) [~iNaNValues]
        
        else:
        
            iNaNValues = np.isnan (dataValues)  

            if replaceWithValue:

                dataValues [iNaNValues] = valueToReplace
                return dataValues

            else:
                                  
                return dataValues [~iNaNValues]
            


    #
    @staticmethod
    def getDataValuesWithGaussianNoise (dataValues, uncertainties):
        '''
        :param dataValues: complete list of data values.
        :type dataValues: list [float] or NumPy array (one dimension)

        :param uncertainties: list of uncertainties for each data point.
        :type uncertainties: list [float] or NumPy array (one dimension)
        
        :return: list of data values with random Gaussian noise added.
        :rtype: NumPy array 
        
        **Description:**
        Add Gaussian noise to a list of data values using the NumPy random.normal method. The user-provided uncertainty values for each data value are fed
        into the np.random.normal method as the standard deviation of the normal distribution with mean value the data value.
        '''

        # Only do the noise adding if all the data values have associated uncertainties.
        if len (dataValues) == len (uncertainties):
        
            # Assume that the uncertainty in each data value represents the standard deviation of a normal distribution around this data value.                 
            dataValuesWithGaussianNoise = [ np.random.normal (dataValues [iDataValue], uncertainties [iDataValue], 1)[0]  
                                            for iDataValue in range ( len (uncertainties) ) ]            
            
            
        # If the number of data values does not match the number of uncertainty values, then issue a warning and return the data values.
        else:

            print ()
            print ('---WARNING---')
            print (' Number of data values does not correspond to the number of uncertainty values.')

        
            dataValuesWithGaussianNoise = dataValues

            
        return  np.asarray (dataValuesWithGaussianNoise)

