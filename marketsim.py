import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import datetime as dt
import QSTK.qstkstudy.EventProfiler as ep
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import csv

orderfile = 'orders1.csv'
valuefile = 'values1.csv'

def take_data(dt_start, dt_end, symbols):
    dataobj = da.DataAccess('Yahoo')
    dt_timeofday = dt.timedelta(hours=16)
    dt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(dt_timestamps, symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
    return d_data

def analyse(dt_start, dt_end, fund, index):
    print
    # print dt_start.__str__()+" to "+dt_end._str__()
    print "Portfolio ",fund.iloc[-1]
    na_rets = fund['Value']
    tsu.returnize0(na_rets)
    #print na_rets
    average_daily_return = na_rets.sum()/na_rets.size
    cummulative_return = sum(na_rets)
    stdev = np.std(na_rets)
    sharpe = 252**0.5 * average_daily_return/stdev

    print "Average Daily Return: ",average_daily_return
    print "Cummulative Return: ",cummulative_return
    print "Volatility (stdev of daily returns): ",stdev
    print "Sharpe Ratio: ",sharpe



def simtrades(orderfile, valuefile):
    orders = []
    dates = []
    symbols =[]
    reader = csv.reader(open(orderfile, 'rU'), delimiter=',')
    for row in reader:
        order = []
        yr, mth, day, sym, typ, num = row
        dates.append(dt.datetime(int(yr), int(mth), int(day)))
        symbols.append(sym)
        order.append(dt.datetime(int(yr), int(mth), int(day)))
        order.append(sym)
        order.append(typ)
        order.append(int(num))
        orders.append(order)

    sdates = list(set(dates))
    ssymbols = list(set(symbols))
    sdates.sort()
    # print sdates
    orders.sort(key= lambda order:order[0])
    dt_start = sdates[0]
    # print dt_start
    # dt_end = sdates[0] + dt.timedelta(days=10)
    dt_end = sdates[-1] + dt.timedelta(days=1)
    # print dt_end
    d_data = take_data(dt_start,dt_end, ssymbols)
    actual_closes = d_data['close']
    trades = actual_closes * 0
    ssymbols.append('Cash')
    trades['Cash'] = 0
    trades['Cash'][dt_start + dt.timedelta(hours=16)] = 100000
    # print actual_closes
    # print trades
    actual_closes['Cash'] = 1.0

    for order in orders:
        date, sym, typ, num = order
        date = date + dt.timedelta(hours=16)
        # print order
        # print trades[sym][date + dt.timedelta(hours=16)]
        if typ == 'Buy':
            trades[sym][date] += num
            trades['Cash'][date] -= num*actual_closes[sym][date]
        elif typ == 'Sell':
            trades[sym][date] -= num
            trades['Cash'][date] += num*actual_closes[sym][date]
    # print trades

    # print len(trades)
    for sym in ssymbols:
        for i in range(1,len(trades)):
            trades[sym].iloc[i] += trades[sym].iloc[i-1]
    # print actual_closes
    # print trades
    ts_fund = actual_closes * trades
    ts_fund['Value'] = sum([ts_fund[sym] for sym in ssymbols])
    for sym in ssymbols:
        del ts_fund[sym]

    # print trades[:5]
    # print actual_closes[:5]
    # print ts_fund[:5]
    # print ts_fund[-5:]

    writer = csv.writer(open(valuefile, 'wb'), delimiter = ',')
    # print ts_fund.index
    for row_index in ts_fund.index:
        # row_index
        val =  ts_fund['Value'][row_index]
        row_to_enter = [row_index.year,row_index.month,row_index.day, val]
        writer.writerow(row_to_enter)

    analyse(None,None,ts_fund,None)

simtrades(orderfile,valuefile)
