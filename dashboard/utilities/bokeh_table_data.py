from beartype import beartype
import polars as pl
from bokeh.models import ColumnDataSource, TableColumn
from utilities.bokeh_line_data import bokeh_line_data

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
    agg_data = bokeh_line_data_dict['agg_data']
    # possibly re-use or re-purpose bokeh line data function
    columns = agg_data.columns
    dataSource = ColumnDataSource(agg_data.to_dict(as_series=False))
    dataColumns = [TableColumn(field=col, title=col, width=15+int(len(col)*5)) for col in columns]
    bokeh_table_data_dict = {"dataSource":dataSource, "dataColumns":dataColumns}
    return bokeh_table_data_dict