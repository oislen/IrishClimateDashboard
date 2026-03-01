import pickle
import logging
import polars as pl
from beartype import beartype
from bokeh.models import Select, Div, Button, MultiSelect, ScrollBox
from bokeh.layouts import column, row

# import custom modules
import cons
from table.bokeh_table_data import bokeh_table_data
from table.bokeh_table_plot import table_height, table_width, bokeh_table_plot
from utilities.timeit import timeit
from utilities.widgets import widget_width, range_slider

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
    table_agg_level_selector = Select(title="Time Span:", value=cons.line_agg_level_default, options=cons.line_agg_level_options, width=widget_width, height=60, aspect_ratio=10)
    table_stat_selector = Select(title="Aggregate:", value=cons.stat_default, options=cons.stat_options, width=widget_width, height=60, aspect_ratio=10)

    # define range sliders for each weather column measure
    range_slider_list = [Div(text="Measures:")]
    for col in cons.col_options:
        range_slider_list.append(range_slider(col=col, data_dict=bokeh_table_data_dict['dataSource'].data))
    range_sliders_box = column(children=range_slider_list)
    range_sliders_scrollbox = ScrollBox(child=range_sliders_box, width=widget_width, height=200)
    range_slider_reset_button = Button(label="Reset All", width=widget_width)

    # define controls for county selection
    table_county_multiselect = MultiSelect(title="Counties:", value=cons.counties_values, options=cons.counties_options, width=widget_width, height=200)
    table_county_selectall_button = Button(label="Select All", width=widget_width)
    table_county_clearall_button = Button(label="Clear All", width=widget_width)

    table_agg_level_selector.on_change("value", callback_table_plot)
    table_stat_selector.on_change("value", callback_table_plot)
    table_county_multiselect.on_change("value", callback_table_plot)
    table_county_selectall_button.on_click(callback_multiselect_selectall)
    table_county_clearall_button.on_click(callback_multiselect_clearall)

    # structure dashboard table plot
    control_panel = column(children=[
        table_agg_level_selector,
        table_stat_selector,
        range_sliders_scrollbox, range_slider_reset_button,
        table_county_multiselect, table_county_selectall_button, table_county_clearall_button,
    ],
    height=table_height,
    width=widget_width
    )
    dashboard_table = row(control_panel, table_plot)

    return dashboard_table
