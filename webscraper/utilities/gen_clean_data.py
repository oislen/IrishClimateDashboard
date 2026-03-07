import logging
import os
import re
import polars as pl
from beartype import beartype
import cons
from utilities.S3Client import S3Client

@beartype
def load_data(
    fpath:str,
    stations_data:pl.DataFrame
    ) -> pl.DataFrame:
    """Loads webscraped met data from disk

    Parameters
    ----------
    fpath : str
        The file path to load the webscraped met data from disk
    stations_data : polars.DataFrame
        The loaded met eireann stations dataset as a polars dataframe

    Returns
    -------
    pl.DataFrame
        The loaded webscraped met data
    """
    # extract stationid
    station_id = int(re.findall(pattern="dly([0-9]+)\.csv", string=os.path.basename(fpath))[0])
    # load file lines
    with open(fpath) as file:
        lines = [line.rstrip().lower() for line in file]
    # split into rows
    split_lines = [row.split(",") for row in lines]
    # generate dataframe
    n_cols = len(split_lines[-1])
    data_lines = [line for line in split_lines if len(line) == n_cols]
    raw_colnames = data_lines[0]
    clean_names = [col if col != "ind" else f"{col}_{raw_colnames[idx-1]}" for idx, col in enumerate(raw_colnames)]
    if data_lines[1:] != []:
        # convert rows to a dataframe
        dataframe = pl.DataFrame(data=data_lines[1:], schema=clean_names, orient="row")
        # rename columns to standard names
        cols_to_rename = {"maxt":"maxtp", "mint":"mintp", "g_rad":"glorad"}
        dataframe = dataframe.rename(mapping={old:new for old, new in cols_to_rename.items() if old in clean_names})
        # subset required rows and columns
        cols_to_sub = ["date"] + cons.col_options
        sub_cols = [col for col in dataframe.columns if col in cols_to_sub]
        row_filter = pl.col("date").str.contains("20(1[0-9]|2[0-9])")
        dataframe = dataframe.select(sub_cols).filter(row_filter)
        # convert numeric columns
        for col in cons.col_options:
            if col in dataframe.columns:
                dataframe = dataframe.with_columns(pl.col(col).str.strip_chars().alias(col))
                dataframe = dataframe.with_columns(pl.when(pl.col(col).is_in([""," "])).then(None).otherwise(pl.col(col)).cast(pl.Float64).alias(col))
            else:
                dataframe = dataframe.with_columns(pl.lit(None).alias(col))
        # join on met eireann stations data and process results
        sub_cols = [col for col in dataframe.columns if "ind" not in col]
        dataframe = (dataframe
                     .select(sub_cols)
                     .with_columns(station_id = station_id)
                     .join(other=stations_data, on="station_id", how="inner")
                     .rename(mapping={"station_id":"id"})
                     .with_columns(county=pl.col("county").str.to_titlecase(), date=pl.col("date").str.to_datetime(format="%d-%b-%Y"))
                     )
        # order columns and sort rows
        sub_cols = [col for col in dataframe.columns if col in cons.cleaned_data_cols]
        dataframe = dataframe.select(sub_cols).sort(by=["county","date"])
    else:
        dataframe = pl.DataFrame(schema=cons.cleaned_data_cols)
    return dataframe

@beartype
def gen_clean_data(
    scraped_data_dir:str=cons.scraped_data_dir,
    cleaned_data_dir:str=cons.cleaned_data_dir,
    stations_fpath:str=cons.stations_fpath,
    store_on_s3:bool=False
    ):
    """Generates the master data from the individual raw Met Eireann .xlsx files

    Parameters
    ----------
    scraped_data_dir : str
        The local directory to load the raw Met Eireann .csv files from, default is cons.scraped_data_dir
    cleaned_data_dir : str
        The local directory to write the cleaned Met Eireann .csv files to, default is cons.cleaned_data_dir
    stations_fpath : str
        The file path to load the reference station data from disk, default is cons.stations_fpath
    store_on_s3 : bool
        Whether to back up the clean data files on s3, default is False

    Returns
    -------
    """
     # load data files from file directory
    scraped_data_fpaths = [os.path.join(scraped_data_dir, fname) for fname in os.listdir(scraped_data_dir)]
    logging.info("Reading, cleaning and storing files ...")
    s3client = S3Client(sessionToken=cons.session_token_fpath)
    stations_data = pl.read_csv(stations_fpath).rename(mapping={"name":"station"})
    for fpath in scraped_data_fpaths:
        # extract basename
        scraped_fname, _ = os.path.splitext(os.path.basename(fpath))
        cleaned_fextension = ".parquet"
        # load data
        clean_data = load_data(fpath=fpath, stations_data=stations_data).to_pandas()
        clean_data_shape = clean_data.shape
        # only rewrite file with data
        if clean_data_shape[0] > 0:
            logging.info(f"Clean Data Shape: {clean_data_shape}")
            # write data to clean data directory
            cleaned_data_fpath = os.path.join(cleaned_data_dir, f"{scraped_fname}{cleaned_fextension}")
            logging.info(f"Writing cleaned data file {cleaned_data_fpath} to disk")
            clean_data.to_parquet(cleaned_data_fpath, index=False, schema=cons.cleaned_data_pa_schema)
            if store_on_s3:
                # store data on s3 back up repository
                s3client.store(
                    data=clean_data, 
                    bucket=cons.s3_bucket, 
                    key=f"{cons.s3_clean_directory}/{scraped_fname}{cleaned_fextension}", 
                    schema=cons.cleaned_data_pa_schema
                    )