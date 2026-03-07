from beartype import beartype
import polars as pl
import polars.selectors as cs
from bokeh.models import ColumnDataSource, TableColumn, NumberFormatter
from line.bokeh_line_data import bokeh_line_data
import cons

@beartype
def bokeh_table_data(
    master_data:pl.LazyFrame,
    stat:str,
    agg_level:str,
    counties:list,
    filter_expression_list:list=[]
    ) ->dict:
    """
    Generates the data used in the bokeh table plot.

    Parameters
    ----------
    master_data : pl.LazyFrame
        The master data to be transformed into aggregated bokeh data objects for visualisation
    stat : str
        The statistic being visualised on the dashboard.
    agg_level : str
        The aggregate level being visualised on the dashboard.
    counties : list
        The counties being visualised on the dashboard.
    filter_expression_list : list
        A list of polars filter expressions to apply to the aggregated data for the bokeh table plot
    
    Returns
    -------
    dict
        The aggregated bokeh data objects to visualise in the bokeh table plot
    """
    # run master data through line data function to aggregate up to desired level
    bokeh_line_data_dict = bokeh_line_data(master_data=master_data, stat=stat, agg_level=agg_level, counties=counties)
    # calculate reference file for range slider min max values
    min_max_ref_dict = bokeh_line_data_dict['agg_data'].select(cons.col_options).describe().filter(pl.col("statistic").is_in(["min","max"])).to_dict(as_series=False)
    agg_data = bokeh_line_data_dict['agg_data'].drop(["date", "index"]).rename({"date_str":agg_level}).with_columns(cs.numeric().round(2))
    # add measure filter logic here
    if filter_expression_list != []:
        agg_data = agg_data.filter(*filter_expression_list)
    # pass polars filter expression through function parameters and apply filter here post aggregation
    columns = agg_data.collect_schema().names()
    dataSource = ColumnDataSource(agg_data.collect().to_dict(as_series=False))
    number_formatter = NumberFormatter(format="0,0.00")
    # create data column objects
    dataColumns = []
    for col in columns:
        table_column = TableColumn(field=col, title=col, width=15+int(len(col)*10))
        if col in cons.col_options:
            table_column.formatter = number_formatter
        dataColumns.append(table_column)
    # package bokeh table data output as a dictionary
    bokeh_table_data_dict = {"min_max_ref_dict":min_max_ref_dict ,"dataSource":dataSource, "dataColumns":dataColumns}
    return bokeh_table_data_dict