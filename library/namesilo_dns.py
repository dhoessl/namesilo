#!/usr/bin/python3

from ansible.module_utils.basic import AnsibleModule
from api import NamesiloAPI, Domain, DomainRecordStateError

def main():
    module_args = {
        "api_key": {
            "type": "str",
            "required": True,
            "no_log": True
        },
        "domains": {
            "type": "list",
            "required": True
        }
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    result = {
        "changed": False,
        "original_domains": module.params["domains"],
        "domains": None
    }

    api = NamesiloAPI(module.params["api_key"])

    for domain in module.params["domains"]:
        try:
            namesilo_domain = Domain(domain["name"], api, domain["records"])
        except DomainRecordStateError as e:
            module.fail_json(
                msg=f"{e}",
                **result
            )
        for record in namesilo_domain.records:
            if record["state"] in ["updated", "added", "removed"]:
                result["changed"] = True
        result["domains"].append({
            "name": domain["name"],
            "records": namesilo_domain.records
        })
    module.exit_json(**result)

if __name__ == "__main__":
    main()
