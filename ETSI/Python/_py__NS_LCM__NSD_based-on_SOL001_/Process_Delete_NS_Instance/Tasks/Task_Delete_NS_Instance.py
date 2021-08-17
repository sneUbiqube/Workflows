from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API

from custom.ETSI.NsLcmSol005 import NsLcmSol005


if __name__ == "__main__":

    dev_var = Variables()
    context = Variables.task_call(dev_var)

    nsLcm = NsLcmSol005('10.31.1.245', '8080')
    nsLcm.set_parameters(context['mano_user'], context['mano_pass'])
    
    r = nsLcm.ns_lcm_delete_instance_of_ns(context["ns_instance_id"])
    
    ret = MSA_API.process_content('ENDED', f'{r}', context, True)
    print(ret)