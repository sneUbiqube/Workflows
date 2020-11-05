'''
Guide used for developing this task script: https://msa2.ubiqube.com/msa_sdk/order.html#msa_sdk.order.Order.command_execute

'''

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

#Initiate Order object with the device_id
obmf = Order(device_id)

#Execute ADD method of StaticRouting Microservice to add route in the device
command = 'CREATE' # MS method corresponding on ADD Static route operation

source_address = context['source_address'] #MS input variable value
subnet_mask = context['subnet_mask'] #MS input variable value
nexthop = context['nexthop'] #MS input variable value

config = dict(object_id=source_address, mask=subnet_mask, next_hop=nexthop)
obj = {"":config} #object = {'':{'object_id':'192.168.1.2', 'gateway':'192.168.1.254'}}
params = dict(static_route=obj)
context['ms_params'] = params

response = obmf.command_execute(command, params, timeout=60) #execute the MS ADD static route operation

if response.get('wo_status') == 'FAIL':
    detials = ''
    if 'wo_newparams' in response:
        detials = response.get('wo_newparams')
    ret = MSA_API.process_content('FAILED', 'Failure details: ' + detials, context, True)
    print(ret)

#store OBMF command execution response in context
context['response'] = response.get('wo_newparams')

ret = MSA_API.process_content('ENDED', 'Add static route operation is done successfully.', context, True)
print(ret)