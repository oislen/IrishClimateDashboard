import cons
import os
import logging
import pickle
import numpy as np
import polars as pl
import pandas as pd
import geopandas as gpd
from beartype import beartype
from typing import Union

@beartype
def gen_map_data(
    rep_counties_fpath:str=cons.rep_counties_fpath,
    ni_counties_fpath:str=cons.ni_counties_fpath,
    master_data_fpath:str=cons.master_data_fpath,
    map_data_fpath:str=cons.map_data_fpath
    ):
    """Generates counties map data for the bokeh map dashboard

    Parameters
    ----------
    rep_counties_fpath : str
        The file path to the republic of ireland counties .shp file on disk, default is cons.rep_counties_fpath,
    ni_counties_fpath : str
        The file path to northern ireland counties .shp file on disk, default is cons.ni_counties_fpath
    master_data_fpath : str
        The file path to the pre-aggregated data on disk, default is cons.master_data_fpath
    map_data_fpath : str
        The file location to write the map data to disk, default is map_data_fpath

    Returns
    -------
    None
    """
    logging.info("Loading rep / ni counties shape files ...")
    # load in county shape files
    rep_counties = (gpd.read_file(rep_counties_fpath)[["ENGLISH", "geometry"]].rename(columns={"ENGLISH": "county"}).to_crs(epsg=2157))
    ni_counties = gpd.read_file(ni_counties_fpath)[["county", "geometry"]].to_crs(epsg=2157)
    logging.info("Loading pre-aggregated data dictionary ...")
    # load pre-aggregated data
    master_data = pl.read_parquet(master_data_fpath)
    logging.info("Concatenating counties geopandas dataframes ...")
    # concatenate county shape files
    counties = gpd.GeoDataFrame(pd.concat([rep_counties, ni_counties], ignore_index=True), crs="EPSG:2157")
    logging.info("Simplifying counties geometries ...")
    # simplify the granularity of the geometry column to speed up dashboard performance, tolerance is in the units of the crs (EPSG:2157 is in meters)
    counties["geometry"] = counties["geometry"].simplify(tolerance=1000)
    logging.info("Standardising county names to title case ...")
    # clean up county column
    counties["county"] = (counties["county"].str.title().str.replace(pat="County ", repl="", regex=False))
    logging.info("Ordering results by county name ...")
    # sort data by county
    counties = counties.sort_values(by="county")
    logging.info("Calculating county level aggregate statistics ...")
    # create a dictionary to contain map data
    tmp_agg_data_list = []
    # iterate over statistic and pre aggregated data
    for stat in cons.stat_options:
        logging.info(f"{stat} ...")
        tmp_master_data = master_data.clone()
        tmp_master_data = tmp_master_data.with_columns(pl.col("date").dt.year().cast(pl.String).alias("year"), pl.lit(stat).alias("stat"))
        # aggregate data to county level
        group_cols = ["county","year","stat"]
        agg_dict = [getattr(pl.col(col), stat)().replace({None:np.nan}).alias(col) for col in cons.col_options]
        tmp_agg_data = tmp_master_data.group_by(group_cols).agg(agg_dict)
        tmp_agg_data_list.append(tmp_agg_data)
    agg_data = pl.concat(items=tmp_agg_data_list,how="vertical").sort(by=["stat","county","year"])
    # join county level data to map data
    map_geodata = gpd.GeoDataFrame(
        data=pd.merge(left=counties, right=agg_data.to_pandas(), on="county", how="left"),
        crs="EPSG:2157",
        )
    if os.path.exists(os.path.dirname(map_data_fpath)):
        logging.info("Writing counties data to disk as .parquet file ...")
        # write the pre-aggregated data dictionary to disk
        map_geodata.to_parquet(path=map_data_fpath)
    else:
        raise FileNotFoundError(f"{os.path.dirname(map_data_fpath)} does not exist")
