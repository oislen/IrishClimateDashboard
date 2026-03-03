# load relevant libraries
import os
import sys
import re
import json

root_dir_re_match = re.findall(string=os.getcwd(), pattern="^.+IrishClimateDashboard")
root_dir = root_dir_re_match[0] if len(root_dir_re_match) > 0 else os.path.join(".", "IrishClimateDashboard")
sys.path.append(root_dir)
# set directories
data_dir = os.path.join(root_dir, 'data')
dashboard_dir = os.path.join(root_dir, 'dashboard')
# set data files
master_data_fpath = os.path.join(data_dir, 'master.parquet')
gis_dir = os.path.join(data_dir, "gis")
preaggregate_data_fpath = os.path.join(data_dir, "preaggregate_data.parquet")
bokeh_line_data_fpath = os.path.join(data_dir, "bokeh_line_data.pickle")
bokeh_map_data_fpath = os.path.join(data_dir, "bokeh_map_data.pickle")
map_data_fpath = os.path.join(gis_dir, "map_data.parquet")
points_data_fpath = os.path.join(gis_dir, "points_data.parquet")
# set bokeh reference dashboard file paths
bokeh_dashboard_ref_dir = os.path.join(dashboard_dir, "ref")
county_line_colors_fpath = os.path.join(bokeh_dashboard_ref_dir, "county_line_colors.json")
map_settings_fpath = os.path.join(bokeh_dashboard_ref_dir, "map_settings.json")
figure_settings_fpath = os.path.join(bokeh_dashboard_ref_dir, "fig_settings.json")
unittest_normal_dists_fpath = os.path.join(bokeh_dashboard_ref_dir, "unittest_normal_dists.json")
col_options_fpath = os.path.join(bokeh_dashboard_ref_dir, "col_options.json")
stat_options_fpath = os.path.join(bokeh_dashboard_ref_dir, "stat_options.json")
agg_level_strftime_fpath = os.path.join(bokeh_dashboard_ref_dir, "agg_level_strftime.json")
measurement_units_fpath = os.path.join(bokeh_dashboard_ref_dir, "measurement_units.json")

# seaborn plot settings
sns_fig_settings = {'figure.figsize':(7, 7), "lines.linewidth": 0.7}

# set whether to load in pickle data for bokeh app or generate from master file
load_data_dict = True

# load bokeh reference data
with open(county_line_colors_fpath) as json_file: 
    county_line_colors = json.load(json_file)
with open(map_settings_fpath) as json_file: 
    MAP_SETTINGS = json.load(json_file)
with open(figure_settings_fpath) as json_file: 
    FIG_SETTING = json.load(json_file)
with open(col_options_fpath) as json_file: 
    col_options = json.load(json_file)
with open(stat_options_fpath) as json_file: 
    stat_options = json.load(json_file)
with open(agg_level_strftime_fpath) as json_file: 
    date_strftime_dict = json.load(json_file)
with open(measurement_units_fpath, encoding='utf-8') as json_file:
    measurement_units_dict = json.load(json_file)

# bokeh line selector settings
counties = list(county_line_colors.keys())
line_colors = list(county_line_colors.values())
counties_values = [str(i) for i in range(len(counties))]
counties_options = [(str(i), c) for i, c in enumerate(counties)]
line_agg_level_options = list(date_strftime_dict.keys())
line_agg_level_default = line_agg_level_options[0]
col_default = col_options[0]
stat_default = stat_options[0]
show_stations_default = []
linedash_year_start = "2010"
linedash_year_month_start = "2010-01"
linedash_year_weekno_start = "2010-01"
linedash_month_timespan = ["01", "12"]
linedash_weekno_timespan = ["01", "52"]

# bokeh server execution commands
bat_execBokehApp = "START /MIN CMD.EXE /C exeBokehApp.bat"
sh_execBokehApp = "bash exeBokehApp.sh &"

# unittest constants
unittest_n_dates = 3
unittest_country_station_map ={'dublin':['dublin airport', 'casement'], 'cork':['ucc']}
unittest_start_date = '2020-01-01'
with open(unittest_normal_dists_fpath) as json_file: 
    unittest_normal_dists = json.load(json_file)
