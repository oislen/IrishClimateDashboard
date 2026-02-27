import cons
from bokeh.models import DataTable, Div
from bokeh.layouts import column

def bokeh_table_plot(bokeh_data_dict):
    """
    """
    data_table = DataTable(
        source=bokeh_data_dict['dataSource'],
        columns=bokeh_data_dict['dataColumns'],
        width=int(cons.FIG_SETTING['width']*1.25),
        height=cons.FIG_SETTING['height'],
        #stylesheets=[stylesheet],
        autosize_mode="none",
        #index_header=" ",
    )
    # add count of rows
    n_rows = Div(text=f"<b>Total Rows: {len(bokeh_data_dict['dataSource'].data[bokeh_data_dict['dataColumns'][0].field])}</b>", width=cons.FIG_SETTING['width'], height=25)
    data_table = column(data_table, n_rows)
    return data_table