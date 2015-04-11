__author__ = 'Shrirang Mundada'

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import datetime as dt
import QSTK.qstkstudy.EventProfiler as ep
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import copy
import csv
from Events import find_events
from Helper import take_data


# Store filename
s_filename='Boll2012SD2.pdf'

# Start date
dt_start = dt.datetime(2012, 1, 1)

# End date
dt_end = dt.datetime(2012, 12, 31)

# Market Index to compare with
market_sym='SPY'

# Symbol list
dataobj = da.DataAccess('Yahoo')
ls_symbols = dataobj.get_symbols_from_list('sp5002012')
ls_symbols.append(market_sym)

## Edit/Customize Events in Events.py file
##................................................................................

d_data = take_data(dt_start,dt_end,ls_symbols)
ldt_timestamps = d_data["close"].index
events = find_events(ls_symbols, dt_start, dt_end)
df_events = events.copy()
df_events = df_events * np.NaN
for sym in ls_symbols:
    for i in range(1, len(ldt_timestamps)):
        if events[sym].ix[ldt_timestamps[i]] >= 1:
            df_events[sym].ix[ldt_timestamps[i]] = 1

print df_events
print "Creating Study"
ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename=s_filename, b_market_neutral=True, b_errorbars=True,
                s_market_sym = market_sym)
print "Done.."
