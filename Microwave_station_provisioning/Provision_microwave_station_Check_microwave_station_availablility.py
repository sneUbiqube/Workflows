from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.order import Order
from msa_sdk.device import Device
from msa_sdk.orchestration import Orchestration
from datetime import datetime
from msa_sdk import constants
from msa_sdk import lookup
from msa_sdk import util
import ipaddress
import time
import re
import json
import sys
import os

"""
The proposals of the task are:
   - Monitor IP address availability by simple ICMP echo
   - Finish sucessfully in case if the IP address is available
"""


#New Variables object
TaskVariables = Variables()

#Add new variables
TaskVariables.add('ip_address', var_type = 'String')
TaskVariables.add('hostname', var_type = 'String')
TaskVariables.add('vlan_list.0.id', var_type = 'String')
TaskVariables.add('vlan_list.0.name', var_type = 'String')
TaskVariables.add('trunk_port', var_type = 'String')

#Add vars to context
context = Variables.task_call(TaskVariables)

#Variables to finish the task properlly
fail_comment = str()
success_comment = str()
fail_string = f'{{"wo_status": "FAIL", "wo_comment": "{fail_comment}"}}'
success_string = f'{{"wo_status": "ENDED", "wo_comment": "{success_comment}"}}'

#Create Orchestration object to update GUI dynamically
Orchestration = Orchestration(context['UBIQUBEID'])
async_update_list = (context['PROCESSINSTANCEID'], context['TASKID'], context['EXECNUMBER'])

#Import microservice alias list
with open('/opt/fmc_repository/Process/Microwave_station_provisioning/microservices_list.json', 'r') as alias_file:
  	context['ms_aliases'] = json.load(alias_file)

#Flag to know when microwave station becoms available
is_available = False

Orchestration.update_asynchronous_task_details(*async_update_list, 'Check microwave station availability. IP is {}... '.format(context['ip_address']))
#String to check availability
ping_string = "ping  -c 1 -W 1 {} | grep -oP '(0|100)%\s+?packet\s+?loss'".format(context['ip_address'])

while not is_available:
    if os.popen(ping_string).read().startswith('0%'):
      is_available = True
    else:
      time.sleep(10)

Orchestration.update_asynchronous_task_details(*async_update_list, 'Check microwave station availability. IP is {}... OK'.format(context['ip_address']))      


#Finish the task correctlly
result = MSA_API.process_content('ENDED', 'Station with IP {} is available now.'.format(context['ip_address']), context, True)
print(result)

