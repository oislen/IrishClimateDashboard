import time
import numpy as np
import logging


def timeit(func, params, itr=1, digits=3):
    """Wrapper function for timing the execution time of a given function. Runs multiple iterations and returns average execution time.

    Parameters
    ----------
    func : function
        The function to time
    params : dict
        The input parameters to be passed into the function
    itr : int
        The number of iterations to run
    digits : int
        The number of decimal places to round the average recorded time to

    Returns
    -------
    function output
        The function output from the final iteration
    """
    t_results = []
    for i in range(itr):
        t0 = time.time()
        res = func(**params)
        t1 = time.time()
        t_results.append(t1 - t0)
    result = round(np.mean(t_results), digits)
    logging_message=f"Execution Time for {func.__name__}: {result} seconds"
    if itr>1:
        logging_message=f"Mean {logging_message}"
    logging.info(logging_message)
    return res
