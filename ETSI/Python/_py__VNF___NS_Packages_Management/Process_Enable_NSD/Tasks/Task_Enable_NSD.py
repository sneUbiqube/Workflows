from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

from custom.ETSI.NsdSol005 import NsdSol005


if __name__ == "__main__":

    dev_var = Variables()
    dev_var.add('ns_package_id', var_type='String')
    context = Variables.task_call(dev_var)
    
    _state = True

    nsdApi = NsdSol005(context["mano_ip"], context["mano_port"])
    nsdApi.set_parameters(context['mano_user'], context['mano_pass'])
    r = nsdApi.set_operational_state(context['ns_package_id'], _state)

    ret = MSA_API.process_content('ENDED', f'{r}', context, True)
    print(ret)