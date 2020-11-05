from msa_sdk.order import Order
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

dev_var = Variables()
dev_var.add('acl_name', var_type='String')
dev_var.add('conditions', var_type='String')
dev_var.add('protocol', var_type='String')
dev_var.add('source_address', var_type='String')
dev_var.add('source_wildcardmask', var_type='String')
dev_var.add('source_port', var_type='String')
dev_var.add('destination_address', var_type='String')
dev_var.add('destination_wildcardmask', var_type='String')
dev_var.add('destination_port', var_type='String')

context = Variables.task_call(dev_var)

#get device_id from context
device_id = context['device_id'][3:]

#Initiate Order object with the device_id
obmf = Order(device_id)

#Execute ADD method of StaticRouting Microservice to add route in the device
command = 'CREATE' # MS method corresponding on ADD Static route operation

object_id = context.get('acl_name')
condition = context.get('conditions')
protocol = context.get('protocol')
src_address = context.get('source_address')
src_wildcard = context.get('source_wildcardmask')
src_port = context.get('source_port')
dst_address = context.get('destination_address')
dst_wildcard = context.get('destination_wildcardmask')
dst_port = context.get('destination_port')

#build MS the dictionary input object 
config = dict(object_id=object_id)
if all (k in context for k in ('conditions', 'protocol')):
    if condition:
        config['condition'] = condition
        config['protocol'] = protocol
        config['src_address'] = src_address
        config['src_wildcard'] = src_wildcard
        config['src_port'] = src_port
        config['dst_address'] = dst_address
        config['dst_wildcard'] = dst_wildcard
        config['dst_port'] = dst_port
    
obj = {"":config} #object = {'':{'object_id':'192.168.1.2', 'gateway':'192.168.1.254'}}
params = dict(access_lists=obj)

context['ns_params_create'] = params

response = obmf.command_execute(command, params, timeout=60) #execute the MS ADD static route operation

if response.get('wo_status') == 'FAIL':
    detials = ''
    if 'wo_newparams' in response:
        detials = response.get('wo_newparams')
    ret = MSA_API.process_content('FAILED', 'Failure details: ' + detials, context, True)
    print(ret)

#store OBMF command execution response in context
context['response'] = response.get('wo_newparams')

ret = MSA_API.process_content('ENDED', 'Add ACL operation is done successfully.', context, True)
print(ret)