# load relevant libraries
import logging
from bokeh.io import curdoc
from bokeh.models import TabPanel, Tabs

# load custom modules
from line.bokeh_line_dash import bokeh_line_dash
from map.bokeh_map_dash import bokeh_map_dash
from table.bokeh_table_dash import bokeh_table_dash

def main():
    """Generates the bokeh dashboard

    Parameters
    ----------
    
    Returns
    -------
    bokeh.layouts.Tabs
        The interactive bokeh line dashboard
    """
    # initialise each dashboard
    dashboard_line = bokeh_line_dash()
    dashboard_map = bokeh_map_dash()
    dashboard_table = bokeh_table_dash()
    # construct tab panels
    panel_line_tab = TabPanel(child=dashboard_line, title='Time Series', name="panel_line_tab")
    panel_map_tab = TabPanel(child=dashboard_map, title='GIS Map', name="panel_map_tab")
    panel_table_tab = TabPanel(child=dashboard_table, title='Data Table', name="panel_table_tab")
    # return combined tabs
    return Tabs(tabs=[panel_line_tab, panel_map_tab, panel_table_tab], name="layout")

# set up logging
lgr = logging.getLogger()
lgr.setLevel(logging.INFO)
# clear the document to remove old references
curdoc().clear()
# create dashboard
layout = main()
# deploy bokeh server and add dashboard layout
curdoc().add_root(layout)
