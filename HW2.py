import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import datetime as dt
import QSTK.qstkstudy.EventProfiler as ep
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import csv
##import marketsim

opp = {"Buy":"Sell","Sell":"Buy"}
def event_profiler(dt_start, dt_end, spyear, event,hold,todo, file_name, orderfile, valuefile):
    dataobj = da.DataAccess('Yahoo')
    symbols = dataobj.get_symbols_from_list("sp500" + spyear)
    symbols = dataobj.get_symbols_from_list("test")
    symbols.append('SPY')
    # print symbols
    dt_timeofday = dt.timedelta(hours=16)
    dt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    d_data = take_data(dt_start, dt_end, symbols, "actual_close")
    # print d_data
    prices = d_data["actual_close"]
    #print type(prices)
    df_events = prices
    df_events = df_events * np.NAN
    #print df_events
    #print prices
    count = 0
    orders = []
    bollval = bollinger(dt_start,dt_end,symbols,20)
    prices = bollval
    for sym in symbols:
        for i in range(1, len(dt_timestamps)):
            if event(sym, i, prices, dt_timestamps):
                od = dt_timestamps[i]
                orders.append([od.year,od.month,od.day,sym,todo,100])
                sd = dt_timestamps[i+hold] if i+hold<len(dt_timestamps) else dt_timestamps[-1]
                orders.append([sd.year,sd.month,sd.day,sym,opp[todo],100])
                df_events[sym].ix[dt_timestamps[i]] = 1
                count += 1
                print count
    print "No of orders ",count*2
    writer = csv.writer(open(orderfile, 'wb'), delimiter = ',')
    # print ts_fund.index
    for order in orders:
        writer.writerow(order)
    # marketsim.simtrades(orderfile, valuefile)
    # print "Creating Study"
    print "df_events"
    print df_events
    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                 s_filename= file_name, b_market_neutral=True, b_errorbars=True,
                 s_market_sym='SPY')
    print "Done"

def event(sym,i,prices, timestamps):
    today = prices[sym].ix[timestamps[i]]
    yest = prices[sym].ix[timestamps[i-1]]
    return yest>= -1.0 and today <= -1.0 and prices["SPY"].ix[timestamps[i]] >= 1.0


def take_data(dt_start, dt_end, symbols, type_data=None):
    dataobj = da.DataAccess('Yahoo')
    dt_timeofday = dt.timedelta(hours=16)
    dt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(dt_timestamps, symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method = 'ffill')
        d_data[s_key] = d_data[s_key].fillna(method = 'bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
    return d_data


def bollinger(dt_start, dt_end, symbols, lookback):
    d_data = take_data(dt_start-dt.timedelta(days=(lookback/5+2) * 7), dt_end, symbols)
    prices = d_data["close"]
    # print prices
    dt_timeofday = dt.timedelta(hours=16)
    dt_timestamps = du.getNYSEdays(dt_start-dt.timedelta(days=(lookback/5+2) * 7), dt_end, dt_timeofday)
    ind = dt_timestamps.index(du.getNYSEdays(dt_start, dt_start+dt.timedelta(days=7),dt_timeofday )[0])
    # mov_avg = prices * np.NAN
    # upperband = prices * np.NAN
    # lowerband = prices * np.NAN
    # bollingerval = prices * np.NAN
    # for sym in symbols:
    #     for i in range(ind, len(dt_timestamps)):
    #         price = prices[sym].ix[dt_timestamps[i]]
    #         avg = sum([prices[sym].ix[dt_timestamps[i-j]] for j in range(lookback)])/float(lookback)
    #         dev = (sum([(prices[sym].ix[dt_timestamps[i-j]]-avg)**2 for j in range(lookback)])/float(lookback))**0.5
    #         bollingerval[sym].ix[dt_timestamps[i]] = (price-avg)/dev
    mov_avg = pd.rolling_mean(prices, lookback)
    std_dev = pd.rolling_std(prices, lookback)
    bollingerval = (prices-mov_avg)/std_dev
    return bollingerval.ix[ind:,:]



dt_start = dt.datetime(2012,1,1)
dt_end = dt.datetime(2012,2,28)
# bollingerval = bollinger(dt_start, dt_end, ["AAPL","MSFT"], 20)
# print bollingerval

event_profiler(dt_start, dt_end, "2012", event, 5, "Buy", "EventbollSP2012.pdf", "orders1.csv", "values12.csv")

