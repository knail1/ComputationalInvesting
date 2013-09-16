'''
This source code is released under the New BSD license.


Created on September, 15 2013

@author: Omer Ansari
@contact: knail1@live.com
@summary: HW for Computational Investing 1, Coursera.

The purpose of this assignment is to
Introduce you to historical equity data
Introduce you to Python & Numpy, and
Give you a first look at portfolio optimization
'''

# QSTK Imports
import QSTK.qstkutil.qsdateutil as DateUtility
import QSTK.qstkutil.tsutil as TSUtility
import QSTK.qstkutil.DataAccess as DataAccess

# Third Party Imports
import datetime as Datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as Numpy
import itertools as Itertools
import os.path
import operator

def permutationsAlgorithm():
    completeSimulationDataDictionaryNoValues = {}
    allPossibleCombinations = Itertools.permutations([0.0,0.0,0.0,0.1,0.1,0.1,0.2,0.2,0.2,0.3,0.3,0.3,0.4,0.4,0.4,0.5,0.5,0.6,0.7,0.8,0.9,1.0],4)
    for line in allPossibleCombinations:
        if Numpy.sum(line) == 1.0:
            #print line
            if (completeSimulationDataDictionaryNoValues.has_key(line) == False):
                completeSimulationDataDictionaryNoValues[line] = None

    #print "completeSimulationDataDictionary"
    return completeSimulationDataDictionaryNoValues


def portfolioIterator(logFileName,startDate,endDate,symbolArray):
    #if (os.path.isfile(logFileName)) == False:
    #    headerLine = "portfolio,allocation,sharpe\n"
    #    fout.write(headerLine)

    #fout = open(logFileName,'w')
    allPossibleCombinations = Itertools.permutations([0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0],4)

    completeSimulationDataDictionary = permutationsAlgorithm() # key : portfolio, value: sharpe

    # now to create the legal combinations:
    for line in completeSimulationDataDictionary:
            result = simulate(startDate,endDate,symbolArray,list(line))
            outputPrinter(startDate,endDate,symbolArray,list(line),result)
            completeSimulationDataDictionary[line] = result['sharpe']
            #fout.write(completeSimulationDataDictionary.__str__())

    #bestAllocation = []
    bestAllocation = max(completeSimulationDataDictionary.iterkeys(), key=lambda k: completeSimulationDataDictionary[k])

    #print "completeSimulationDataDictionary[bestAllocation]"
    #print completeSimulationDataDictionary[bestAllocation]

    return (completeSimulationDataDictionary[bestAllocation],list(bestAllocation))




    #print "allLegalCombinations"
    #print allLegalCombinations

    #fout.write("\n")
    #fout.close()

def simulate(startDate, endDate, symbolArray, allocationsArray):
    '''
    - Some assumptions:
    - Allocate some amount of value to each equity on the first day. You then "hold" those investments for the entire year.
    - Use adjusted close data. In QSTK, this is 'close'
    - Report statistics for the entire portfolio
    '''

    timeOfDayToCalculateAt = Datetime.timedelta(hours=16) # 16 = 1600 from epoch so 4pm

    # Get a list of trading days between the start and the end.
    listOfTradingDays = DateUtility.getNYSEdays(startDate, endDate, timeOfDayToCalculateAt)

    # Creating an object of the dataaccess class with Yahoo as the source.
    # cleaning the cache at insantiation as well, per http://wiki.quantsoftware.org/index.php?title=CompInvestI_Homework_1
    equityDataObject = DataAccess.DataAccess('Yahoo', cachestalltime=0)

    # Key to be read from the data:
    #ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    attributeOfEquityToExtract = ['close']

    # Reading the data, now AttributeDataDictionary is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    rawEquityData = equityDataObject.get_data(listOfTradingDays, symbolArray, attributeOfEquityToExtract)
    AttributeDataDictionary = dict(zip(attributeOfEquityToExtract, rawEquityData))

    #print "AttributeDataDictionary"
    #print AttributeDataDictionary

    closingPrices=AttributeDataDictionary["close"].values

    #print "ClosingPrices:"
    #print closingPrices

    normalizedClosingPrices= closingPrices / closingPrices[0, :] # divide all rows by the first row, inclusive
    #print "normalizedClosingPrices:"
    #print normalizedClosingPrices

    allocatedClosingPrices = normalizedClosingPrices*allocationsArray

    averageDailyReturnsArray = Numpy.array(closingPrices.copy(), dtype=float)

    #print "allocatedClosingPrices"
    #print allocatedClosingPrices

    dailyValueOfPortfolio = Numpy.zeros((len(allocatedClosingPrices),1))
    for row in xrange(len(allocatedClosingPrices)):
        dailyValueOfPortfolio[row-1] = Numpy.sum(allocatedClosingPrices[row-1,:])

    #print "dailyValueOfPortfolio"
    #print dailyValueOfPortfolio


    backupOfDailyValueOfPortfolio = Numpy.array(dailyValueOfPortfolio.copy(), dtype=float)


    averageDailyReturnsArrayFromQSTK = TSUtility.returnize0(dailyValueOfPortfolio)

    #print "avg daily return of portfolio via TSUtility.returnize0"
    #print averageDailyReturnsArrayFromQSTK

     #daily_cum_ret(t) = daily_cum_ret(t-1) * (1 + daily_ret(t))
    dailyCumReturnsOfPortfolio = Numpy.zeros((len(allocatedClosingPrices),1))
    dailyCumReturnsOfPortfolio[0,0] = backupOfDailyValueOfPortfolio[0,0]


    #print "    dailyCumReturnsOfPortfolio[0,0]"
    #print dailyCumReturnsOfPortfolio[0,0]


    for row in xrange(len(allocatedClosingPrices)):
            if (row != (len(allocatedClosingPrices) -1)):
                dailyCumReturnsOfPortfolio[row+1,0] = dailyCumReturnsOfPortfolio[row,0] * (1 + averageDailyReturnsArrayFromQSTK[row,0])




    #print "dailyCumReturnsOfPortfolio"
    #print dailyCumReturnsOfPortfolio

    """for column in xrange(len(symbolArray)):
        for row in xrange(len(allocatedClosingPrices)): # this measure the length of the row
            if row == 1:
                averageDailyReturnsArray[0,:] = [0.0,0.0,0.0,0.0]
            if allocatedClosingPrices[row-1, column-1] != 0:
               averageDailyReturnsArray[row,column-1] = (allocatedClosingPrices[row,column-1]/allocatedClosingPrices[row-1, column-1]) - 1
            else:
                averageDailyReturnsArray[row,column-1] = 0

    averageDailyReturnsArrayFromQSTK = TSUtility.returnize0(allocatedClosingPrices)
    print "TSUtility.returnize0"
    print averageDailyReturnsArrayFromQSTK


    print "averageDailyReturnsArray:"
    print averageDailyReturnsArray

    averageDailyReturnOfEachSymbol = [0] * len(symbolArray)

    # now we'll take an average for each symbol
    for column in xrange(len(symbolArray)):
        averageDailyReturnOfEachSymbol[column-1] = Numpy.average(averageDailyReturnsArray[1:,column-1])

    print "averageDailyReturnOfEachSymbol:"
    print averageDailyReturnOfEachSymbol

    #[a*b for a,b in zip(lista,listb)]

    #avgDailyReturn = Numpy.dot(averageDailyReturnOfEachSymbol * allocationsArray)
    #avgDailyReturn = [a*b for a,b in zip(averageDailyReturnOfEachSymbol, allocationsArray)]
    #avgDailyReturn=0.0
    #for a,b in zip(averageDailyReturnOfEachSymbol, allocationsArray):
    #    avgDailyReturn = avgDailyReturn + a*b

    #avgDailyReturn = Numpy.average(averageDailyReturnOfEachSymbol,weights=allocationsArray)
    avgDailyReturn = Numpy.sum(averageDailyReturnOfEachSymbol)
    avgDailyReturn = Numpy.average(averageDailyReturnOfEachSymbol)
    """




    stdDevOfDailyReturns=Numpy.std(averageDailyReturnsArrayFromQSTK)
    avgDailyReturn=Numpy.average(averageDailyReturnsArrayFromQSTK)
    sharpeRatio= 252**0.5 * avgDailyReturn/stdDevOfDailyReturns
    cumulativeReturn=dailyCumReturnsOfPortfolio[-1]

    return {'vol':stdDevOfDailyReturns, 'daily_ret':avgDailyReturn ,'sharpe':sharpeRatio, 'cum_ret':cumulativeReturn }

def outputPrinter(startDate,endDate,listOfSymbols, allocation, result):
    print "Start Date: ",
    print startDate
    print "End Date: ",
    print endDate
    print "Symbols: ",
    print listOfSymbols
    print "Optimal Allocations: ",
    print allocation
    print "Sharpe Ratio: ",
    print result['sharpe']
    print "Volatility (stdev of daily returns): ",
    print result['vol']
    print "Average Daily Return:",
    print result['daily_ret']
    print "Cumulative Return: ",
    print result['cum_ret']
    print "----------------------------------------------------------------"

def main():
    ''' Main Function'''
    #listOfSymbols = ["AAPL", "GLD", "GOOG", "XOM"]
    #listOfSymbols = ['BRCM', 'TXN', 'IBM', 'HNZ']
    listOfSymbols = ['BRCM', 'ADBE', 'AMD', 'ADI']
    #listOfSymbols = ["AXP", "HPQ", "IBM", "HNZ"]
    #allocation = [0.4, 0.4, 0.0, 0.2]
    #allocation = [0.4, 0.4, 0.0, 0.2]
    startDate = Datetime.datetime(2011,1,1)
    endDate = Datetime.datetime(2011,12,31)
    #endDate = Datetime.datetime(2011,12,31)

    #result = simulate(startDate,endDate,listOfSymbols,allocation)
    #outputPrinter(startDate,endDate,listOfSymbols,allocation,result)

    (highestSharpeRatio, bestAllocation) = portfolioIterator("dataxyz.txt",startDate,endDate,listOfSymbols)

    print "the best allocation for %s : %s" % (str(listOfSymbols), str(bestAllocation))
    print "its corresponding sharpe ratio is %f" % highestSharpeRatio




if __name__ == '__main__':
    main()
