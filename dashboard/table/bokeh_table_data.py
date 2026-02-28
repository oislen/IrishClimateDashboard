from beartype import beartype
import polars as pl
import polars.selectors as cs
from bokeh.models import ColumnDataSource, TableColumn, NumberFormatter
from line.bokeh_line_data import bokeh_line_data
import cons

@beartype
def bokeh_table_data(
    master_data:pl.DataFrame,
    stat:str,
    agg_level:str,
    counties:list):
    """
    """
    # run master data through line data function to aggregate up to desired level
    bokeh_line_data_dict = bokeh_line_data(master_data=master_data, stat=stat, agg_level=agg_level, counties=counties)
    agg_data = bokeh_line_data_dict['agg_data'].drop(["date", "index"]).rename({"date_str":agg_level}).with_columns(cs.numeric().round(2))
    # possibly re-use or re-purpose bokeh line data function
    columns = agg_data.columns
    dataSource = ColumnDataSource(agg_data.to_dict(as_series=False))
    number_formatter = NumberFormatter(format="0,0.00")
    # create data column objects
    dataColumns = []
    for col in columns:
        table_column = TableColumn(field=col, title=col, width=15+int(len(col)*10))
        if col in cons.col_options:
            table_column.formatter = number_formatter
        dataColumns.append(table_column)
    # package bokeh table data output as a dictionary
    bokeh_table_data_dict = {"dataSource":dataSource, "dataColumns":dataColumns}
    return bokeh_table_data_dict