import os
import logging
import pickle
import polars as pl
import pandas as pd
import geopandas as gpd
import cons
from beartype import beartype
from typing import Union

@beartype
def gen_points_data(
    master_data_fpath:str=cons.master_data_fpath,
    stations_fpath:str=cons.stations_fpath,
    points_data_fpath:str=cons.points_data_fpath
    ):
    """Generates gis points data for Met Eireann stations

    Parameters
    ----------
    master_data_fpath : str
        The file path to the master data on disk, default is cons.master_data_fpath
    stations_fpath : str
        The file path to the stations reference data on disk, default is cons.stations_fpath
    points_data_fpath : str
        The file location to write the gis points data to disk, default is cons.points_data_fpath

    Returns
    -------
    """
    logging.info("Loading master and stations data from disk ...")
    # load master and station data
    master_data = pl.read_parquet(master_data_fpath)
    stations_data = pl.read_csv(stations_fpath)
    logging.info("Identifying master station ids ...")
    # extract out station ids from mater file
    master_station_ids = master_data.select(pl.col("id")).unique().to_series()
    logging.info("Filtering corresponding station data ...")
    # filter master data with station ids
    master_stations = (stations_data
                       .filter(pl.col("station_id").is_in(master_station_ids))
                       .with_columns(pl.col("county").str.to_titlecase().alias("county"), pl.col("name").str.to_titlecase().alias("name"))
                       ).to_pandas()
    logging.info("Creating geopandas DataFrame of station data ...")
    # create gis data
    geo_master_stations = gpd.GeoDataFrame(
        data=master_stations,
        geometry=gpd.points_from_xy(master_stations.longitude, master_stations.latitude),
        crs="EPSG:4326",
        ).to_crs(epsg=2157)
    if os.path.exists(os.path.dirname(points_data_fpath)):
        logging.info("Writing gis stations data to disk as .parquet file ...")
        # write the gis stations data
        geo_master_stations.to_parquet(path=points_data_fpath)
    else:
        raise FileNotFoundError(f"{os.path.dirname(points_data_fpath)} does not exist")
