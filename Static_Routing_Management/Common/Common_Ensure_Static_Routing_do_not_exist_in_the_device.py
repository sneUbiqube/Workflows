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

object_name = 'static_route'

command = 'IMPORT'
params = dict(object_name="0")
#synchronise the given device microservice

params = dict()
params[object_name] = "0"
#synchronise the given device microservice
obmf.command_call(command, 0, params) # put 0 to not update the db

#get microservices instance by microservice object ID.
object_id = context.get('source_address')
src_mask = context.get('subnet_mask')
vlan_id = context.get('vlan_id')
next_hop = context.get('nexthop')
distance = context.get('distance')
response = json.loads(obmf.content)
context.update(obmf_sync_resp=response)

#ensure the object inputs are in the response.
is_static_route_matched = False
obj_id = object_id.replace('.', "_")

#response={'entity': {'commandId': 0, 'status': 'OK', 'message': '{"static_route":{"10_100_100_32":{"object_id":"10.100.100.32","mask":"255.255.255.255","vlan_id":"GigabitEthernet2","next_hop":"10.166.129.14","distance":null},"10_100_100_33":{"object_id":"10.100.100.33","mask":"255.255.255.255","vlan_id":"GigabitEthernet2","next_hop":"10.166.129.14","distance":null},"10_100_100_34":{"object_id":"10.100.100.34","mask":"255.255.255.255","vlan_id":"GigabitEthernet2","next_hop":"10.166.129.14","distance":null},"10_100_100_35":{"object_id":"10.100.100.35","mask":"255.255.255.255","vlan_id":"GigabitEthernet2","next_hop":"10.166.129.14","distance":null},"10_100_100_36":{"object_id":"10.100.100.36","mask":"255.255.255.255","vlan_id":"GigabitEthernet2","next_hop":"10.166.129.14","distance":null},"10_100_100_37":{"object_id":"10.100.100.37","mask":"255.255.255.255","vlan_id":"GigabitEthernet2","next_hop":"10.166.129.14","distance":null},"10_100_100_38":{"object_id":"10.100.100.38","mask":"255.255.255.255","vlan_id":"GigabitEthernet2","next_hop":"10.166.129.14","distance":null},"10_100_100_39":{"object_id":"10.100.100.39","mask":"255.255.255.255","vlan_id":"GigabitEthernet2","next_hop":"10.166.129.14","distance":null},"10_100_100_40":{"object_id":"10.100.100.40","mask":"255.255.255.255","vlan_id":"GigabitEthernet2","next_hop":"10.166.129.14","distance":null},"10_100_100_41":{"object_id":"10.100.100.41","mask":"255.255.255.255","vlan_id":"GigabitEthernet2","next_hop":"1...

message = response.get('entity').get('message')

if message:
    #Convert message into array
    message = json.loads(message)
    if obj_id in message.get(object_name):

        sr = message.get(object_name).get(obj_id)
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
