import cons
import os
import logging
import pickle
import numpy as np
import polars as pl
from beartype import beartype
from typing import Union

@beartype
def gen_preagg_data(
    master_data_fpath:str=cons.master_data_fpath, 
    preaggregate_data_fpath:str=cons.preaggregate_data_fpath
    ):
    """Generates preaggregate data for bokeh dashboard app

    Parameters
    ----------
    master_data_fpath : None or pd.DataFrame
        The file location to write the master data to disk, default is cons.master_data_fpath
    preaggregate_data_fpath : str
        The file location to write the pre-aggregated data to disk, default is cons.preaggregate_data_fpath

    Returns
    -------
    """
    logging.info("Loading master data from disk ...")
    # load master data
    master_data = pl.read_parquet(master_data_fpath)
    logging.info("Performing initial data aggregation to year-month level ...")
    # preaggregate the data to year-month level for each available stat
    pre_agg_data_dict = {}
    strftime = cons.date_strftime_dict["year-month"]
    agg_data = master_data.clone()
    agg_data = agg_data.with_columns(date_str = pl.col("date").dt.to_string(strftime))
    agg_data = agg_data.with_columns(date = pl.col("date_str").str.to_datetime(format=strftime))
    group_cols = ["county", "date", "date_str"]
    logging.info("Performing final data aggregation to desired statistics ...")
    concat_items = []
    for stat in cons.stat_options:
        logging.info(f"{stat} ...")
        agg_dict = [getattr(pl.col(col), stat)().replace({None:np.nan}).alias(col) for col in cons.col_options]
        tmp_agg_data = agg_data.group_by(group_cols).agg(agg_dict).sort(by=group_cols).with_columns(pl.lit(stat).alias("stat"))
        concat_items.append(tmp_agg_data)
    # concatenate dataframes together
    concat_data = pl.concat(items=concat_items,how='vertical')
    if os.path.exists(preaggregate_data_fpath):
        logging.info("Writing pre-aggregated data to disk as .parquet file ...")
        # write the pre-aggregated data dictionary to disk
        concat_data.write_parquet(file=preaggregate_data_fpath)
    else:
        raise ValueError(f"{preaggregate_data_fpath} does not exist")
