from bokeh.models import RangeSlider
from beartype import beartype
import pandas as pd

widget_width = 140
range_slider_widget_width = 100

@beartype
def range_slider(
    col:str,
    data_dict:dict,
    step:float=0.01,
    height:int=40,
    width:int=range_slider_widget_width,
    sizing_mode:str="fixed"
    ) -> RangeSlider:
    """
    Generates a bokeh range slider widget for a given column with dynamic min max values and disabled state based on data availability.

    Parameters
    ----------
    col : str
        The column name for which to create the range slider
    data_dict : dict
        A dictionary containing the min and max values for the column to determine the range slider values and disabled state
    step : float, optional
        The step value for the range slider, by default 0.01
    height : int, optional
        The height of the range slider widget, by default 40
    width : int, optional
        The width of the range slider widget, by default range_slider_widget_width
    sizing_mode : str, optional
        The sizing mode for the range slider widget, by default "fixed"
    
    Returns
    -------
    RangeSlider
        The generated bokeh range slider widget
    """
    # determine whether to disable range slider
    disabled = pd.isna(data_dict[col][0]) or pd.isna(data_dict[col][1])
    # extract min and max values
    min_value = data_dict[col][0] if not disabled else 0
    max_value = data_dict[col][1] if not disabled else 0
    # create column range slider
    col_range_slider = RangeSlider(
        start=min_value,
        end=max_value,
        value=(min_value, max_value),
        step=step, title=col,
        width=width,
        height=height,
        sizing_mode=sizing_mode,
        disabled=disabled,
        visible=not disabled,
        name=f"{col}_range_slider"
        )
    return col_range_slider