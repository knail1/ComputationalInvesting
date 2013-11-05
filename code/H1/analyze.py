'''
This source code is released under the New BSD license.


Created on 10/2/13

@author: Omer Ansari
@contact: knail1@live.com
@summary: HW3 for Computational Investing 1, Coursera.

Overview
  Read CSV into trades array
  Scan trades for symbols and dates
  Read in data
  Scan trades to update cash
  Scan trades to create ownership array & value  Scan cash and value to create total fund value

  example:

  Part 1: Create a market simulation tool, marketsim.py that takes a command line like this:
  python marketsim.py 1000000 orders.csv values.csv

    in separate python file.

    Part 2: Create a portfolio analysis tool, analyze.py, to analyze the data, in separate file.

    python analyze.py values.csv \$SPX

    The tool should read in the daily values (cumulative portfolio value) from values.csv and plot them. It should use the symbol on the command line as a benchmark for comparison (in this case $SPX). Using this information, analyze.py should:

    . Plot the price history over the trading period.
    . Your program should also output:
    . Standard deviation of daily returns of the total portfolio
    . Average daily return of the total portfolio
    . Sharpe ratio (Always assume you have 252 trading days in an year. And risk free rate = 0) of the total portfolio
    . Cumulative return of the total portfolio
'''


import QSTK.qstkutil.tsutil as TSUtility
import QSTK.qstkutil.qsdateutil as DateUtility
import QSTK.qstkutil.DataAccess as DataAccess
import numpy as Numpy
import csv
import pandas as pd
import datetime as Datetime

if __name__ == '__main__':

    # for the initial build we will input variables within the script, and print on STDOUT


    valuesFileName = 'values.csv'
    baselineFund = ""

    symbolArray = ['$SPX']



    #creating a sort of table (separated by CR) of arrays , each item is an array of the specific value details
    valuesReader = csv.reader(open(valuesFileName), delimiter=',')

    #print valuesReader
    justValues = []
    justCumValues = []


    #df_values = pd.read_csv(valuesFileName, names =['date', 'value'])
    #df_values = df_values.drop(df_values.index[:1])
    #ldt_timestamps = df_values['date']

    #na_price = df_values['value'].values

    i = 0

    #print valuesReader
    normalizedValue = 1.0
    lastYr = 0
    lastMo = 0
    lastDay = 0
    for values in valuesReader:
        if i == 0:
            baseline = float(values[3])
            startDate = Datetime.datetime(int(values[0]), int(values[1]), int(values[2]),16)
        normalizedValue = (int(values[3])*1.0)/baseline
        justValues.append(normalizedValue)
        lastYr = int(values[0])
        lastMo = int(values[1])
        lastDay = int(values[2])

        i += 1

    endDate = Datetime.datetime(lastYr,lastMo,lastDay,16)
    cumulativeReturn=justValues[-1]


    # calculating the $SPX or passed index numbers from here :


    timeOfDayToCalculateAt = Datetime.timedelta(hours=16) # 16 = 1600 from epoch so 4pm

    #print "startdate: ",
    #print startDate
    #print "endDate: ",
    #print endDate
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

    print "ClosingPrices:"
    print closingPrices

    normalizedClosingPrices= closingPrices / closingPrices[0, :] # divide all rows by the first row, inclusive
    print "normalizedClosingPrices:"
    print normalizedClosingPrices

    allocatedClosingPrices = normalizedClosingPrices*1 # 100% allocated!

    print "allocatedClosingPrices is:",
    print allocatedClosingPrices


    dailyValueOfPortfolio = Numpy.zeros((len(allocatedClosingPrices),1))
    for row in xrange(len(allocatedClosingPrices)):
        dailyValueOfPortfolio[row-1] = Numpy.sum(allocatedClosingPrices[row-1,:])


    print "dailyValueOfPortfolio",
    print dailyValueOfPortfolio

    SPX_backupOfDailyValueOfPortfolio = Numpy.array(dailyValueOfPortfolio.copy(), dtype=float)



    SPX_averageDailyReturnsArrayFromQSTK = TSUtility.returnize0(dailyValueOfPortfolio)
    averageDailyReturnsArrayFromQSTK = TSUtility.returnize0(justValues)

    stdDevOfDailyReturns=Numpy.std(averageDailyReturnsArrayFromQSTK)
    SPX_stdDevOfDailyReturns=Numpy.std(SPX_averageDailyReturnsArrayFromQSTK)

    avgDailyReturn=Numpy.average(averageDailyReturnsArrayFromQSTK)
    SPX_avgDailyReturn=Numpy.average(SPX_averageDailyReturnsArrayFromQSTK)
    sharpeRatio= 252**0.5 * avgDailyReturn/stdDevOfDailyReturns
    SPX_sharpeRatio= 252**0.5 * SPX_avgDailyReturn/SPX_stdDevOfDailyReturns

    SPX_dailyCumReturnsOfPortfolio = Numpy.zeros((len(allocatedClosingPrices),1))
    SPX_dailyCumReturnsOfPortfolio[0,0] = SPX_backupOfDailyValueOfPortfolio[0,0]


    #print "    dailyCumReturnsOfPortfolio[0,0]"
    #print dailyCumReturnsOfPortfolio[0,0]


    for row in xrange(len(allocatedClosingPrices)):
            if (row != (len(allocatedClosingPrices) -1)):
                SPX_dailyCumReturnsOfPortfolio[row+1,0] = SPX_dailyCumReturnsOfPortfolio[row,0] * (1 + averageDailyReturnsArrayFromQSTK[row,0])


    SPX_cumulativeReturn=normalizedClosingPrices[-1]

    print "sharpeRatio of fund:",
    print sharpeRatio
    print "sharpeRatio of comp. fund:",
    print SPX_sharpeRatio

    print "totalReturn of fund:",
    print cumulativeReturn
    print "totalReturn of comparison symbol:",
    print SPX_cumulativeReturn

    print "stdDevOfDailyReturns of fund:",
    print stdDevOfDailyReturns
    print "stdDevOfDailyReturns of comp. fund:",
    print SPX_stdDevOfDailyReturns

    print "avgDailyReturn of fund:",
    print avgDailyReturn
    print "avgDailyReturn of comp. fund:",
    print SPX_avgDailyReturn
