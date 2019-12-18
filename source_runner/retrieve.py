"""Helper functions to retrieve model running results."""
import pandas as pd
import numpy as np
from tqdm.auto import tqdm
from datetime import datetime
__all__ = ['set_filter', 'retrieve_outputs', 'process_results']


def set_filter(veneer, node_of_interest, variable_of_interest):
    """ Basic settings for retrieving model results.
    
    Parameters
    ==========
    
    
    Returns
    ==========
    """
    filter_elements = {
                        'name_for_location': veneer.name_for_location,
                        'NetworkElement': node_of_interest, 
                        'RecordingVariable': variable_of_interest
                      }
    
    return filter_elements


def retrieve_outputs(v, filter_elements, run_ID, f_dir, save_raw=False, results=None):
    """Retrieve modelling results.
    
    Parameters
    ==========
    * v : Veneer-py object
    * run_ID : list, of allruns information
    * node_of_interest : string, name of the node to get results
    * variable_of_interest : string, name of variable to get results
    * fn_dir : file directory for storing simulation outputs

    """
    results = process_results(v, filter_elements, run_ID, f_dir, save_raw=save_raw, results=results)
    
    # save_run(v, filter_elements)
    
    # out_f_name = node_of_interest + '_' + variable_of_interest[0:4] + '_outputs_low.csv'
    return results
# End retrieve_outputs()

def process_results(v, filter_elements, run_ID, f_dir, save_quantile=[0.95, 0.99], save_raw=False, results=None):
    model_runs = v.retrieve_runs()
    num_runs = len(model_runs)
    quantiles = pd.DataFrame({k: np.zeros(num_runs) for k in save_quantile})
    means = pd.DataFrame({'mean': np.zeros(num_runs)})
    stds = pd.DataFrame({'std': np.zeros(num_runs)})
    
    name_for_location = filter_elements['name_for_location']
    node_of_interest = filter_elements['NetworkElement']
    variable_of_interest = filter_elements['RecordingVariable']
    
    v_elements = {k: val for k, val in filter_elements.items() if k is not 'name_for_location'}
    # ress = pd.DataFrame(index=[i for i in range(365)])
    # result_all_runs=np.array([datetime.strftime(x,'%Y-%m-%d') 
    #                           for x in list(pd.date_range(start='20100701', end='20110630'))]).reshape(365,1)
    # result_all_runs = None
    for index in range(num_runs):
        run_name = model_runs[index]['RunUrl']
        resultsall = v.retrieve_multiple_time_series(run=run_name, 
                                                    criteria=v_elements, 
                                                    name_fn=name_for_location)
        start_date = (resultsall.index[-1] - pd.DateOffset(years=2)) + pd.DateOffset(days=1)
        resultsall = resultsall.loc[start_date:]
        if resultsall.empty:
            raise ValueError("No results for Run ID: {}\n\
            Node of Interest: {}\n\
            Var of Interest: {}".format(run_name,
                                            node_of_interest,
                                            variable_of_interest))
            #store['run_%d'%index] = resultsall
            #result_ts.append(resultsall)
            
        run_quantiles = resultsall.quantile(save_quantile).transpose()
        run_means = resultsall.mean()
        run_stds = resultsall.std()
        quantiles.loc[index, save_quantile] = run_quantiles.loc[node_of_interest, :]
        means.loc[index] = run_means.loc[node_of_interest]
        stds.loc[index] = run_stds.loc[node_of_interest]
        resultsall_np =  resultsall.values
        
        try:
            result_all_runs = np.hstack((result_all_runs, resultsall_np))
        except (ValueError, UnboundLocalError) as e:
            timeframe = np.array(resultsall.index.date.tolist()).reshape(len(resultsall.index), 1)
            result_all_runs = np.hstack((timeframe, resultsall_np))
    if save_raw:
        fn_elements = [f_dir,
                        '{}'.format(run_ID+1),
                        '_low', 
                        node_of_interest, 
                        variable_of_interest[0:4]]
        np.savetxt(('{}'*len(fn_elements) +'.csv').format(*fn_elements),
                   result_all_runs, delimiter=',', newline='\n', 
                   header=", ".join(["Date"] + [str(i+1) for i in range(num_runs)]), fmt='%s')   
                
        #write different statistics (quantiles, means, stds) into different files
    statistic_all = pd.concat([means, stds, quantiles], axis=1)
    
    if results is None:
        results = statistic_all.to_records(index=False)
    else:
        results = np.hstack((results, statistic_all.to_records(index=False)))
    
    return results
# End process_results()
