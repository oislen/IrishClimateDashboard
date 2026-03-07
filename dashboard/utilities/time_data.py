import datetime
import polars as pl
from typing import Union
from beartype import beartype

@beartype
def time_data(
    data:pl.LazyFrame, 
    agg_dict:list, 
    counties:Union[list, None]=None, 
    strftime:Union[str, None]=None
    ) -> pl.LazyFrame:
    """Aggregates and filters Met Eireann for time series plot

    Parameters
    ----------
    data : polars.LazyFrame
        The Met Eireann data to aggregate and filter
    agg_dict : list
        The column aggregation operations to perform on the Met Eireann data
    counties : list
        A list, or iterable, containing the counties to filter for
    strftime : string
        The strftime expression for converting the start date and end date strings from the time_span parameter into datetime objects for filtering

    Returns
    -------
    polars.LazyFrame
        The aggregated and filtered Met Eireann time series data
    """
    agg_data = data.clone()
    # if filtering data with respect to counties
    if counties != None:
        agg_data = agg_data.filter(pl.col("county").is_in(counties))
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
