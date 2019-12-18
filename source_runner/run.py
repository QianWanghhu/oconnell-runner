"""Helper function to run the model"""

from .parameter_funcs import group_parameters, get_initial_param_vals
from .retrieve import retrieve_outputs

from tqdm import tqdm

__all__ = ['run_model']


def run_model(v, filter_elements, samples, parameters, p_index, timeframe, f_dir, save_raw=False, batch_process=10):
    """Run the model.
    
    Parameters
   ==========
    * v : Veneer-py object
    * samples : np.array, transposed array of samples
    * parameters : DataFrame, of initial inputs, n * m matrix where  n is the number of samples and m is the number of parameters
    * p_index : parameter index of parameters in the parameter input used for Polynomial chaos 
    * timeframe : dict[str], {'begin': start_date, 'end': end_date}
    * f_dir : file directory for storing simulation outputs
    * save_raw : bool, default is false. If true, model results of each day will be saved
    * batch_process : process results in `n` batches, where `n` defaults to 10.
    """	
    M = len(samples)
    param_count = len(p_index)
    param_names, param_vename_dic, param_vename, param_types = group_parameters(parameters)
    
    # Get initial parameter values
    initial_params = get_initial_param_vals(v, param_names, param_vename, param_vename_dic)
    
    v.drop_all_runs()

    v_cmt_gen = v.model.catchment.generation
    v_link = v.model.link
    v_link_cnst = v_link.constituents
    v_routing = v_link.routing
    v_node = v.model.node
    v_node_cnst = v_node.constituents
    
    model_results = None
    for i in tqdm(range(M)):
    # for i in range(M):
        # update parameter values for all in the input file

        for j in range(param_count):
            name = parameters.Veneer_name[p_index[j]]
            param_new_factor = samples[i][j]
            param_value_ini = initial_params[name]
            if param_types[p_index[j]] == 0:
                param_value_new = [param_new_factor for value in initial_params[name]]
            else:
                param_value_new = [param_new_factor * value for value in initial_params[name]]
            #set parameter values
            if name in param_vename_dic[param_vename[0]]:
                assert v_cmt_gen.set_param_values(name, param_value_new, fromList = True)
            if name in  param_vename_dic[param_vename[1]]:
                assert v_link_cnst.set_param_values(name, param_value_new,fromList = True)
            if name in  param_vename_dic[param_vename[2]]:
                assert v_node.set_param_values(name, param_value_new,fromList = True)
            if name in  param_vename_dic[param_vename[3]]:
                assert v_routing.set_param_values(name, param_value_new,fromList = True)

        v.run_model(start=timeframe['begin'], end=timeframe['end'])

        # reset Source model to initial parameter values
        ini_param_val = initial_params[name]
        if name in param_vename_dic[param_vename[0]]:
            v_cmt_gen.set_param_values(name, ini_param_val, fromList=True)
        if name in param_vename_dic[param_vename[1]]:
            v_link_cnst.set_param_values(name, ini_param_val, fromList=True)
        if name in param_vename_dic[param_vename[2]]:
            v_node.set_param_values(name, ini_param_val, fromList=True)
        if name in param_vename_dic[param_vename[3]]:
            v_routing.set_param_values(name, ini_param_val, fromList=True)
        if name in param_vename_dic[param_vename[4]]:
            v_node_cnst.set_param_values(name, ini_param_val, fromList=True, 
                                        node_types=['StorageNodeModel'],aspect='model')
        if (i+1) % batch_process == 0 or (i == M-1):
            model_results = retrieve_outputs(v, filter_elements, i, save_raw=save_raw, results=model_results, f_dir=f_dir)
            v.drop_all_runs()                                               
    # allruns = v.retrieve_runs()
    # retrieve_outputs(v, allruns, 'Outlet Node17', 'Constituents@Sediment - Fine@Downstream Flow Mass')
    return model_results
# End run_model()