from bokeh.models import RangeSlider
from beartype import beartype
import pandas as pd

widget_width = 140
range_slider_widget_width = 100

@beartype
def range_slider(
    col:str,
    data_dict:dict,
    step:float=1,
    height:int=40,
    width:int=range_slider_widget_width,
    sizing_mode:str="fixed"
    ) -> RangeSlider:
    """
    """
    disabled = pd.isna(data_dict[col][0]) or pd.isna(data_dict[col][1])
    min_value = data_dict[col][0] if not disabled else 0
    max_value = data_dict[col][1] if not disabled else 0
    col_range_slider = RangeSlider(start=min_value, end=max_value, value=(min_value, max_value), step=step, title=col, width=width, height=height, sizing_mode=sizing_mode, disabled=disabled, visible=not disabled)
    return col_range_slider