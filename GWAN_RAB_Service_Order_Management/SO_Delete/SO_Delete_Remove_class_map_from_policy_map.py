import json
import time
from msa_sdk import constants
from msa_sdk.orchestration import Orchestration
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

dev_var = Variables()
context = Variables.task_call(dev_var)

####################################################
#                                                  #
#                FUNCTIONS                         #
#                                                  #
####################################################
'''
Get parameters values from class_map dictionary.

@param context:
    Service instance context.
@param policy_map:
    policy_map dictionary.
@param param:
    Parameter key name.
@param is_madatory:
    True or False is parameter is mandatory or not.
@return:
    Parameter value.
'''
def get_config_param_val(context, policy_map, param, is_madatory=True):
    value = ''
    if param in policy_map:
        value = policy_map.get(param)
        if is_madatory == True:
            if not value:
                ret = MSA_API.process_content(constants.FAILED, 'The required input "' + param + '" value is empty.', context, True)
                print(ret)
    elif is_madatory == True:
        ret = MSA_API.process_content(constants.FAILED, 'Miss required input parameter "' + param + '" key in the policy_map object.', context, True)
        print(ret)
        
    return value

'''
Retrieve process instance by service instance ID.

@param orch:
    Ochestration class object reference.
@param process_id:
    Baseline workflow process ID.
@param timeout:
    loop duration before to break.
@param interval:
    loop time interval.
@return:
    Response of the get process instance execution.
'''
def get_process_instance(orch, process_id, timeout=60, interval=5):
    response = {}
    global_timeout = time.time() + timeout
    while True:
        #get service instance execution status.
        orch.get_process_instance(process_id)
        response = json.loads(orch.content)
        status = response.get('status').get('status')
        #context.update(get_process_instance=status)
        if status != constants.RUNNING or time.time() > global_timeout:
            break
        time.sleep(interval)

    return response
####################################################
#                                                  #
#                MAIN CODE                         #
#                                                  #
####################################################

#Get device id (router) from context (e.g: UBI2455).
device_ref = context['device_external_ref']
device_id = device_ref[3:]

#Get StaticRouting dictionary object from context.
policy_map_dicts = context['policyMaps']

#Initiate orchestraction object.
ubiqube_id = context['UBIQUBEID']
orch = Orchestration(ubiqube_id)

#Static Routing Management WF service name constant variable.
SERVICE_NAME = 'Process/nttcw-gwan-rab-wf/Policy_Map_Management/Policy_Map_Management'
CREATE_PROCESS_NAME = 'New_Service'
ADD_PROCESS_NAME = 'Delete_Policy_Map'
service_id = ''
service_ext_ref = ''
#Instantiate new Policy_Map_Management WF dedicated for the device_id.
if not 'policy_map_service_instance' in context:
    data = dict(device_id=device_ref)
    orch.execute_service(SERVICE_NAME, CREATE_PROCESS_NAME, data)
    response = json.loads(orch.content)
    #context['response'] = response
    status = response.get('status').get('status')
    if status == constants.ENDED:
        if 'serviceId' in response:
            service_id = response.get('serviceId').get('id')
            service_ext_ref = response.get('serviceId').get('serviceExternalReference')
            #Store service_instance_id of Policy_Map_Management WF in context.
            context['policy_map_service_instance'] = dict(external_ref=service_ext_ref, instance_id=service_id)
        else:
            ret = MSA_API.process_content(constants.FAILED, 'Missing service id return by orchestration operation.', context, True)
            print(ret)
    else:
        ret = MSA_API.process_content(constants.FAILED, 'Execute service operation failed.', context, True)
        print(ret)
#Update service_instance external reference to "POLICY_MAP_" + device_ext_ref (e.g: POLICY_MAP_UBI2455).
#service_ext_ref = 'POLICY_MAP_' + device_ext_ref

#Loop in policy_map dictionaries and in policy_map list by calling the Policy_Map_Management process 'Add_ACL'.
data = dict()
for key, policy_map_list  in policy_map_dicts.items():
    policy_map_name = ''
    #ensure policy_map_list is not empty otherwise break the loop.
    if len(policy_map_list):
        count = 0
        data_policy_map_list = list()
        #loop in policy_map list (specific sheet config).
        for policy_map in policy_map_list:
            data_policy_map_dict = dict()
            if isinstance(policy_map, dict):
                if count == 0:
                    policy_map_name = get_config_param_val(context, policy_map, 'policy_map_name')
                else:
                    data_policy_map_dict['class_map'] = get_config_param_val(context, policy_map, 'class_name')
                if data_policy_map_dict:
                    data_policy_map_list.append(data_policy_map_dict.copy())
                count +=1
        #prepare data dict
        data['policy_map_name'] = policy_map_name
        data['policy'] = data_policy_map_list
        #execute 'Policy_Map_Management' process 'Delete_Policy_Map'
        if isinstance(data, dict):
            context['delete_policy_map_data'] = data
            service_ext_ref = context.get('policy_map_service_instance').get('external_ref')
            #execute service by ref.
            orch.execute_service_by_reference(ubiqube_id, service_ext_ref, SERVICE_NAME, ADD_PROCESS_NAME, data)
            response = json.loads(orch.content)
            process_id = response.get('processId').get('id')
            #get service process details.
            response = get_process_instance(orch, process_id)
            status = response.get('status').get('status')
            details = response.get('status').get('details')
            if status == constants.FAILED:
                ret = MSA_API.process_content(constants.FAILED, 'Execute service operation is failed: ' + details, context, True)
                print(ret) 

ret = MSA_API.process_content(constants.ENDED, 'Policy-map configuration deleted successfully to the device ' + device_ref, context, True)
print(ret)