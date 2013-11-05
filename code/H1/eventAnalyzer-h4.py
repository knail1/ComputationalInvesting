'''
Copyright (c) 2011, 2012, Georgia Tech Research Corporation (GTRC) All rights reserved.
This source code is released under the New BSD license.

Updated 10/9/2013

@author: Sourabh Bajaj, updated by Omer Ansari
@summary: H4 , coursera, comp investing
instead of putting a 1 we will output to a file


(1)eventAnalyzer-h4.py ---> (2)marketsim-h4.py ----> (3)results-h4.py

# (1):
 run the event, and when event happens
    create the orders_H4.csv and put in it:
    order to buy 100 shares of the equity.
    order to sell 100 shares five NYSE days later
        in format:
        Date, AAPL, BUY, 100
        Date + 5 days, AAPL, SELL, 100
        e.g 2011,1,10,AAPL,Buy,100,

# (2): take orders_H4.csv as input and run the analysis create values-h4.py
            essentially no material change from H3 script1 (marketsim.py)
# (3): take values-h4.py and create the metrics, sharpe ratio etc
            essentially no material change from H3 script2 (analyze.py)


# using initialCashPosition as 50000
# start date as 1/1/08, end date as 12/31/09


'''


import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep
import re as RegularExpressions
import pandas as pd

"""
Accepts a list of symbols along with start and end date
Returns the Event Matrix which is a pandas Datamatrix
Event matrix has the following structure :
    |IBM |GOOG|XOM |MSFT| GS | JP |
(d1)|nan |nan | 1  |nan |nan | 1  |
(d2)|nan | 1  |nan |nan |nan |nan |
(d3)| 1  |nan | 1  |nan | 1  |nan |
(d4)|nan |  1 |nan | 1  |nan |nan |
...................................
...................................
Also, d1 = start date
nan = no information about any event.
1 = status bit(positively confirms the event occurence)
"""


def find_events(ls_symbols, d_data, ordersFile):
    ''' Finding the event dataframe '''
    df_close = d_data['actual_close']
    ts_market = df_close['SPY']
    regexpForYearMonthDay = RegularExpressions.compile("^(\d+)-(\d+)-(\d+)")


    print "Finding Events"

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_close.index

    for s_sym in ls_symbols:
        print "analyzing events for :",
        print s_sym
        for i in range(1, len(ldt_timestamps)):
            print "analyzing day:",
            print i
            # Calculating the returns for this timestamp
            f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]
            #f_marketprice_today = ts_market.ix[ldt_timestamps[i]]
            #f_marketprice_yest = ts_market.ix[ldt_timestamps[i - 1]]
            #f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1
            #f_marketreturn_today = (f_marketprice_today / f_marketprice_yest) - 1

            # Event is found if the symbol price today is less than $5 and was >= $5 yesterday

            if f_symprice_today < 9.0 and f_symprice_yest >= 9.0:
                yearMonthDayArrayForBuy = regexpForYearMonthDay.match(str(ldt_timestamps[i]))
                orderToBuy = yearMonthDayArrayForBuy.group(1) + "," + yearMonthDayArrayForBuy.group(2) + "," + yearMonthDayArrayForBuy.group(3) + "," + s_sym + ",Buy,100,\n"
                ordersFile.write(orderToBuy)

                yearMonthDayArrayForSell = regexpForYearMonthDay.match(str(ldt_timestamps[i+5]))
                orderToSell = yearMonthDayArrayForSell.group(1) + "," + yearMonthDayArrayForSell.group(2) + "," + yearMonthDayArrayForSell.group(3) + "," + s_sym + ",Sell,100,\n"
                ordersFile.write(orderToSell)


    return df_events


if __name__ == '__main__':
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    #print ldt_timestamps[0].
    #print type(ldt_timestamps[0])
    dataobj = da.DataAccess('Yahoo', cachestalltime=0)
    ls_symbols = dataobj.get_symbols_from_list('sp5002012')
    ls_symbols.append('SPY')

    #ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ls_keys = ['close', 'actual_close']
    #ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys, verbose=True)
    #d_data = dict(zip(ls_keys, ldf_data))
    #close = d_data['close']
    #aclose = d_data['actual_close']
    #close.save('closeData.txt')
    #aclose.save('acloseData.txt')

    close = pd.load("closeData.txt")
    aclose = pd.load("acloseData.txt")

    d_data = {'close': close, 'actual_close': aclose}


    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    ordersFile = open("orders_H4.csv", 'w')
    df_events = find_events(ls_symbols, d_data, ordersFile)
    ordersFile.close()

    #print "Creating Study"
    #ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
    #            s_filename='MyEventStudy-sp500-2012-q3.pdf', b_market_neutral=True, b_errorbars=True,
    #            s_market_sym='SPY')
