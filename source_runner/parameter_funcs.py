"""Helper functions to load parameters"""
import pandas as pd

__all__ = ['load_parameter_file', 'group_parameters', 'get_initial_param_vals']

def load_parameter_file(fn):
    """Load parameters from file
    
    Parameters
    ==========
    * fn : str, filename and location to load
    
    Returns
    ==========
    * tuple[parameter settings]
    """
    # Importing parameters file
    parameters = pd.read_csv(fn)
    return parameters
# End load_parameter_file()


def group_parameters(parameters):
    """Group parameters for model analysis
    
    Parameters
    ==========
    * parameters : DataFrame, parameter values loaded from CSV
    
    Returns
    ==========
    * tuple[grouped parameters]
    """
    # group parameters according to locations in Source
    param_group = ['param_cmtgen',
                   'param_linkcons',
                   'param_node',
                   'param_linkrout',
                   'param_nodecons']

    # parameter names
    param_vename = ['param_cmtgen_list',
                       'param_linkcons_list',
                       'param_node_list',
                       'param_linkrout_list',
                       'param_nodecons_list']

    # param_by_location: store parameter information grouped by locations
    param_locations = ['v.model.catchment.generation', 
                       'v.model.link.constituents', 
                       'v.model.node', 
                       'v.model.link.routing', 
                       'v.model.node.constituents']

    name_loc_mapping = zip(param_group, param_locations)
    vename_loc_mapping = zip(param_vename, param_group)
    param_by_location = {name: parameters.loc[parameters['Veneer_location'] == loca, :] 
                        for name, loca in name_loc_mapping}
    
    # param_vename_dic: store parameter names grouped by locations
    param_vename_dic = {name: param_by_location[loca]['Veneer_name'].values for name, loca in vename_loc_mapping}
    
    param_names = parameters['Veneer_name'].values
    #param_count = len(param_names)
    #parameter types
    param_types = parameters.loc[:,'type']

    return param_names, param_vename_dic, param_vename, param_types
# End group_parameters()


def get_initial_param_vals(v, param_names, param_vename, param_vename_dic):
    """Get initial parameter values from Source
	
	Parameters
    ==========
    * v : Veneer-py object
	* param_names : list[str], of parameter names
	* param_vename : list[str], of veneer-py parameter names
	* param_vename_dic : dict, mapping of veneer-py parameter name to Source model
    
    Returns
    ==========
    * dict, of initial parameter values
	"""
    initial_params = {}
    for i in param_names:
        if i in param_vename_dic[param_vename[0]]:
            initial_params[i] = v.model.catchment.generation.get_param_values(i)
        if i in param_vename_dic[param_vename[1]]:
            initial_params[i] = v.model.link.constituents.get_param_values(i)
        if i in param_vename_dic[param_vename[2]]:
            initial_params[i] = v.model.node.get_param_values(i)
        if i in param_vename_dic[param_vename[3]]:
            initial_params[i] = v.model.link.routing.get_param_values(i)
        if i in param_vename_dic[param_vename[4]]:
            initial_params[i] = v.model.node.constituents.get_param_values(i, node_types=['StorageNodeModel'],aspect='model')
    
    return initial_params
# End get_initial_param_vals()