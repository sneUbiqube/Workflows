import json
from msa_sdk import constants
from msa_sdk.order import Order
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

dev_var = Variables()
dev_var.add('access_lists.0.acl_name', var_type='String')
dev_var.add('access_lists.0.acl.0.condition', var_type='String')
dev_var.add('access_lists.0.acl.0.protocol', var_type='String')
dev_var.add('access_lists.0.acl.0.src_address', var_type='String')
dev_var.add('access_lists.0.acl.0.src_wildcard', var_type='String')
dev_var.add('access_lists.0.acl.0.src_port', var_type='String')
dev_var.add('access_lists.0.acl.0.dst_address', var_type='String')
dev_var.add('access_lists.0.acl.0.dst_wildcard', var_type='String')
dev_var.add('access_lists.0.acl.0.dst_port', var_type='String')
context = Variables.task_call(dev_var)

#get device_id from context
device_id = context['device_id'][3:]

#Initiate Order object with the device_id
obmf = Order(device_id)

#Execute ADD method of StaticRouting Microservice to add route in the device
command = 'CREATE' # MS method corresponding on ADD Static route operation

#build MS the dictionary input object
access_lists = context.get('access_lists')

config = dict(access_lists=access_lists)
config['object_id']= "object_id"   #add mandatory field object_id, put only one default value

obj = {"":config} #object = {'':{'object_id':'192.168.1.2', 'gateway':'192.168.1.254'}}
params = dict(access_lists=obj)

context['ns_params_create'] = params

obmf.command_execute(command, params, timeout = 300) #execute the MS ADD static route operation
response = json.loads(obmf.content)

if response.get('wo_status') == constants.FAILED:
    detials = ''
    if 'wo_newparams' in response:
        detials = response.get('wo_newparams')
    MSA_API.task_error('Failure details: ' + detials, context, True)

#store OBMF command execution response in context
context['response'] = response.get('wo_newparams')

MSA_API.task_success('Add ACL operation is done successfully.', context, True)