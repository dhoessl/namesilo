Role Name
=========

Create, delete and update Namesilo DNS Records from ansible playbook

Requirements
------------

This Module requires [namesilo-py](https://github.com/dhoessl/namesilo-py) which will be installed by the main task itself, if not present as python module

Role Variables
--------------

| var | value | default |
| --- | ----- | ------- |
| `namesilo_api_key` | Your namesilo Api key - should be placed in a vault | `None` |
| `namesilo_domains` | list of domains to manage - example below | `[]` |

`namesilo_domains` example
------------------
```
---
namesilo_domains:
  - name: "example.com"
    records:
      - host: "namesilo-test"
        type: "A"
        value: "0.0.0.0"
        ttl: "3600"
      - host: ""
        type: "MX"
        value: "mail.example.com"
        ttl: "3600"
        distance: "5"
...
```

Example Playbook
----------------
```
---
- hosts: 'localhost'
  roles:
    - role: 'namesilo'
      tags: 'namesilo'
...
```
License
-------

GPL-3.0

Author Information
------------------

* Dominic Hößl <dhoessl@dhoessl.de>

