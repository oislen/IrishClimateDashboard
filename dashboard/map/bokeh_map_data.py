import cons
import pickle
import pandas as pd
import geopandas as gpd
from bokeh.models import GeoJSONDataSource
from beartype import beartype

@beartype
def bokeh_map_data(
    map_data:gpd.GeoDataFrame, 
    station_data:gpd.GeoDataFrame,
    col:str,
    stat:str,
    year:str
    ):
    """Generates the data used in the bokeh map plot.

    Parameters
    ----------
    map_data : gpd.GeoDataFrame
        The aggregated geopandas data to be transformed into aggregated bokeh data objects for visualisation
    station_data : geopandas.DataFrame
        The geospatial Met Eireann station data to be transformed into a bokeh data object for visualisation
    col : str
        The climate measure category to plot in the interactive bokeh heatmap
    stat : str
        The aggregated statistic to plot in the interactive bokeh heatmap
    year : str
        The year of the data to filter for

    Returns
    -------
    dict
        The aggregated and station bokeh data objects to visualise
    """
    bokeh_map_data_dict = {}
    # filter for year
    data_filter = (map_data['year'].astype(str) == year) & (map_data['stat'].astype(str) == stat)
    missing_filter = (map_data['year'].isnull())
    sub_cols = ['county', 'geometry', 'year', 'stat', col]
    map_data_sub = map_data.loc[data_filter | missing_filter, sub_cols]
    # split data into missing and non-missing
    nonmiss_map_data = map_data_sub[map_data_sub.notnull().all(axis=1)]
    miss_map_data = map_data_sub[map_data_sub.isnull().any(axis=1)]
    # Input GeoJSON source that contains features for plotting
    missgeosource = GeoJSONDataSource(geojson=miss_map_data.to_json())
    nonmissgeosource = GeoJSONDataSource(geojson=nonmiss_map_data.to_json())
    pointgeosource = GeoJSONDataSource(geojson=station_data.to_json())
    # calculate colour bar range
    color_mapper_low = nonmiss_map_data[col].min()
    color_mapper_high = nonmiss_map_data[col].max()
    # assign data to temp dict
    bokeh_map_data_dict["col"] = col
    bokeh_map_data_dict["map_data"] = map_data
    bokeh_map_data_dict["nonmiss_map_data"] = nonmiss_map_data
    bokeh_map_data_dict["miss_map_data"] = miss_map_data
    bokeh_map_data_dict["missgeosource"] = missgeosource
    bokeh_map_data_dict["nonmissgeosource"] = nonmissgeosource
    bokeh_map_data_dict["pointgeosource"] = pointgeosource
    bokeh_map_data_dict["color_mapper_low"] = color_mapper_low
    bokeh_map_data_dict["color_mapper_high"] = color_mapper_high
    # pickle the bokeh map data dictionary to disk
    # with open(cons.bokeh_map_data_fpath, 'wb') as f:
    #    pickle.dump(bokeh_map_data_dict, f, protocol = pickle.HIGHEST_PROTOCOL)
    return bokeh_map_data_dict
