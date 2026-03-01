from bokeh.models import RangeSlider
from beartype import beartype
import numpy as np
import pandas as pd

widget_width = 140
range_slider_widget_width = 100

@beartype
def range_slider(
    col:str,
    data_dict:dict,
    step=1,
    height=40,
    width=range_slider_widget_width,
    sizing_mode="fixed"
    ) -> RangeSlider:
    """
    """
    data_series = pd.Series(data_dict[col]).replace({np.nan:None})
    disabled = data_series.isnull().all()
    min_value = data_series.min() if not disabled else 0
    max_value = data_series.max()if not disabled else 0
    col_range_slider = RangeSlider(
        start=min_value,
        end=max_value,
        value=(min_value, max_value),
        step=step,
        title=col,
        width=width,
        height=height,
        sizing_mode=sizing_mode,
        disabled=disabled,
        visible=~disabled
        )
    return col_range_slider