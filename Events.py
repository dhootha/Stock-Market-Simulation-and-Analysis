import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import QSTK.qstksim as sim
import QSTK.qstktools.report as report
import datetime as dt
import QSTK.qstkstudy.EventProfiler as ep
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import copy
import csv
from Helper import take_data


def find_events(ls_symbols, dt_start, dt_end):
    ''' Finding the event dataframe '''
    d_data = take_data(dt_start,dt_end,ls_symbols)
    df_close = d_data['close']
    ts_market = df_close['SPY']

    print "Finding Events"

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_close.index
    
##    for s_sym in ls_symbols:
##        for i in range(1, len(ldt_timestamps)):
##            # Calculating the returns for this timestamp
##            f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
##            f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]
##            f_marketprice_today = ts_market.ix[ldt_timestamps[i]]
##            f_marketprice_yest = ts_market.ix[ldt_timestamps[i - 1]]
##            f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1
##            f_marketreturn_today = (f_marketprice_today / f_marketprice_yest) - 1
##
##            # Event is found if the symbol is down more then 3% while the
##            # market is up more then 2%
##            if f_symreturn_today <= -0.03 and f_marketreturn_today >= 0.02:
##                df_events[s_sym].ix[ldt_timestamps[i]] = 1
    bollval = bollinger(dt_start,dt_end,ls_symbols)
    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            val = bollval[s_sym].ix[ldt_timestamps[i]]
##            print val
            if val== 1.0:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1
            elif val == 0.0:
                df_events[s_sym].ix[ldt_timestamps[i]] = 0
    print "events"
    print df_events             
    return df_events

def bollinger(dt_start,dt_end, ls_symbols, lookback=20):
    dt_end += dt.timedelta(days = 2)
    d_data = take_data(dt_start-dt.timedelta(days=(lookback/5+2) * 7), dt_end, ls_symbols)
    prices = d_data["close"]
    dt_timeofday = dt.timedelta(hours=16)
    dt_timestamps = du.getNYSEdays(dt_start-dt.timedelta(days=(lookback/5+2) * 7), dt_end, dt_timeofday)
    ind = dt_timestamps.index(du.getNYSEdays(dt_start, dt_start+dt.timedelta(days=7),dt_timeofday )[0])
    mov_avg = pd.rolling_mean(prices, lookback)
    std_dev = pd.rolling_std(prices, lookback)
    bollingerval = (prices-mov_avg)/std_dev
    df = bollingerval.ix[ind:,:]
#    print df
    bollval = copy.deepcopy(df)
    df = df * np.NAN
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    count = 0
    for s_sym in ls_symbols:
        flag = False
        for i in range(1, len(ldt_timestamps)):
            val = bollval[s_sym].ix[ldt_timestamps[i]]
            valy = bollval[s_sym].ix[ldt_timestamps[i-1]]
            market = bollval['SPY'].ix[ldt_timestamps[i]]
            if not flag and val >= -1 and valy < -1 and market > 0:
##                print "hello"
                df[s_sym].ix[ldt_timestamps[i]] = 1
##                if i+20 < len(ldt_timestamps):
##                    df[s_sym].ix[ldt_timestamps[i+20]] = 0
##                else:
##                    df[s_sym].ix[ldt_timestamps[-1]] = 0
                count +=1
                flag = True
            if flag and abs(market - val) <= 0.5:
                df[s_sym].ix[ldt_timestamps[i]] = 0
                flag = False
##            else:
##                bollval[s_sym].ix[ldt_timestamps[i]] = np.NAN
##            else:
##                bollval[s_sym].ix[ldt_timestamps[i]] = 0
##            elif market - val > 1:
##                bollval[s_sym].ix[ldt_timestamps[i]] = -2
##            else:
##                bollval[s_sym].ix[ldt_timestamps[i]] = 0
#    print bollval
    print "Total Events :",count
    return df

##dt_start = dt.datetime(2010,12,23)
##dt_end = dt.datetime(2010,12,30)
##bollingerval = bollinger(dt_start, dt_end, ["AAPL","MSFT"], 20)
##print bollingerval
