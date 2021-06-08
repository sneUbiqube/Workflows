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
timeout = 300
obmf.command_synchronize(timeout)

#get microservices instance by microservice object ID.
object_name = 'static_route'
object_id = context.get('source_address')
src_mask = context.get('subnet_mask')
vlan_id = context.get('vlan_id')
next_hop = context.get('nexthop')
distance = context.get('distance')
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
        ret_static_route_vlan_id = sr.get('vlan_id')
        ret_static_route_next_hop = sr.get('next_hop')
        ret_static_route_distance = sr.get('distance')
        if distance == '1' and ret_static_route_distance == 'null':
            # Set the default 'Distance' value in th Catalyst ME.
            ret_static_route_distance = '1'
        if object_id == ret_static_route_ip and src_mask == ret_static_route_mask and vlan_id == ret_static_route_vlan_id and next_hop == ret_static_route_next_hop and distance == ret_static_route_distance:
            is_static_route_matched = True

#if response equals empty dictionary it means StaticRouting object is not exist in the device yet.
if is_static_route_matched != False:
    MSA_API.task_error('Static Routing with id="' + obj_id + '" exists in the device.', context, True)
MSA_API.task_success('Static Routing with id="' + obj_id + '" does not exist in the device.', context, True)