import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def simulate(dt_start, dt_end, symbols, allocations):
    dt_timeofday = dt.timedelta(hours=16)
    dt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    c_dataobj = da.DataAccess('Yahoo')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = c_dataobj.get_data(dt_timestamps, symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    na_price = d_data['close'].values
    na_normalized_price = na_price / na_price[0, :]
    port = na_normalized_price * allocations
    portval = np.array([sum(day) for day in port])
    na_rets = portval.copy()
    tsu.returnize0(na_rets)
    average_daily_return = na_rets.sum()/na_rets.size
    cummulative_return = portval[-1]
    stdev = np.std(na_rets)
    sharpe = portval.size**0.5 * average_daily_return/stdev
    return sharpe,stdev,average_daily_return,cummulative_return
##    #print d_data
##    #print na_price
##    #print na_normalized_price
##    #print port
##    #print portval
##    #print na_rets
    print "Average Daily Return: ",average_daily_return
    print "Cummulative Return: ",cummulative_return
    print "Volatility (stdev of daily returns): ",stdev
    print "Sharpe Ratio: ",sharpe


def optimization(startdate,enddate,symbols):
    n = 10.0
    allocations =   ([a/n,b/n,c/n,d/n]
                      for a in range(0,11)
                      for b in range(0,11)
                      for c in range(0,11)
                      for d in range(0,11)
                      if a+b+c+d == 10)
    max_sharpe = 0.0
    optimal_allocations = [1.0,0,0,0]
    for allocation in allocations:
        sharpe,stdev,average_daily_return,cummulative_return=simulate(startdate, enddate, symbols, allocation)
        if sharpe > max_sharpe:
            max_sharpe = sharpe
            optimal_allocation = allocation
    sharpe,stdev,average_daily_return,cummulative_return=simulate(startdate, enddate, symbols, optimal_allocation)
    print
    print "Average Daily Return: ",average_daily_return
    print "Cummulative Return: ",cummulative_return
    print "Volatility (stdev of daily returns): ",stdev
    print "Sharpe Ratio: ",sharpe
    print "Optimal Allocation: ",optimal_allocation


startdate = dt.datetime(2011, 1, 1)
enddate = dt.datetime(2011, 12, 31)
optimization(startdate, enddate, ['AAPL','GLD','GOOG','XOM'])

startdate = dt.datetime(2010, 1, 1)
enddate = dt.datetime(2010, 12, 31)
optimization(startdate, enddate, ['AXP','HPQ','IBM','HNZ'])

startdate = dt.datetime(2011, 1, 1)
enddate = dt.datetime(2011, 12, 31)
optimization(startdate, enddate, ['BRCM','TXN','AMD','ADI'])


