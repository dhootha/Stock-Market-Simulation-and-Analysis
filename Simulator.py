__author__ = 'Shrirang Mundada'

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
from Events import find_events
from Helper import take_data


# Start date
dt_start = dt.datetime(2008, 1, 1)

# End date
dt_end = dt.datetime(2012,12, 31)

# Market Index to compare with
s_market_sym='SPY'

# Symbol list
dataobj = da.DataAccess('Yahoo')
ls_symbols = dataobj.get_symbols_from_list('sp5002012')
ls_symbols.append(s_market_sym)

## Edit/Customize Events in Events.py file
##................................................................................
dt_timeofday = dt.timedelta(hours=16)
dt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

df_events = find_events(ls_symbols, dt_start,dt_end)
#print df_events

def create_alloc(ls_symbols,dt_timestamps,df_events):
    alloc = df_events.copy()
    del alloc[s_market_sym]
    alloc.iloc[:] = 0
    alloc['_CASH'] = 1
    for sym in ls_symbols[:-1]:
        for date in range(1,len(dt_timestamps)):
            val = df_events[sym].ix[dt_timestamps[date]]
            if val == 1 or val == 0:
##                print "Val present"
                if val == 1:
                    alloc[sym].ix[dt_timestamps[date]] = 1
                else:
                    alloc[sym].ix[dt_timestamps[date]] = 0
            else:
##                print "In else"
                alloc[sym].ix[dt_timestamps[date]] = alloc[sym].ix[dt_timestamps[date-1]]
                
    return alloc

alloc = create_alloc(ls_symbols,dt_timestamps,df_events)

##historic_data = pd.DataFrame(d_data['close'])
##del historic_data[s_market_sym]

d_data = take_data(dt_start,dt_end,ls_symbols[:-1])
historic_data = d_data

print alloc
portfolio,lev,comm,slip,bor = sim.tradesim_comb( alloc, historic_data,f_start_cash = 1000000, i_leastcount=1,
            b_followleastcount=True, f_slippage=0.0,
            f_minimumcommision=0.0, f_commision_share=0.0,
            i_target_leverage=1, f_rate_borrow = 0.0, log="ID8.csv", b_exposure=False)


report.print_html(portfolio[1::2],["SPY"], "ID8 bollinger_fund SD1",lf_dividend_rets=0.0, original="",
    s_fund_name="Bollinger_fund with SD 1", s_original_name="Original", d_trading_params="", d_hedge_params="",
    s_comments="", directory="Report", leverage=False, s_leverage_name="Leverage",commissions=0, slippage=0,
    borrowcost=0, i_start_cash=100000)
