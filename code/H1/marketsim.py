'''
This source code is released under the New BSD license.


Created on 10/2/13

@author: Omer Ansari
@contact: knail1@live.com
@summary: HW3 for Computational Investing 1, Coursera.


# updates HW3 by essentially
# taking the orders_H4.csv as input,
# using initialCashPosition as 50000
# start date as 1/1/08, end date as 12/31/09
# when event occurs buy 100 shares of the equity.
# sell automatically 5 trading days later


Overview
  Read CSV into trades array
  Scan trades for symbols and dates
  Read in data
  Scan trades to update cash
  Scan trades to create ownership array & value
  Scan cash and value to create total fund value

  example:

  Part 1: Create a market simulation tool, marketsim.py that takes a command line like this:
  python marketsim.py 1000000 orders.csv values.csv

  orders.csv:
    2008, 12, 3, AAPL, BUY, 130
    2008, 12, 8, AAPL, SELL, 130
    2008, 12, 5, IBM, BUY, 50

Your simulator should calculate the total value of the portfolio for each day using adjusted closing prices
(cash plus value of equities) and print the result to the file values.csv.
The contents of the values.csv file should look something like this:

2008, 12, 3, 1000000
2008, 12, 4, 1000010
2008, 12, 5, 1000250
...

    Part 2: Create a portfolio analysis tool, analyze.py, to analyze the data, in separate file.


'''

import sys
import csv
import pandas
import numpy
import re as RegularExpressions
import datetime as Datetime
import QSTK.qstkutil.qsdateutil as QSTKDateUtility
import QSTK.qstkutil.DataAccess as QSTKDataAccess

if __name__ == '__main__':

    # for the initial build we will input variables within the script, and print on STDOUT

    initialCashPosition = 1000000
    ordersFileName = 'orders.csv'
    valuesFileName = 'values.csv'

    #ordersFile = open(ordersFileName, 'r')

    #initialCashPosition = 0
    #ordersFileName = ''
    #valuesFileName = ''
    #for arg in sys.argv:
    #        initialCashPosition = arg[1]
    #        ordersFileName = arg[2]
    #        valuesFileName = arg[3]

    valuesFile = open(valuesFileName, 'w')
    #creating a sort of table (separated by CR) of arrays , each item is an array of the specific order details
    orderReader = csv.reader(open(ordersFileName).read().split(), delimiter=',')
    #orderReader2 = orderReader # for later


    symbolArray = []
    datesOfTradesArray = []
    orderReaderArray = []


    for trades in orderReader:
        trades = trades[0:-1]
        print trades
        orderReaderArray.append(trades)
        #[0:-1 cleans last column
        # from: ['2011', '1', '10', 'AAPL', 'Buy', '1500', '']
        # to: ['2011', '1', '10', 'AAPL', 'Buy', '1500']

        #creating a list of symbols
        if symbolArray.__contains__(trades[3]):
            pass
        else:
            symbolArray.append(trades[3])


        #pulling dates from the trade,
        # (a) create a sorted list of dates.
        # (b) find the first and last date from the sorted list
        # (c) create the NYSE daily dates for the trades

        #class datetime.datetime(year, month, day[, hour[, minute[, second[, microsecond[, tzinfo]]]]])
        justADate = Datetime.datetime(int(trades[0]),int(trades[1]),int(trades[2]),16)


        datesOfTradesArray.append(justADate)

    # need to use get NYSE dates function to create an array of the right number of dates

    print "orderReaderArray is",
    print orderReaderArray


    #sort the dates of trades:
    datesOfTradesArray.sort()

    #print "BEFORE 1600 FIX : sorted dates of trades :",
    #print datesOfTradesArray

    #adding 1600hr to the last date of trade so that its included inthe NYSE dates timestamps:


    #CorrectedlastDate = datesOfTradesArray[-1].replace(hour=16)
    #datesOfTradesArray[-1] = CorrectedlastDate
    dateCount = 0
    datesOfTradesArray64 = []
    for eachDate in datesOfTradesArray:
        datesOfTradesArray[dateCount] = datesOfTradesArray[dateCount].replace(hour=16)
        datesOfTradesArray64.append(numpy.datetime64(datesOfTradesArray[dateCount]))
        dateCount += 1


    print "datesOfTradesArray:",
    print datesOfTradesArray

    #now converting dates to numpy.datetime64
    print "datesOfTradesArray64: ",
    print datesOfTradesArray64



    #print "symbolsArray: ",
    #print symbolArray

    EventStudyTimestamps = QSTKDateUtility.getNYSEdays(datesOfTradesArray[0], datesOfTradesArray[-1], Datetime.timedelta(hours=16))

    #print "EventStudyTimestamps  are: ",
    #print EventStudyTimestamps[0]

    #pandasDataFrame = pandas.DataFrame(index=EventStudyTimestamps, columns=symbolArray)

    # now pull in all the stock prices for each NYSE traded data in the range for each stock
    # and plop it into a DataFrame:

    dataObject = QSTKDataAccess.DataAccess('Yahoo', cachestalltime=0)
    #ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ls_keys = ['close']


    StockPriceDataFrame_ = dataObject.get_data(EventStudyTimestamps,symbolArray,ls_keys, verbose=True)

    # bizarre correction, flatting(?) required:
    StockPriceDataFrame = StockPriceDataFrame_[0]
    StockOwnershipDataFrame = StockPriceDataFrame.copy(deep=True) # this way, the size and index/columns of the array is maintained
    StockOwnershipDataFrame = StockOwnershipDataFrame * 0  # fill it with zeros, no ownership of any stock day0

    #print "StockPriceDataFrame is: ",
    #print StockPriceDataFrame

    #print "StockPriceDataFrame.lookup(1,2) is:",
    #StockPriceDataFrame.lookup(StockPriceDataFrame.index.values[-3],"AAPL")

    #print StockPriceDataFrame['AAPL'][StockPriceDataFrame.index.values[0]]

    cashColumnArray = [0]*len(EventStudyTimestamps)
    equityColumnArray = [0]*len(EventStudyTimestamps)

    # now we will iterate through each of the trading days, and look for
    # the days where we place the orders, and update cashPosition based on buy/sell.
    # For the days there is no trade, we will just copy the last cashPosition in.


    day = 0
    tradeSpecifics = []
    ongoingCashPostion = initialCashPosition
    orig_stdout = sys.stdout # saving original STDOUT filehandle
    sys.stdout = valuesFile


    for eachDayInRange in StockPriceDataFrame.index.values:

        if datesOfTradesArray64.__contains__(eachDayInRange):

            # there was a trade or more this day, lets find all the trades that happened this day

            for eachTrade in orderReaderArray:
                #convert the date from eachTrade ['2011', '1', '10', 'AAPL', 'Buy', '1500']
                #to numpy.datetime64, with 1600 offset
                tempDateOfTrade = numpy.datetime64(Datetime.datetime(int(eachTrade[0]), int(eachTrade[1]), int(eachTrade[2]), 16))

                #now look throgh each trade and match the date of the trade
                if eachDayInRange == tempDateOfTrade:
                    #look for which symbol was traded and update cash position
                    #format: dataframe['GOOG'][date]
                    stockPrice = StockPriceDataFrame[eachTrade[3]][tempDateOfTrade]


                    tradeDollarValue = stockPrice * int(eachTrade[5])


                    if eachTrade[4] == 'Buy':
                        ongoingCashPostion -= tradeDollarValue
                        #print "Day %d, %s : Buying %s stocks of %s, each worth %d , total tradeValue: %d, cashPosition: %d" \
                        #      % (day+1, str(tempDateOfTrade), eachTrade[5], eachTrade[3], stockPrice, tradeDollarValue, ongoingCashPostion)

                        #also update stockownership data frame with the stocks bought, notice the ":" for perpuity hold
                        StockOwnershipDataFrame[eachTrade[3]][tempDateOfTrade:] += int(eachTrade[5])


                    elif eachTrade[4] == 'Sell':
                        ongoingCashPostion += tradeDollarValue
                        #print "Day %d, %s : Selling %s stocks of %s, each worth %d , total tradeValue: %d, cashPosition: %d" \
                        #      % (day+1, str(tempDateOfTrade), eachTrade[5], eachTrade[3], stockPrice, tradeDollarValue, ongoingCashPostion)

                        #also update stockownership data frame with the stocks Sold, notice the ":" for perpetuity
                        StockOwnershipDataFrame[eachTrade[3]][tempDateOfTrade:] -= int(eachTrade[5])
                        #print "stockOwnershipDataFrame is:",
                        #print StockOwnershipDataFrame[eachTrade[3]][tempDateOfTrade]



            #insert final cash position into the cash array value for that day
            cashColumnArray[day] = ongoingCashPostion

        else:
            #no trade this day so no change in cash position from yesterday
            cashColumnArray[day] = cashColumnArray[day-1]


        equityValueDataFrame = StockOwnershipDataFrame * StockPriceDataFrame
        # don't need to do the above with each iteration,
        # but want to see the growing/shrinking equity with each day


        for eachSymbol in equityValueDataFrame:
            equityColumnArray[day] = equityColumnArray[day] + equityValueDataFrame[eachSymbol][eachDayInRange]


        print "cash+equity position for day %d , %s :  %d+%d = %d" % (day+1, eachDayInRange, cashColumnArray[day], equityColumnArray[day], cashColumnArray[day]+equityColumnArray[day])

        #print type(numpy.datetime_as_string(eachDayInRange))

        regexp = RegularExpressions.compile("^(\d+)-(\d+)-(\d+)")
        yearMonthDayArray = regexp.match(str(eachDayInRange))
        #print yearMonthDayArray.group(1)


        print "%s, %s, %s, %d" % (yearMonthDayArray.group(1), yearMonthDayArray.group(2), yearMonthDayArray.group(3), cashColumnArray[day]+equityColumnArray[day])

        day += 1

    valuesFile.close()

    #equityValueDataFrame = StockOwnershipDataFrame * StockPriceDataFrame

    #print "equityValueDataFrame is:",
    #print equityValueDataFrame.columns.values
    #print equityValueDataFrame["AAPL"][0]

    #print "stockOwnershipDataFrame is:",
    #print StockOwnershipDataFrame.iloc[0][0]


    #print StockPriceDataFrame.columns.values[3]
    #print type(StockPriceDataFrame.index.values[-3])
    #print StockPriceDataFrame.iloc[0][3]
