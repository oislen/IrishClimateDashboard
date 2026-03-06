# import relevant libraries
from beartype import beartype
import polars as pl
import numpy as np
import datetime

# import custom modules
import cons
from bokeh.models import ColumnDataSource
from utilities.time_data import time_data

@beartype
def bokeh_line_data(
    master_data:pl.LazyFrame,
    stat:str,
    agg_level:str,
    counties:list
    ) -> dict:
    """Generates the data used in the bokeh line plot.

    Parameters
    ----------
    master_data : pl.LazyFrame
        The master data to be transformed into aggregated bokeh data objects for visualisation
    stat : str
        The statistic being visualised on the dashboard.
    agg_level : str
        The aggregate level being visualised on the dashboard.
    counties : list
        The counties being visualised on the dashboard.

    Returns
    -------
    dict
        The aggregated bokeh data objects to visualise
    """
    # filter for desired statistic and the previous full calendar year
    max_datetime = master_data.select(pl.col("date").max().dt.strftime("%Y").str.to_datetime("%Y") - pl.duration(days=1)).collect().to_series()[0]
    data = master_data.filter((pl.col("date") <= max_datetime))
    # determine time span from date aggregate level
    date_strftime = cons.date_strftime_dict[agg_level]
    # generate time data aggregated by year
    agg_dict = [getattr(pl.col(col).drop_nulls(), stat)().replace({None:np.nan}).alias(col) for col in cons.col_options]
    agg_data = time_data(
        data=data,
        agg_dict=agg_dict,
        counties=counties,
        strftime=date_strftime,
    )
    # create filtered column data source views
    dataview_dict = {}
    for county in counties:
        dataview = ColumnDataSource(agg_data.filter(pl.col('county') == county).collect().to_dict(as_series=False))
        cfg_dict = {"dataview":dataview, "color":cons.county_line_colors[county]}
        dataview_dict[county] = cfg_dict
    # update results dictionary
    bokeh_line_data_dict = {"agg_data":agg_data, "dataview_dict":dataview_dict}
    return bokeh_line_data_dict
