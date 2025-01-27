#!/usr/bin/python3

from ansible.module_utils.namesiloapiconnector import NamesiloApiWrapper as naw
from ansible.module_utils.basic import AnsibleModule


class namesilo:
    def __init__(self):
        fields = {
            "apikey": {
                'type': "str",
                'required': True,
                'no_log': True
            },
            "domain": {
                'type': "str",
                'required': True
            },
            "type": {
                'type': "str",
                'default': 'A',
                'choices': ['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'SRV']
            },
            "host": {
                'type': "str",
                'default': ''
            },
            "value": {
                'type': "str",
                'required': True
            },
            "ttl": {
                'type': "int",
                'default': 3600
            },
            "distance": {
                'type': "int",
                'default': 10
            },
            "state": {
                'type': "str",
                'default': "present",
                'choices': ['present', 'absent']
            }
        }
        self.module = AnsibleModule(
            argument_spec=fields,
            supports_check_mode=False
        )
        result = {
            'changed': False,
            'host': self.module.params['host'] + '.' + self.module.params['domain'],
            'value': self.module.params['value'],
            'ttl': self.module.params['ttl'],
            'type': self.module.params['type'],
            'state': self.module.params['state']
        }
        if self.module.params['host'] == '':
            result['host'] = self.module.params['domain']
        else:
            result['host'] = self.module.params['host'] + '.' + self.module.params['domain']
        if self.module.params['type'] == 'MX':
            result['distance'] = self.module.params['distance']

        self.ApiConnection = naw(self.module.params['apikey'])

        # Request current DNS Entries
        hosts = self.CheckforRecord()
        # Check if the host is in the existing entries
        # If thats the case just update its config
        for host in hosts:
            if host["host"] != result["host"]:
                continue
            if host["type"] != result["type"]:
                continue
            if self.module.params['state'] != "present":
                self.change_settings(host, 'delete')
            if (host["ttl"] != str(self.module.params["ttl"])
                    or host["value"] != self.module.params["value"]):
                self.change_settings(host, "update")
            if self.module.params['type'] != 'MX':
                self.module.exit_json(**result)
            if host['distance'] == str(self.module.params['distance']):
                self.module.exit_json(**result)
            self.change_settings(host, 'update')
        # if the host to change is not in the current entries and state is absent, delete it
        if self.module.params['state'] == 'absent':
            self.module.exit_json(**result)
        # if some other keyword than "present" or "absent" is used -> fail
        if self.module.params["state"] != "present":
            self.module.fail_json(
                msg='Could not determine what to do with provided information!',
                **result
            )
        # if host is not found in existing entries and should be present -> create
        self.AddRecord()
        changed_result = dict(old_data={}, changed=True)
        new_data = self.CheckforRecord()
        for data in new_data:
            if data["host"] != result["host"]:
                continue
            if data["type"] != self.module.params["type"]:
                continue
            if data["value"] != self.module.params["value"]:
                continue
            changed_result['new_data'] = data
            changed_result['diff'] = data
        self.module.exit_json(**changed_result)

    def change_settings(self, old_host_data, action):
        if action == 'update':
            self.UpdateDns(old_host_data['record_id'])
        elif action == 'delete':
            self.DeleteRecord(old_host_data['record_id'])
        result = dict(old_data=old_host_data, changed=True)
        new_data = self.CheckforRecord()
        for host in new_data:
            if host['record_id'] == old_host_data['record_id']:
                result['new_data'] = host
        self.module.exit_json(**result)

    def CheckforRecord(self) -> list:
        api_result = self.ApiConnection.listRecords(
            self.module.params['domain']
        )
        result = {}
        # If no RR is set just output the result
        if 'No DNS ' in api_result['reply']['detail']:
            return []
        # If call was not successfull print the error
        if api_result['reply']['detail'] != 'success':
            result['detail'] = api_result['reply']['detail']
            self.module.fail_json(
                msg='Could not fetch information from API',
                **result
            )
        # Output the resource_record list
        return api_result["reply"]["resource_record"]

    def AddRecord(self):
        self.ApiConnection.addRecord(
            self.module.params['domain'],
            self.module.params['type'],
            self.module.params['host'],
            self.module.params['value'],
            str(self.module.params['distance']),
            str(self.module.params['ttl'])
        )

    def DeleteRecord(self, rrid):
        self.ApiConnection.deleteRecord(
            self.module.params['domain'],
            rrid
        )

    def UpdateDns(self, rrid):
        self.ApiConnection.updateRecord(
            self.module.params['domain'],
            rrid,
            self.module.params['host'],
            self.module.params['value'],
            str(self.module.params['distance']),
            str(self.module.params['ttl'])
        )


if __name__ == '__main__':
    namesilo_mod = namesilo()
