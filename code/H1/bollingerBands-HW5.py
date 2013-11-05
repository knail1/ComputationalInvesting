'''
This source code is released under the New BSD license.


Created on 10/24/13

@author: Omer Ansari
@contact: knail1@live.com
@summary: HW5 for Computational Investing 1, Coursera.

implementing bollinger bands

Part 1: Implement Bollinger bands as an indicator using 20 day look back.
Create code that generates a chart showing the rolling mean, the stock price,
and upper and lower bands. The upper band should represent the mean plus one standard
deviation and here the lower band is the mean minus one standard deviation.
Traditionally the upper and lower Bollinger bands are 2 standard deviations but for this
assignment we would use a tighter band of 1 or a single standard deviation.

Part 2: Have your code output the indicator value in a range of -1 to 1. Yes, those
values can be exceeded, but the intent is that +1 represents the situation where the
price is at +1 standard deviations above the mean. To convert the present value of
Bollinger bands into -1 to 1:

    Bollinger_val = (price - rolling_mean) / (rolling_std)

You should run two experiments.
Experiment 1: Implement Bollinger bands and convert the value between -1 and 1.
Then create a plot for the timeframe between Jan 1, 2010 to Dec 31,2010 for Google.
Symbol: GOOG
Startdate: 1 Jan 2010
Enddate: 31 Dec 2010
20 period lookback
Experiment 2: Implement an indicator of your own choice and create a similar chart.
For both experiments, you should:
The plot should have two subplots, one showing the price history of the equity and
the other showing the indicator value.

Example Output

Output for 4 equities, using pandas to calculate bollinger band values.
Lookback = 20 days.
                         AAPL      GOOG       IBM      MSFT
2010-12-23 16:00:00  1.185009  1.298178  1.177220  1.237684
2010-12-27 16:00:00  1.371298  1.073603  0.590403  0.932911
2010-12-28 16:00:00  1.436278  0.745548  0.863406  0.812844
2010-12-29 16:00:00  1.464894  0.874885  2.096242  0.752602
2010-12-30 16:00:00  0.793493  0.634661  1.959324  0.498395



'''


import pandas
import matplotlib.pyplot as plt
import datetime as Datetime
import QSTK.qstkutil.qsdateutil as QSTKDateUtility
import QSTK.qstkutil.DataAccess as QSTKDataAccess



if __name__ == '__main__':

    startDate = Datetime.datetime(2010, 3, 12)
    endDate = Datetime.datetime(2010, 6, 28)
    #symbolArray = ['BRCM', 'ADBE', 'AMD', 'ADI']
    symbolArray = ['AAPL', 'GOOG', 'IBM', 'MSFT']
    lookBack = 20


    EventStudyTimestamps = QSTKDateUtility.getNYSEdays(startDate, endDate, Datetime.timedelta(hours=16))


    #print "EventStudyTimestamps  are: ",
    #print EventStudyTimestamps[0]

    dataObject = QSTKDataAccess.DataAccess('Yahoo', cachestalltime=0)
    #ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ls_keys = ['close']


    StockPriceDataFrame_ = dataObject.get_data(EventStudyTimestamps, symbolArray, ls_keys, verbose=True)

    # bizarre correction, flattening(?) required:
    StockPriceDataFrame = StockPriceDataFrame_[0]

    #StockPriceDataFrame = SPDF
    SPDFMean = pandas.rolling_mean(StockPriceDataFrame, 20)
    SPDFStdDev = pandas.rolling_std(StockPriceDataFrame, 20)



    bollingerDataFrame = (StockPriceDataFrame - SPDFMean) / SPDFStdDev

    print bollingerDataFrame.tail()

        # Plotting the prices with x-axis=timestamps
    '''
    #this block prints out the pdf graph for bollinger bands
    plt.clf()
    plt.subplot(211)
    plt.plot(EventStudyTimestamps, StockPriceDataFrame['GOOG'], label='Google')
    plt.legend()
    plt.ylabel('Price')
    plt.xlabel('Date')
    plt.xticks(size='xx-small')
    plt.xlim(EventStudyTimestamps[0], EventStudyTimestamps[-1])
    plt.subplot(212)
    plt.plot(EventStudyTimestamps, bollingerDataFrame['GOOG'], label='Google-Bollinger')
    plt.axhline(1.0, color='r')
    plt.axhline(-1.0, color='r')
    plt.legend()
    plt.ylabel('Bollinger')
    plt.xlabel('Date')
    plt.xticks(size='xx-small')
    plt.xlim(EventStudyTimestamps[0], EventStudyTimestamps[-1])
    plt.savefig('homework5.pdf', format='pdf')
    '''

