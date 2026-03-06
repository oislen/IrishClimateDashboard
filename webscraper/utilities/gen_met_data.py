import logging
import os
import pandas as pd
import urllib.request
from beartype import beartype
from typing import Union
import cons

@beartype
def url_retrieve(
    stationid:int, 
    scraped_data_dir:str=cons.scraped_data_dir, 
    data_level:str="dly"
    ):
    """Retrieves met data for a given station id 

    Parameters
    ----------
    stationid : int
        The station id to retrieve data for
    scraped_data_dir : str
        The file directory to write the scraped met data to, default is cons.scraped_data_dir
    data_level : str
        The time level of the met data to scrape, default is "dly"

    Returns
    -------
    urllib.request.urlretrieve, Exception
        A retrieval response
    """
    data_fname = f"{data_level}{stationid}.csv"
    data_url = f"http://cli.fusio.net/cli/climate_data/webdata/{data_fname}"
    download_data_fpath = os.path.join(scraped_data_dir, data_fname)
    try:
        resp = urllib.request.urlretrieve(data_url, download_data_fpath)
    except Exception as e:
        resp = e
    return resp

@beartype
def gen_met_data(
    stations_fpath:str=cons.stations_fpath,
    filter_open:bool=True,
    topn_stations:Union[int, None]=None,
    scraped_data_dir:str=cons.scraped_data_dir,
    data_level:str="dly"
    ):
    """Webscrapes the met data for all station ids in a given stations dataframe

    Parameters
    ----------
    stations_fpath : str
        The file path to the met eireann stations reference data, default is cons.stations_fpath
    filter_open : bool
        Whether to only filter for only open weather stations in the met eireann stations reference data, default is True
    topn_stations : int
        The number of stations to sample from the head of the met eireann stations reference data, default is None
    scraped_data_dir : str
        The file directory to write the scraped met data to, default is cons.scraped_data_dir
    data_level : str
        The time level of the met data to scrape, default is "dly"


    Returns
    -------
    """
    # load stations data
    stations = pd.read_csv(stations_fpath)
    if filter_open:
        # only consider open stations for now
        open_stations_filter = stations['close_year'].isnull()
        stations = stations.loc[open_stations_filter, :].reset_index(drop=True)
    if topn_stations is not None:
        stations = stations.head(topn_stations)
    # iterate over each station and pull daily level data using using stationid
    responses =[]
    for idx, row in stations.iterrows():
        logging.info(f"{idx} {row['county']} {row['station_id']} {row['name']}")
        response = url_retrieve(stationid=row['station_id'], scraped_data_dir=scraped_data_dir, data_level=data_level)
        logging.info(response)
        responses.append(response)
    