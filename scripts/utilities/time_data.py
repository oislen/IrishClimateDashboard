import datetime
import pandas as pd

def time_data(data, agg_dict, time_span = None, counties = None, strftime = None):
    """"""
    agg_data = data.assign(date = data['date'].dt.strftime(strftime)).copy()
    agg_data['date'] = pd.to_datetime(agg_data['date'], format = strftime)
    group_cols = ['county', 'date']
    agg_data = agg_data.groupby(group_cols, as_index = False).agg(agg_dict).reset_index()
    # if filtering date with respect to timespan
    if time_span != None:
        time_span_lb = (agg_data['date'] >= datetime.datetime.strptime(time_span[0], strftime))
        time_span_ub = (agg_data['date'] <= datetime.datetime.strptime(time_span[1], strftime))
        agg_data = agg_data.loc[time_span_lb & time_span_ub, :]
    # if filtering data with respect to counties
    if counties != None:
        agg_data = agg_data.loc[agg_data['county'].isin(counties)]
    return agg_data