import pickle
import logging
import polars as pl
from functools import partial
from beartype import beartype
from bokeh.models import Select, Div, Button, MultiSelect, ScrollBox
from bokeh.layouts import column, row

# import custom modules
import cons
from table.bokeh_table_data import bokeh_table_data
from table.bokeh_table_plot import table_height, table_width, bokeh_table_plot
from utilities.timeit import timeit
from utilities.widgets import widget_width, range_slider

is_updating = False

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
    def callback_table_plot(attr, old, new, source_widget=None):
        global is_updating
        if is_updating:
            return
        logging.info("Callback table plot begin")
        # extract new selector value
        agg_level = table_agg_level_selector.value
        stat = table_stat_selector.value
        range_sliders_box = next(dashboard_table.select({"name":"range_sliders_box"}), None)
        # generate country selection
        selection = list()
        for i in table_county_multiselect.value:
            selection.append(cons.counties[int(i)])
        # generate measures filter
        measure_filters_list = []
        if source_widget in ("col_range_slider"):
            for range_slider in range_sliders_box.children[1:]:
                filter_expression = (pl.col(range_slider.title) >= range_slider.value[0]) & (pl.col(range_slider.title) <= range_slider.value[1])
                measure_filters_list.append(filter_expression)
        # update bokeh data
        bokeh_table_data_params = {"master_data":master_data, "stat":stat, "agg_level":agg_level, "counties":selection, "filter_expression_list":measure_filters_list}
        bokeh_table_data_dict = timeit(func=bokeh_table_data, params=bokeh_table_data_params)
        # dynamically update range slider min max values based on aggregation from calculated reference file
        if source_widget in ("agg_level_selector", "stat_selector"):
            try:
                is_updating = True
                for range_slider in range_sliders_box.children[1:]:
                    col_min_max = bokeh_table_data_dict['min_max_ref_dict'][range_slider.title]
                    range_slider.start, range_slider.end, range_slider.value = col_min_max[0], col_min_max[1], tuple(col_min_max)
            finally:
                is_updating = False
        # update bokeh plot
        bokeh_table_plot_params = {"bokeh_data_dict":bokeh_table_data_dict}
        table_plot = timeit(func=bokeh_table_plot, params=bokeh_table_plot_params)
        # reassign bokeh plot to bokeh dashboard
        dashboard_table.children[1] = table_plot
        logging.info("Callback table plot end")

    def callback_range_slider_reset_all():
        callback_table_plot(attr='', old='', new='', source_widget='agg_level_selector')

    def callback_multiselect_select_all():
        table_county_multiselect.value = cons.counties_values

    def callback_multiselect_clear_all():
        table_county_multiselect.value = []

    # define select aggregate level
    table_agg_level_selector = Select(title="Time Span:", value=cons.line_agg_level_default, options=cons.line_agg_level_options, width=widget_width, height=60, aspect_ratio=10, name="agg_level_selector")
    table_agg_level_selector.on_change("value", partial(callback_table_plot, source_widget="agg_level_selector"))
    # define select statistic value
    table_stat_selector = Select(title="Aggregate:", value=cons.stat_default, options=cons.stat_options, width=widget_width, height=60, aspect_ratio=10, name="stat_selector")
    table_stat_selector.on_change("value", partial(callback_table_plot, source_widget="stat_selector"))
    # define range sliders for each weather column measure
    range_slider_list = [Div(text="Measures:")]
    for col in cons.col_options:
        col_range_slider = range_slider(col=col, data_dict=bokeh_table_data_dict['min_max_ref_dict'])
        col_range_slider.on_change("value_throttled", partial(callback_table_plot, source_widget="col_range_slider"))
        range_slider_list.append(col_range_slider)
    range_sliders_box = column(children=range_slider_list, name="range_sliders_box")
    range_sliders_scroll_box = ScrollBox(child=range_sliders_box, width=widget_width, height=200)
    range_slider_reset_button = Button(label="Reset All", width=widget_width)
    range_slider_reset_button.on_click(callback_range_slider_reset_all)
    # define multi-select for counties
    table_county_multiselect = MultiSelect(title="Counties:", value=cons.counties_values, options=cons.counties_options, width=widget_width, height=200, name="counties_multiselect")
    table_county_multiselect.on_change("value", partial(callback_table_plot, source_widget="counties_multiselect"))
    # define select all counties button
    table_county_select_all_button = Button(label="Select All", width=widget_width, name="counties_select_all")
    table_county_select_all_button.on_click(callback_multiselect_select_all)
    # define clear all counties button
    table_county_clear_all_button = Button(label="Clear All", width=widget_width, name="counties_clear_all")
    table_county_clear_all_button.on_click(callback_multiselect_clear_all)

    # structure dashboard table plot
    control_panel = column(children=[
        table_agg_level_selector,
        table_stat_selector,
        range_sliders_scroll_box, range_slider_reset_button,
        table_county_multiselect, table_county_select_all_button, table_county_clear_all_button,
    ],
    height=table_height,
    width=widget_width
    )
    dashboard_table = row(children=[control_panel, table_plot], name="dashboard_table")

    return dashboard_table
