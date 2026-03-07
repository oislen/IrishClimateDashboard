from beartype import beartype
import cons
from bokeh.models import DataTable, Div
from bokeh.layouts import column

table_height = cons.FIG_SETTING['height']
table_width = 820

@beartype
def bokeh_table_plot(bokeh_data_dict:dict):
    """
    Generates the data used in the bokeh table plot.

    Parameters
    ----------
    bokeh_data_dict : dict
        A dictionary of bokeh aggregated data objects to construct the interactive bokeh table plot with
    
    Returns
    -------
    bokeh.layouts.column
        The interactive bokeh table plot
    """
    data_table = DataTable(
        source=bokeh_data_dict['dataSource'],
        columns=bokeh_data_dict['dataColumns'],
        width=table_width,
        height=table_height,
        #stylesheets=[stylesheet],
        autosize_mode="none",
        #index_header=" ",
    )
    # add count of rows
    n_rows = Div(text=f"<b>Total Rows: {len(bokeh_data_dict['dataSource'].data[bokeh_data_dict['dataColumns'][0].field])}</b>", width=table_width, height=25)
    table_layout = column(children=[data_table, n_rows], name="table_plot")
    return table_layout