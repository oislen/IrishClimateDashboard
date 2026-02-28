import pickle
import logging
import polars as pl
from beartype import beartype
from bokeh.models import Select, Div, Button, MultiSelect
from bokeh.layouts import column, row

# import custom modules
import cons
from table.bokeh_table_data import bokeh_table_data
from table.bokeh_table_plot import bokeh_table_plot
from utilities.timeit import timeit

@beartype
def bokeh_table_dash():
    """Generates the bokeh table dashboard

    Parameters
    ----------
    
    Returns
    -------
    bokeh.layouts.row
        The interactive bokeh table dashboard
    """
    logging.info("Initialise table plot begin")
    master_data = pl.read_parquet(cons.master_data_fpath)
    # generate bokeh data for table plot
    bokeh_table_data_params = {"master_data":master_data, "stat":cons.stat_default, "agg_level":cons.line_agg_level_default, "counties":cons.counties}
    bokeh_table_data_dict = timeit(func=bokeh_table_data, params=bokeh_table_data_params)
    # create bokeh plot
    bokeh_table_plot_params = {"bokeh_data_dict":bokeh_table_data_dict}
    table_plot = timeit(func=bokeh_table_plot, params=bokeh_table_plot_params)
    logging.info("Initialise table plot end")

    # create call back function for bokeh dashboard interaction
    def callback_table_plot(attr, old, new):
        logging.info("Callback table plot begin")
        # extract new selector value
        agg_level = table_agg_level_selector.value
        stat = table_stat_selector.value
        selection = list()
        for i in table_county_multiselect.value:
            selection.append(cons.counties[int(i)])
        # update bokeh data
        bokeh_table_data_params = {"master_data":master_data, "stat":stat, "agg_level":agg_level, "counties":selection}
        bokeh_table_data_dict = timeit(func=bokeh_table_data, params=bokeh_table_data_params)
        # update bokeh plot
        bokeh_table_plot_params = {"bokeh_data_dict":bokeh_table_data_dict}
        table_plot = timeit(func=bokeh_table_plot, params=bokeh_table_plot_params)
        # reassign bokeh plot to bokeh dashboard
        dashboard_table.children[1] = table_plot
        logging.info("Callback table plot end")

    def callback_multiselect_selectall():
        table_county_multiselect.value = cons.counties_values

    def callback_multiselect_clearall():
        table_county_multiselect.value = []

    # set up selectors for bokeh line plot
    table_agg_level_selector = Select(
        title="Time Span:",
        value=cons.line_agg_level_default,
        options=cons.line_agg_level_options,
        width=130,
        height=60,
        aspect_ratio=10,
    )
    table_stat_selector = Select(
        title="Aggregate:",
        value=cons.stat_default,
        options=cons.stat_options,
        width=130,
        height=60,
        aspect_ratio=10,
    )
    table_county_multiselect = MultiSelect(
        title="Counties:",
        value=cons.counties_values,
        options=cons.counties_options,
        width=130,
        height=260
    )
    table_county_selectall_button = Button(label="Select All", width=130)
    table_county_clearall_button = Button(label="Clear All", width=130)
    table_agg_level_selector.on_change("value", callback_table_plot)
    table_stat_selector.on_change("value", callback_table_plot)
    table_county_multiselect.on_change("value", callback_table_plot)
    table_county_selectall_button.on_click(callback_multiselect_selectall)
    table_county_clearall_button.on_click(callback_multiselect_clearall)

    # structure dashboard table plot
    space_div = Div(width=30, height=30)
    widgets_table = column(
        table_agg_level_selector,
        table_stat_selector,
        table_county_multiselect,
        table_county_selectall_button,
        table_county_clearall_button,
    )
    dashboard_table = row(widgets_table, table_plot)

    return dashboard_table
