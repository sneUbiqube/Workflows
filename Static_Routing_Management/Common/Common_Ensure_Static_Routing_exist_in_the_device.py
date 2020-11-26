import json
from msa_sdk import constants
from msa_sdk.order import Order
from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
dev_var = Variables()
dev_var.add('source_address', var_type='IPAddress')
dev_var.add('subnet_mask', var_type='IPMask')
dev_var.add('vlan_id', var_type='Interger')
dev_var.add('nexthop', var_type='IPAddress')
dev_var.add('distance', var_type='Interger')
context = Variables.task_call(dev_var)

#get device_id from context
device_id = context['device_id'][3:]
# instantiate device object
obmf  = Order(device_id=device_id)
#synchronise device microservices
timeout = 60
obmf.command_synchronize(timeout)

#get microservices instance by microservice object ID.
object_name = 'static_route'
object_id = context.get('source_address')
src_mask = context.get('subnet_mask')
obmf.command_objects_instances_by_id(object_name, object_id)
response = json.loads(obmf.content)
context.update(obmf_sync_resp=response)

#ensure the object inputs are in the response.
is_static_route_matched = False
obj_id = object_id.replace('.', "_")
if response:
    if obj_id in response.get(object_name): 
        sr = response.get(object_name).get(obj_id)
        ret_static_route_ip = sr.get('object_id')
        ret_static_route_mask = sr.get('mask')
        if ret_static_route_ip == object_id and src_mask == ret_static_route_mask:
            is_static_route_matched = True    

#if response equals empty dictionary it means class map object is not exist in the device yet.
if is_static_route_matched != True:
    ret = MSA_API.process_content(constants.FAILED, 'Static Routing with id="' + obj_id + '" does not exist in the device.', context, True)
    print(ret)
ret = MSA_API.process_content(constants.ENDED, 'Static Routing with id="' + obj_id + '" exists in the device.', context, True)
print(ret)