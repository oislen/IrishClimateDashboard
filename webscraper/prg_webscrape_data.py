import logging
import cons
import time
from beartype import beartype
from utilities.commandline_interface import commandline_interface
from utilities.gen_met_data import gen_met_data
from utilities.gen_clean_data import gen_clean_data
from utilities.gen_master_data import gen_master_data
from utilities.gen_map_data import gen_map_data
from utilities.gen_points_data import gen_points_data

@beartype
def webscrape_data(
    run_met_data:bool, 
    run_clean_data:bool,
    run_master_data:bool, 
    run_map_data:bool,
    run_points_data:bool
    ):
    """Webscrape and process met data into dashboard files

    Parameters
    ----------
    run_met_data : bool
        Retrieves / web scrapes the historical met data
    run_clean_data : bool
        Cleans and processes the scraped met data
    run_master_data : bool
        Generates the master data file from the retrieved / web scraped met data files
    run_map_data : bool
        Generates the map gis file for the bokeh dashboard app
    run_points_data : bool
        Generates the stations gis file for the bokeh dashboard app

    Returns
    -------
    """
    # start timer
    t0 = time.time()

    if run_met_data:
        logging.info('~~~~~ Retrieving data for met stations ...')
        # run webscraper
        gen_met_data(
            stations_fpath=cons.stations_fpath, 
            filter_open=True, 
            topn_stations=5, 
            scraped_data_dir=cons.scraped_data_dir, data_level="dly"
            )
    
    if run_clean_data:
        logging.info('~~~~~ Cleaning met stations data ...')
        # run data cleaning
        gen_clean_data(
            scraped_data_dir=cons.scraped_data_dir,
            cleaned_data_dir=cons.cleaned_data_dir,
            stations_fpath=cons.stations_fpath,
            store_on_s3=False
            )
    
    if run_master_data:
        logging.info('~~~~~ Generating master data file ...')
        # generate master data file
        gen_master_data(
            cleaned_data_dir=cons.cleaned_data_dir, 
            master_data_fpath=cons.master_data_fpath
            )

    if run_map_data:
        logging.info('~~~~~ Generating geospatial map data file ...')
        # generate counties data
        gen_map_data(
            rep_counties_fpath=cons.rep_counties_fpath, 
            ni_counties_fpath=cons.ni_counties_fpath, 
            master_data_fpath=cons.master_data_fpath, 
            map_data_fpath=cons.map_data_fpath
            )

    if run_points_data:
        logging.info('~~~~~ Generating geospatial points data file ...')
        # generate weather station points data
        gen_points_data(
            master_data_fpath=cons.master_data_fpath, 
            stations_fpath=cons.stations_fpath, 
            points_data_fpath=cons.points_data_fpath
            )
        
    # end timer and log result
    t1 = time.time()
    tres = t1 - t0
    eres = round(tres, 2)
    logging.info(f'Total Execution Time: {eres} seconds')

# if running as main programme
if __name__ == '__main__':
    # set up logging
    lgr = logging.getLogger()
    lgr.setLevel(logging.INFO)

    # handle input parameters
    input_params_dict = commandline_interface()

    # call webscrape data
    webscrape_data(
        run_met_data=input_params_dict['run_met_data'], 
        run_clean_data=input_params_dict['run_clean_data'], 
        run_master_data=input_params_dict['run_master_data'], 
        run_map_data=input_params_dict['run_map_data'],
        run_points_data=input_params_dict['run_points_data']
    )