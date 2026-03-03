from beartype import beartype
import cons
from bokeh.models import DataTable, Div
from bokeh.layouts import column

table_height = cons.FIG_SETTING['height']
table_width=820

@beartype
def bokeh_table_plot(bokeh_data_dict:dict):
    """
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
    data_table = column(children=[data_table, n_rows], name="table_plot")
    return data_table