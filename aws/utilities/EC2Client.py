import io
import boto3
import json
import logging
import pandas as pd
from typing import Union
from beartype import beartype


class EC2Client():
    
    @beartype
    def __init__(self, sessionToken:str):
        # load aws config
        with open(sessionToken, "r") as j:
            aws_config = json.loads(j.read())
        # connect to aws boto3
        self.session = boto3.Session(
            aws_access_key_id=aws_config["Credentials"]["AccessKeyId"],
            aws_secret_access_key=aws_config["Credentials"]["SecretAccessKey"],
            aws_session_token=aws_config["Credentials"]["SessionToken"],
            region_name="eu-west-1"
        )
        # generate boto3 s3 connection
        self.client = self.session.client("ec2")
    
    def create_launch_template(self, launch_template_config) -> dict:
        """Creates an EC2 launch template
        
        Parameters
        ----------
        launch_template_config : dict
            The launch template to create

        Returns
        -------
        dict
            The EC2 create launch template response
        """
        # create ec2 launch template
        response = self.client.create_launch_template(**launch_template_config)
        return response
    
    def delete_launch_template(self, LaunchTemplateName) -> dict:
        """Deletes an EC2 launch template
        
        Parameters
        ----------
        LaunchTemplateName : str
            The launch template name to delete

        Returns
        -------
        dict
            The EC2 delete launch template response
        """
        # delete ec2 launch template
        response = self.client.delete_launch_template(LaunchTemplateName=LaunchTemplateName)
        return response
    
    def create_fleet(self, create_fleet_config) -> dict:
        """Creates an EC2 fleet
        
        Parameters
        ----------
        create_fleet_config : dict
            The EC2 create fleet configs

        Returns
        -------
        dict
            The EC2 create fleet response
        """
        response = self.client.create_fleet(**create_fleet_config)
        return response
    
    def describe_fleets(self) -> dict:
        """Describes EC2 fleets
        
        Parameters
        ----------

        Returns
        -------
        dict
            The EC2 describe fleets response
        """
        response = self.client.describe_fleets()
        return response
    
    def delete_fleets(self, FleetIds=[], TerminateInstances=False) -> dict:
        """Delete an EC2 fleet
        
        Parameters
        ----------
        FleetIds : list
            The fleet ids to delete, default is []
        TerminateInstances : bool
            Whether to delete the fleets, default is False

        Returns
        -------
        dict
            The EC2 delete fleets EC2 response
        """
        response = self.client.delete_fleets(FleetIds=FleetIds, TerminateInstances=TerminateInstances)
        return response
    
    def run_instances(self, run_instances_config) -> dict:
        """Runs an EC2 instance
        
        Parameters
        ----------
        run_instances_config : dict
            The run instance configurations

        Returns
        -------
        dict
            The EC2 run instances response
        """
        response = self.client.run_instances(**run_instances_config)
        return response
    
    def stop_instances(self, InstanceIds=[]) -> dict:
        """Stops EC2 instances
        
        Parameters
        ----------
        InstanceIds : list
            The EC2 instance ids to stop, default is []

        Returns
        -------
        dict
            The EC2 stop instances response
        """
        response = self.client.stop_instances(InstanceIds=InstanceIds)
        return response
    
    def terminate_instances(self, InstanceIds=[]) -> dict:
        """Terminates EC2 instances
        
        Parameters
        ----------
        InstanceIds : list
            The EC2 instance ids to terminate, default is []

        Returns
        -------
        dict
            The EC2 terminate instances response
        """
        response = self.client.terminate_instances(InstanceIds=InstanceIds)
        return response
    
    def describe_instances(self, InstanceIds=[], Filters=[], MaxResults=20) -> dict:
        """Describe EC2 instances
        
        Parameters
        ----------
        InstanceIds : list
            The instance ids to describe, default is []
        Filters : list
            The filters to apply when describing instances, default is []
        MaxResults : int
            The maximum number of results to return

        Returns
        -------
        dict
            The EC2 describe instances response
        """
        response = self.client.describe_instances(InstanceIds=InstanceIds, Filters=Filters, MaxResults=MaxResults)
        return response
