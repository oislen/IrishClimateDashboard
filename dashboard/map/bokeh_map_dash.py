import pickle
import logging
import polars as pl
import geopandas as gpd
from bokeh.models import Select, Div, CheckboxButtonGroup
from bokeh.layouts import column, row
from beartype import beartype

import cons
from map.bokeh_map_data import bokeh_map_data
from map.bokeh_map_plot import bokeh_map_plot
from utilities.timeit import timeit

@beartype
def bokeh_map_dash():
    """Generates the bokeh map dashboard

    Parameters
    ----------

    Returns
    -------
    bokeh.layouts.row
        The interactive bokeh map dashboard
    """
    logging.info("Initialise map plot begin")
    master_data = pl.read_parquet(cons.master_data_fpath)
    map_data = gpd.read_parquet(cons.map_data_fpath)
    station_data = gpd.read_parquet(cons.points_data_fpath)
    # generate bokeh data for map plot
    max_datetime = master_data.select(pl.col("date").max().dt.strftime("%Y").str.to_datetime("%Y") - pl.duration(days=1)).to_series()[0]
    bokeh_map_data_params = {"map_data":map_data,"station_data":station_data,"col":cons.col_default,"stat":cons.stat_default,"year":str(max_datetime.year)}
    bokeh_map_data_dict = timeit(func=bokeh_map_data, params=bokeh_map_data_params)
    # create bokeh map plot
    bokeh_map_plot_params = {"bokeh_map_data_dict":bokeh_map_data_dict,"show_stations":cons.show_stations_default}
    map_plot = timeit(func=bokeh_map_plot, params=bokeh_map_plot_params)
    logging.info("Initialise map plot end")

    # create call back function for bokeh dashboard interaction
    def callback_map_plot(attr, old, new):
        logging.info("Callback map plot begin")
        # extract new selector value
        col = map_col_selector.value
        stat = map_stat_selector.value
        year = map_year_selector.value
        show_stations = toggle_stations.active
        # update bokeh data
        bokeh_map_data_params = {"map_data":map_data,"station_data":station_data,"col":col,"stat":stat,"year":year}
        bokeh_map_data_dict = timeit(func=bokeh_map_data, params=bokeh_map_data_params)
        # update bokeh plot
        bokeh_map_plot_params = {"bokeh_map_data_dict":bokeh_map_data_dict,"show_stations":show_stations}
        map_plot = timeit(func=bokeh_map_plot, params=bokeh_map_plot_params)
        # reassign bokeh plot to bokeh dashboard
        dashboard_map.children[1] = map_plot
        logging.info("Callback map plot end")

    # set up selectors for bokeh map plot
    map_col_selector = Select(
        title="Climate Measure:",
        value=cons.col_default,
        options=cons.col_options,
        width=120,
        height=60,
        aspect_ratio=10,
    )
    map_stat_selector = Select(
        title="Aggregate:",
        value=cons.stat_default,
        options=cons.stat_options,
        width=120,
        height=60,
        aspect_ratio=10,
    )
    map_year_selector = Select(
        title="Year:",
        value=str(max_datetime.year),
        options=[str(year) for year in range(int(cons.linedash_year_start), max_datetime.year+1)],
        width=120,
       height=60,
        aspect_ratio=10,
    )
    toggle_stations = CheckboxButtonGroup(
        labels=["Toggle Stations"], 
        active=[], 
        width=120,
        height=40
    )
    map_col_selector.on_change("value", callback_map_plot)
    map_stat_selector.on_change("value", callback_map_plot)
    toggle_stations.on_change("active", callback_map_plot)
    map_year_selector.on_change("value", callback_map_plot)

    # structure dashboard map plot
    widgets_map = column(toggle_stations, map_col_selector, map_stat_selector, map_year_selector)
    dashboard_map = row(widgets_map, map_plot)

    return dashboard_map
