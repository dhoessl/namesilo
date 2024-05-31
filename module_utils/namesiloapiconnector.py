#!/etc/namesilo_api/bin/python3

import requests
import xmltodict


class NamesiloApiWrapper:
    def __init__(self, key):
        self.key = key
        self.api_uri = 'https://www.namesilo.com/api/'
        self.api_options = '?version=1&type=xml&key=' + self.key

    def listRecords(self, domain):
        recordlist = requests.get(self.api_uri
                                  + 'dnsListRecords' + self.api_options
                                  + '&domain=' + domain
                                  ).text
        return xmltodict.parse(recordlist)

    def addRecord(self,
                  domain,
                  rrtype,
                  rrhost,
                  rrvalue,
                  rrdistance='10',
                  rrttl='3600'):
        function_options = '&domain=' + domain \
                + '&rrtype=' + rrtype \
                + '&rrhost=' + rrhost \
                + '&rrvalue=' + rrvalue \
                + '&rrttl=' + rrttl
        if rrtype == 'MX':
            function_options += '&rrdistance=' + rrdistance
        output = requests.get(self.api_uri
                              + 'dnsAddRecord'
                              + self.api_options
                              + function_options
                              ).text
        return xmltodict.parse(output)

    def updateRecord(self,
                     domain,
                     rrid,
                     rrhost,
                     rrvalue,
                     rrdistance='10',
                     rrttl='3600'):
        function_options = '&domain=' + domain \
                + '&rrid=' + rrid \
                + '&rrhost=' + rrhost \
                + '&rrvalue=' + rrvalue \
                + '&rrttl=' + rrttl
        if rrdistance != '10':
            function_options += '&rrdistance=' + rrdistance
        output = requests.get(self.api_uri
                              + 'dnsUpdateRecord'
                              + self.api_options
                              + function_options
                              ).text
        return xmltodict.parse(output)

    def deleteRecord(self, domain, rrid):
        function_options = '&domain=' + domain \
                + '&rrid=' + rrid
        output = requests.get(self.api_uri
                              + 'dnsDeleteRecord'
                              + self.api_options
                              + function_options
                              ).text
        return xmltodict.parse(output)


if __name__ == '__main__':
    NamesiloApiWrapper()
