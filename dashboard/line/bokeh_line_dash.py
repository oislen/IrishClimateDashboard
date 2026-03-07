import pickle
import logging
import polars as pl
from beartype import beartype
from bokeh.models import Select, Div, Button, MultiSelect
from bokeh.layouts import column, row

# import custom modules
import cons
from line.bokeh_line_data import bokeh_line_data
from line.bokeh_line_plot import bokeh_line_plot
from utilities.timeit import timeit

@beartype
def bokeh_line_dash():
    """Generates the bokeh line dashboard

    Parameters
    ----------
    
    Returns
    -------
    bokeh.layouts.row
        The interactive bokeh line dashboard
    """
    logging.info("Initialise line plot begin")
    master_data = pl.scan_parquet(cons.master_data_fpath)
    # generate bokeh data for line plot
    bokeh_line_data_params = {"master_data":master_data, "stat":cons.stat_default, "agg_level":cons.line_agg_level_default, "counties":cons.counties}
    bokeh_line_data_dict = timeit(func=bokeh_line_data, params=bokeh_line_data_params)
    # create bokeh plot
    bokeh_line_plot_params = {"bokeh_data_dict":bokeh_line_data_dict, "col":cons.col_default, "stat":cons.stat_default, "agg_level":cons.line_agg_level_default, "selection":cons.counties}
    line_plot = timeit(func=bokeh_line_plot, params=bokeh_line_plot_params)
    logging.info("Initialise line plot end")

    # create call back function for bokeh dashboard interaction
    def callback_line_plot(attr, old, new):
        logging.info("Callback line plot begin")
        # extract new selector value
        agg_level = line_agg_level_selector.value
        col = line_col_selector.value
        stat = line_stat_selector.value
        selection = list()
        for i in line_county_multiselect.value:
            selection.append(cons.counties[int(i)])
        # update bokeh data
        bokeh_line_data_params = {"master_data":master_data, "stat":stat, "agg_level":agg_level, "counties":selection}
        bokeh_line_data_dict = timeit(func=bokeh_line_data, params=bokeh_line_data_params)
        # update bokeh plot
        bokeh_line_plot_params = {"bokeh_data_dict":bokeh_line_data_dict, "col":col, "stat":stat, "agg_level":agg_level, "selection":selection}
        dashboard_line.children[1] = timeit(func=bokeh_line_plot, params=bokeh_line_plot_params)
        logging.info("Callback line plot end")

    def callback_multiselect_selectall():
        line_county_multiselect.value = cons.counties_values

    def callback_multiselect_clearall():
        line_county_multiselect.value = []

    # set up selectors for bokeh line plot
    line_agg_level_selector = Select(
        title="Time Span:",
        value=cons.line_agg_level_default,
        options=cons.line_agg_level_options,
        width=130,
        height=60,
    )
    line_col_selector = Select(
        title="Climate Measure:",
        value=cons.col_default,
        options=cons.col_options,
        width=130,
        height=60,
        aspect_ratio=10,
    )
    line_stat_selector = Select(
        title="Aggregate:",
        value=cons.stat_default,
        options=cons.stat_options,
        width=130,
        height=60,
        aspect_ratio=10,
    )
    line_county_multiselect = MultiSelect(
        title="Counties:",
        value=cons.counties_values, 
        options=cons.counties_options, 
        width=130, 
        height=260
    )
    line_county_selectall_button = Button(label="Select All", width=130)
    line_county_clearall_button = Button(label="Clear All", width=130)
    line_agg_level_selector.on_change("value", callback_line_plot)
    line_col_selector.on_change("value", callback_line_plot)
    line_stat_selector.on_change("value", callback_line_plot)
    line_county_multiselect.on_change("value", callback_line_plot)
    line_county_selectall_button.on_click(callback_multiselect_selectall)
    line_county_clearall_button.on_click(callback_multiselect_clearall)

    # structure dashboard line plot
    space_div = Div(width=30, height=30)
    widgets_line = column(
        line_agg_level_selector,
        line_col_selector,
        line_stat_selector,
        line_county_multiselect,
        line_county_selectall_button,
        line_county_clearall_button,
    )
    dashboard_line = row(widgets_line, line_plot)

    return dashboard_line
