import os
import logging
import pickle
import pandas as pd
import geopandas as gpd
import cons
from beartype import beartype
from typing import Union

@beartype
def gen_stations_data(
    points_data_fpath:Union[str,None]=None
    ):
    """Generates gis points data for Met Eireann stations

    Parameters
    ----------
    points_data_fpath : str
        The file location to write the gis points data to disk, default is None

    Returns
    -------
    """
    logging.info("Loading master and stations data from disk ...")
    # load master and station data
    master_data = pd.read_feather(cons.master_data_fpath)
    stations_data = pd.read_csv(cons.stations_fpath)
    logging.info("Identifying master station ids ...")
    # extract out station ids from mater file
    master_station_ids = master_data["id"].unique()
    logging.info("Filtering corresponding station data ...")
    # filter master data with station ids
    master_stations = stations_data.loc[
        stations_data["station_id"].isin(master_station_ids), :
    ].copy()
    master_stations["county"] = master_stations["county"].str.title()
    master_stations["name"] = master_stations["name"].str.title()
    logging.info("Creating geopandas DataFrame of station data ...")
    # create gis data
    geo_master_stations = gpd.GeoDataFrame(
        data=master_stations,
        geometry=gpd.points_from_xy(master_stations.longitude, master_stations.latitude),
        crs="EPSG:4326",
        ).to_crs(epsg=2157)
    # if the output
    if points_data_fpath != None:
        if os.path.exists(points_data_fpath):
            logging.info("Writing gis stations data to disk as .pickle file ...")
            # pickle the gis stations data
            with open(points_data_fpath, "wb") as f:
                pickle.dump(geo_master_stations, f, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            raise ValueError(f"{points_data_fpath} does not exist")
