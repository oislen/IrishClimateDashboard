import io
import os
import boto3
import json
import logging
import pandas as pd
import pyarrow as pa
from typing import Union
from beartype import beartype

class S3Client():
    
    @beartype
    def __init__(self, sessionToken:str):
        # load aws config
        with open(sessionToken, "r") as j:
            aws_config = json.loads(j.read())
        # connect to aws boto3
        self.session = boto3.Session(
            aws_access_key_id=aws_config['Credentials']["AccessKeyId"],
            aws_secret_access_key=aws_config['Credentials']["SecretAccessKey"],
            aws_session_token=aws_config['Credentials']["SessionToken"],
            region_name="eu-west-1"
        )
        # generate boto3 s3 connection
        self.client = self.session.client("s3")
    
    @beartype
    def store(
        self,
        data:pd.DataFrame,
        key:str,
        bucket:str,
        schema=None
        ):
        """Stores a raw Met Eireann data file on s3.
        
        Parameters
        ----------
        data : pd.DataFrame
            The raw Met Eireann data to store on s3
        key : str
            The s3 key to store the Met Eireann data files
        bucket : str
            The s3 bucket storing the Met Eireann data files
        schema : pyarrow.Schema
            The pyarrow schema to use when writing parquet files to s3, default is None
        
        Returns
        -------
        None
        """
        _, fextension = os.path.splitext(os.path.basename(key))
        try:
            logging.info(f"Storing data to S3://{bucket}/{key}")
            if fextension==".csv":
                buf = io.StringIO()
                data.to_csv(buf, header=True, index=False)
                buf.seek(0)
                self.client.put_object(Bucket=bucket, Body=buf.getvalue().encode(), Key=key)
            elif fextension==".parquet":
                buf = io.BytesIO()
                data.to_parquet(buf, index=False, schema=schema)
                self.client.put_object(Bucket=bucket, Body=buf.getvalue(), Key=key)
            else:
                raise ValueError(f"Invalid file extensions {fextension}")
        except Exception as e:
            logging.error(str(e))
            
    @beartype
    def retrieve(
        self,
        key:str,
        bucket:str="irishclimateapp" 
        ):
        
        """Retrieves a raw Met Eireann data from AWS s3.
        
        Parameters
        ----------
        key : str
            The s3 key containing the Met Eireann data file
        bucket : str
            The s3 bucket containing the Met Eireann data file
        
        Returns
        -------
        
            The raw Met Eireann data
        """
        data = None
        try:
            logging.info(f"Retrieving data from S3://{bucket}/{key}")
            # load s3 objects into list
            obj = self.client.get_object(Bucket=bucket, Key=key)
            if key.endswith(".parquet"):
                # decode parquet files in body
                data = pd.read_parquet(io.BytesIO(obj["Body"].read()))
            elif key.endswith(".csv"):
                # decode csv files in body
                data = pd.read_csv(io.StringIO(obj["Body"].read().decode('utf-8')))
        except Exception as e:
            logging.error(str(e))
        return data
