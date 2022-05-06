#!/usr/bin/env python3

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
                supports_check_mode=False)
        result = {
            'changed': False,
            'host': self.module.params['host'] + '.' + self.module.params['domain'],  # noqa: E501
            'value': self.module.params['value'],
            'ttl': self.module.params['ttl'],
            'type': self.module.params['type'],
            'state': self.module.params['state']
        }
        if self.module.params['host'] == '':
            result['host'] = self.module.params['domain']
        else:
            result['host'] = self.module.params['host'] + '.' + self.module.params['domain']  # noqa: E501
        if self.module.params['type'] == 'MX':
            result['distance'] = self.module.params['distance']

        self.ApiConnection = naw(self.module.params['apikey'])

        hosts = self.CheckforRecord()
        for host in hosts:
            if (result['host'] == host['host']
                    and self.module.params['type'] == host['type']):
                if self.module.params['state'] == 'present':
                    if (host['ttl'] == str(self.module.params['ttl']) and
                            host['value'] == self.module.params['value']):
                        if self.module.params['type'] != 'MX':
                            self.module.exit_json(**result)
                        elif host['distance'] == str(self.module.params['distance']):  # noqa: E501
                            self.module.exit_json(**result)
                        else:
                            self.change_settings(host, 'update')
                    else:
                        self.change_settings(host, 'update')
                else:
                    self.change_settings(host, 'delete')
        if self.module.params['state'] == 'present':
            self.AddRecord()
            changed_result = dict(old_data={}, changed=True)
            new_data = self.CheckforRecord()
            for data in new_data:
                if ((data['host'] == result['host'] and
                        data['type'] == self.module.params['type']) and
                        data['value'] == self.module.params['value']):
                    changed_result['new_data'] = data
                    changed_result['diff'] = data
            self.module.exit_json(**changed_result)
        elif self.module.params['state'] == 'absent':
            self.module.exit_json(**result)
        else:
            self.module.fail_json(msg='Could not determine what to do with provided information!', **result)  # noqa: E501

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

    def CheckforRecord(self):
        api_result = self.ApiConnection.listRecords(self.module.params['domain'])  # noqa: E501
        result = {}
        result['information'] = []
        if 'No DNS ' in api_result['namesilo']['reply']['detail']:
            pass
        elif api_result['namesilo']['reply']['detail'] != 'success':
            result['detail'] = api_result['namesilo']['reply']['detail']
            self.module.fail_json(
                    msg='Could not fetch information from API',
                    **result
            )
        if api_result['namesilo']['reply']['resource_record']:
            for record in api_result['namesilo']['reply']['resource_record']:
                if isinstance(record, str):
                    continue
                subdomain_information = dict()
                for subdomain_field in record:
                    subdomain_information[subdomain_field] = record[subdomain_field]  # noqa: E501
                result['information'].append(subdomain_information)
        return result['information']

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
