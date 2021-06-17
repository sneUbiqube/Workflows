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
# instantiate device object
obmf  = Order(device_id=device_id)
#synchronise device microservices
timeout = 300
obmf.command_synchronize(timeout)

#get microservices instance by microservice object ID.
object_name = 'access_lists'

access_lists = context['access_lists']
good_values = dict()

if access_lists:
  for rule in access_lists:
    object_id   = str(rule.get('acl_name'))
    obmf.command_objects_instances_by_id(object_name, object_id)
    response = json.loads(obmf.content)
    context.update(obmf_sync_resp=response)
    #if response equals empty dictionary it means class map object is not exist in the device yet.
    if response:
      MSA_API.task_error('ACL with id="' + object_id + '" is already exists in the device.', context, True) 
    #MSA_API.task_success('ACL Map with id="' + object_id + '" does not exist in the device yet.', context, True)
    good_values[object_id]= 1                        


if (len(good_values)):
  good_values_string =  ", ".join(good_values.keys())
else: 
  good_values_string =  ""

MSA_API.task_success('Good, ACL with ids('+good_values_string+') does not exist in the device yet.', context, True)

