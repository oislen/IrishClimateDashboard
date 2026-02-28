import cons
from colour import Color
from bokeh.models import LinearColorMapper, ColorBar, HoverTool, Label
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource
from beartype import beartype

@beartype
def bokeh_map_plot(
    bokeh_map_data_dict:dict, 
    show_stations:list
    ) -> figure:
    """Generates the data used in the bokeh map plot.

    Parameters
    ----------
    bokeh_map_data_dict : dict
        A dictionary of bokeh aggregated data objects to construct the interactive bokeh heatmap with
    show_stations : list
        Whether to toggle the Met Eireann station data overlay in the interactive bokeh heatmap

    Returns
    -------
    bokeh.plotting.figure
        The interactive bokeh heat map
    """
    # define a blue color palette
    lightblue = Color("lightblue")
    steelblue = Color("steelblue")
    palette = tuple([col.get_hex() for col in lightblue.range_to(steelblue, 100)])
    # instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colours.
    color_mapper = LinearColorMapper(
        palette=palette,
        low=bokeh_map_data_dict["color_mapper_low"],
        high=bokeh_map_data_dict["color_mapper_high"],
    )
    # create color bar.
    color_bar = ColorBar(
        color_mapper=color_mapper,
        label_standoff=8,
        width=500,
        height=25,
        border_line_color=None,
        location=(0, 0),
        orientation="horizontal",
        major_label_text_font_size="18px",
    )
    # create underlying figure object
    map_plot = figure(toolbar_location="below", output_backend="webgl", **cons.FIG_SETTING)
    map_plot.axis.visible = False
    map_plot.xgrid.grid_line_color = None
    map_plot.ygrid.grid_line_color = None
    #map_plot.x_range.min_interval = 1
    #map_plot.y_range.min_interval = 1
    #map_plot.x_range.max_interval = 70
    #map_plot.y_range.max_interval = 70
    map_plot.title.text_font_style = "bold"
    map_plot.title.text_font_size = "22px"

    if not bokeh_map_data_dict["miss_map_data"].empty:
        # add patches to render states with no aggregate data
        missgeosource = bokeh_map_data_dict['missgeosource']#[year]['miss_map_dataview']
        misscounties = map_plot.patches(
            xs="xs", ys="ys", source=missgeosource, fill_color="slategray", **cons.MAP_SETTINGS
        )
        map_plot.add_tools(
            HoverTool(
                renderers=[misscounties],
                tooltips=[("County Name", "@county"), ("County Value", "NA")],
                attachment="left",
                mode="mouse",
            )
        )
    
    if not bokeh_map_data_dict["nonmiss_map_data"].empty:
        # add patches to render states with aggregate data
        nonmissgeosource = bokeh_map_data_dict['nonmissgeosource']
        nonmisscounties = map_plot.patches(
            xs="xs",
            ys="ys",
            source=nonmissgeosource,
            fill_color={"field": bokeh_map_data_dict['col'], "transform": color_mapper},
            **cons.MAP_SETTINGS,
        )
        map_plot.add_tools(
            HoverTool(
                renderers=[nonmisscounties],
                tooltips=[("County Name", "@county"), ("County Value", f"@{bokeh_map_data_dict['col']}")],
                attachment="left",
                mode="mouse",
            )
        )
    
    # add points to render stations
    if show_stations == [0]:
        stationpoints = map_plot.scatter(
            x="x", y="y", source=bokeh_map_data_dict['pointgeosource'], color="red", size=8, alpha=0.3
        )
        map_plot.add_tools(
            HoverTool(
                renderers=[stationpoints],
                tooltips=[
                    ("Station Name", "@name"),
                    ("Station Id", "@station_id"),
                    ("Latitude", "@latitude"),
                    ("Longitude", "@longitude"),
                    ("Open Year", "@open_year"),
                ],
                attachment="right",
                mode="mouse",
            )
        )
    # set layout of color bar
    map_plot.add_layout(color_bar, "below")

    # add units of measurement
    mytext = Label(
        x=3,
        y=3,
        x_units='screen',
        y_units='screen',
        text=f"Units: {cons.measurement_units_dict[bokeh_map_data_dict['col']]}"
        )
    map_plot.add_layout(mytext)

    return map_plot
