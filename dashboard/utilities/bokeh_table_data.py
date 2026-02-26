import polars as pl
from bokeh.models import ColumnDataSource, TableColumn

def bokeh_table_data(master_data):
    """
    """
    # filter for desired statistic and the previous full calendar year
    max_datetime = master_data.select(pl.col("date").max().dt.strftime("%Y").str.to_datetime("%Y") - pl.duration(days=1)).to_series()[0]
    data = master_data.filter((pl.col("date") <= max_datetime))
    columns = master_data.columns
    dataSource = ColumnDataSource(data.to_dict(as_series=False))
    dataColumns = [TableColumn(field=col, title=col, width=15+int(len(col)*5)) for col in columns]
    bokeh_table_data_dict = {"dataSource":dataSource, "dataColumns":dataColumns}
    return bokeh_table_data_dict