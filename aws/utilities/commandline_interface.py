import argparse


def commandline_interface() -> dict:
    """A commandline interface for parsing input parameters with

    Parameters
    ----------
    None

    Returns
    -------
    dict
        A dictionary of key, value pairs where the values are parsed input parameters
    """
    # define argument parser object
    parser = argparse.ArgumentParser(description="Execute Random TeleCom Data Programme.")
    # add input arguments
    parser.add_argument("--launch", action=argparse.BooleanOptionalAction, dest="launch", default=False, help="Boolean, whether to launch a new ec2 instance",)
    parser.add_argument("--terminate", action=argparse.BooleanOptionalAction, dest="terminate", default=False, help="Boolean, whether to terminate all running ec2 instances",)
    # extract input arguments
    args = parser.parse_args()
    # create an output dictionary to hold the results
    parameter_names = ["launch", "terminate"]
    input_params_dict = {parameter_name: getattr(args, parameter_name) for parameter_name in parameter_names}
    return input_params_dict
