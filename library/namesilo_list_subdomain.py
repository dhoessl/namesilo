#!/usr/bin/env python3

from ansible.module_utils.namesiloapiconnector import NamesiloApiWrapper as naw
from ansible.module_utils.namesiloapifunctions import CheckDomain
from ansible.module_utils.basic import AnsibleModule


def CheckforSubdomain():
    fields = {
            "apikey": dict(type="str", required=True),
            "domain": dict(type="str", required=True),
            "subdomain": dict(type="str", required=True),
            "type": dict(type="str", default='A'),
            "all": dict(type="bool", default=False)
    }
    module = AnsibleModule(argument_spec=fields)

    subdomain = module.params['subdomain']
    domain = module.params['domain']
    subdomain_full = subdomain + '.' + domain
    ApiConnection = naw(module.params['apikey'])

    CheckDomain(domain)

    recordlist = ApiConnection.listRecords(domain)
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
    items_to_pop = []
    num = 0
    if subdomain != '':
        for subdomain in result['information']:
            if subdomain['host'] != subdomain_full:
                items_to_pop.append(num)
            else:
                if subdomain['type'] != module.params['type'] and not module.params['all']:
                    items_to_pop.append(num)
            num += 1
        while items_to_pop:
            result['information'].pop(items_to_pop.pop())
    result['changed'] = False
    module.exit_json(**result)
    # if result['information']:
    #     result['changed'] = True
    #     module.exit_json(**result)
    # else:
    #     result['changed'] = False
    #     module.exit_json(**result)


if __name__ == '__main__':
    CheckforSubdomain()
