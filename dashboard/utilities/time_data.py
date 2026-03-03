import datetime
import polars as pl
from typing import Union
from beartype import beartype

@beartype
def time_data(
    data:pl.DataFrame, 
    agg_dict:list, 
    time_span:Union[list, None]=None, 
    counties:Union[list, None]=None, 
    strftime:Union[str, None]=None
    ) -> pl.DataFrame:
    """Aggregates and filters Met Eireann for time series plot

    Parameters
    ----------
    data : polars.DataFrame
        The Met Eireann data to aggregate and filter
    agg_dict : list
        The column aggregation operations to perform on the Met Eireann data
    time_span : list
        A list, or iterable, containing the time series start date and end date as strings to filter for
    counties : list
        A list, or iterable, containing the counties to filter for
    strftime : string
        The strftime expression for converting the start date and end date strings from the time_span parameter into datetime objects for filtering

    Returns
    -------
    polars.DataFrame
        The aggregated and filtered Met Eireann time series data
    """
    agg_data = data.clone()
    # if filtering data with respect to counties
    if counties != None:
        agg_data = agg_data.filter(pl.col("county").is_in(counties))
    # if filtering date with respect to timespan
    if False:#time_span != None:
        time_span_lb = pl.col("date") >= datetime.datetime.strptime(time_span[0], strftime)
        time_span_ub = pl.col("date") <= datetime.datetime.strptime(time_span[1], strftime)
        agg_data = agg_data.filter(time_span_lb & time_span_ub)
    # format date attributes
    agg_data = agg_data.with_columns(pl.col("date").dt.to_string(format=strftime).alias("date_str"))
    # aggregate to county and date level
    group_cols = ["county", "date_str"]
    agg_data = agg_data.group_by(group_cols).agg(agg_dict+[pl.col("date").min()])
    # order results and generate plotting index
    agg_data = (agg_data
                .sort(by=["county","date"])
                .with_columns(
                    pl.struct("county","date").rank(method ="dense", descending=False).over(partition_by="county", order_by="date").alias("index") - 1
                    )
                )
    return agg_data
