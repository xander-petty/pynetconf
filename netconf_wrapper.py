"""
Python wrapper to interact with netconf 
"""
__author__ = 'Xander Petty'
__contact__ = 'Alexander.Petty@williams.com'
__version__ = '1.0'

from ncclient import manager 
import os 
from lxml.builder import E 
from lxml import etree 
import xmltodict
from pprint import pprint 
from time import sleep 

class NetConf():
    def __init__(self, host, port, username, password, hostkey_verify=False):
        params = {
            'host': host,
            'port': port,
            'username': username,
            'password': password,
            'hostkey_verify': hostkey_verify
        }
        self.m = manager.connect(**params)
    def disconnect(self):
        self.m.close_session()
    def verify_connection(self):
        return self.m.connected 
    def list_capabilities(self):
        return list(self.m.server_capabilities)
    def list_netconf_capabilities(self):
        netcap = []
        cap = self.m.server_capabilities
        for i in cap:
            if str(i).__contains__('urn'):
                if str(i).__contains__('yang:'):
                    netcap.append(
                        i.split('yang:')[1].split('?')[0]
                    )
        return netcap 
    def download_netconf_capabilities(self, folder):
        cwd = os.getcwd()
        path = str(f'{cwd}\\{folder}')
        os.mkdir(path)
        cap = self.list_netconf_capabilities()
        for yang in cap:
            try:
                schema = str(self.m.get_schema(yang))
                name = str(f'{yang}.yang')
                write_path = path + '\\' + name
                file = open(write_path, 'w')
                file.write(schema)
                file.close()
            except:
                pass 
    def print_yang_model(self, model):
        print(self.m.get_schema(model))
    def get_ietf_interfaces(self):
        namespace = 'urn:ietf:params:xml:ns:yang:ietf-interfaces'
        interface_filter = etree.tostring(
            E(
                'filter',
                E(
                    'interfaces',
                    E(
                        'interface',
                        E('name'),
                        E('enabled'),
                        E('description')
                    ),
                    xmlns=namespace
                )
            ), pretty_print=True
        ).decode()
        return xmltodict.parse(self.m.get(filter=interface_filter).xml)['rpc-reply']['data']
    def get_ietf_routing_instance(self):
        namespace = 'urn:ietf:params:xml:ns:yang:ietf-routing'
        routing_filter = etree.tostring(
            E(
                'filter',
                E(
                    'routing',
                    E(
                        'routing-instance'
                    ),
                    xmlns=namespace
                )
            ), pretty_print=True
        ).decode()
        return xmltodict.parse(self.m.get(filter=routing_filter).xml)['rpc-reply']['data']
    

if __name__ == '__main__':
    username = 'developer'
    password = 'C1sco12345'
    ip = 'ios-xe-mgmt.cisco.com'
    port = 10000
    params = {
        'username': username,
        'password': password,
        'host': ip,
        'port': port
    }
    # TEST CONNECTION
    netconf = NetConf(**params)
    netconf.verify_connection()
    sleep(2)
    
    # TEST INTERFACE YANG
    interfaces = netconf.get_ietf_interfaces()['interfaces']['interface']
    pprint(interfaces)
    sleep(2)

    # TEST ROUTING YANG 
    routing = netconf.get_ietf_routing_instance()['routing']['routing-instance']
    pprint(routing)
    sleep(2)

    # TEST CAPABILITIES LIST
    all_capabilities = netconf.list_capabilities()
    for cap in all_capabilities:
        print(cap)
    sleep(2)

    # TEST NETCONF CAPABILITIES FILTER
    netconf_abilities = netconf.list_netconf_capabilities()
    for cap in netconf_abilities:
        print(cap)
    sleep(2)

    # TEST PRINT YANG MODEL
    netconf.print_yang_model('ietf-interfaces')
    sleep(2)

    # TEST DOWNLOAD ALL NETCONF-YANG MODELS 
    folder_name = 'yang_model_test'
    netconf.download_netconf_capabilities(folder_name)
    sleep(2)

    # DISCONNECT
    netconf.disconnect()
