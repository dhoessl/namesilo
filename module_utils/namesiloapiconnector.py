#!/usr/bin/python3

from requests import get

class NamesiloApiWrapper:
    def __init__(self, key) -> None:
        self.key = key
        self.api_uri = 'https://www.namesilo.com/api/'
        self.api_options = '?version=1&type=json&key=' + self.key

    def listRecords(self, domain) -> dict:
        response = get(
            self.api_uri
            + 'dnsListRecords' + self.api_options
            + '&domain=' + domain
        )
        return response.json()

    def addRecord(self, domain, rrtype, rrhost, rrvalue,
                  rrdistance='10', rrttl='3600') -> dict:
        record_options = '&domain=' + domain + '&rrtype=' + rrtype \
                + '&rrhost=' + rrhost + '&rrvalue=' + rrvalue \
                + '&rrttl=' + rrttl
        if rrtype == 'MX':
            record_options += '&rrdistance=' + rrdistance
        response = get(
            self.api_uri
            + 'dnsAddRecord'
            + self.api_options
            + function_options
        )
        return response.json()

    def updateRecord(self, domain, rrid, rrhost, rrvalue,
                     rrdistance='10', rrttl='3600') -> dict:
        function_options = '&domain=' + domain + '&rrid=' + rrid \
                + '&rrhost=' + rrhost + '&rrvalue=' + rrvalue \
                + '&rrttl=' + rrttl
        if rrdistance != '10':
            function_options += '&rrdistance=' + rrdistance
        response = get(
            self.api_uri
            + 'dnsUpdateRecord'
            + self.api_options
            + function_options
        )
        return response.json()

    def deleteRecord(self, domain, rrid) -> dict:
        function_options = '&domain=' + domain + '&rrid=' + rrid
        response = requests.get(
            self.api_uri
            + 'dnsDeleteRecord'
            + self.api_options
            + function_options
        )
        return response.json()


if __name__ == '__main__':
    NamesiloApiWrapper()
