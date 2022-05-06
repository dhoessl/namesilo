#!/usr/bin/env python3

from ansible.module_utils.namesiloapiconnector import NamesiloApiWrapper as naw
from ansible.module_utils.basic import AnsibleModule


def CheckforDomain():
    fields = {
            "apikey": dict(type="str", required=True),
            "domain": dict(type="str", required=True)
    }
    module = AnsibleModule(argument_spec=fields)

    ApiConnection = naw(module.params['apikey'])
    recordlist = ApiConnection.listRecords(module.params['domain'])
    result = {}

    # kr and vr are the keys and values for the record
    # kd and vd are the domain specific keys and values
    for k, v in recordlist.items():
        for k1, v1 in v.items():
            if k1 == 'reply':
                for kr, vr in v1.items():
                    if kr == 'code':
                        result['code'] = vr
                        if result['code'] == '300':
                            pass
                    elif kr == 'detail':
                        result['detail'] = vr
                        if result['detail'] != 'success':
                            result['rc'] = 1
                    elif kr == 'resource_record':
                        result['information'] = []
                        for ld in vr:
                            subdom_inf = {}
                            for kd, vd in ld.items():
                                subdom_inf[kd] = vd
                            result['information'].append(subdom_inf)
    result['changed'] = False
    module.exit_json(**result)
    # if result['information']:
    #     result['changed'] = True
    #     module.exit_json(**result)
    # else:
    #     result['changed'] = False
    #     module.exit_json(**result)


if __name__ == '__main__':
    CheckforDomain()
