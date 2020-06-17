"""
The goal of this tool is to demonstrate Netconf and its ability to return structured data
as well as push configurations in a structured format while providing the ability to confirm results before
commiting changes. 
"""
__author__ = 'Xander Petty'

from ncclient import manager 
import xmltodict
import json
from getpass import getpass 
from pprint import pprint 
from lxml import etree 
from lxml.builder import E as Element 

if __name__ == '__main__':
    # Connect to Netconf on lab device
    username = 'admin'
    password = getpass('Local admin password: ')
    ip = '10.179.0.37'
    port = 830
    netconf = manager.connect(host=ip, username=username, password=password, port=port, hostkey_verify=False)

    # Demonstrate pulling ARP data from Operational state
    arp_filter = etree.tostring(
        Element(
            'filter',
            Element(
                'arp-data',
                Element(
                    'arp-vrf',
                    Element(
                        'vrf',
                        'Default'
                    )
                ),
                xmlns='http://cisco.com/ns/yang/Cisco-IOS-XE-arp-oper'
            )
        ), pretty_print=True
    ).decode()
    arp_xml = netconf.get(filter=arp_filter).xml 
    arp_dict = xmltodict.parse(arp_xml)['rpc-reply']['data']['arp-data']['arp-vrf']['arp-oper']
    arp_json = json.loads(json.dumps(arp_dict))
    pprint(arp_json)

    # Demonstrate pulling interface data from Operational state
    interface_filter = etree.tostring(
        Element(
            'filter',
            Element(
                'interfaces',
                Element(
                    'interface',
                    Element(
                        'name'
                    ),
                    Element(
                        'admin-status'
                    ),
                    Element(
                        'oper-status'
                    ),
                    Element(
                        'last-change'
                    ),
                    Element(
                        'phys-address'
                    ),
                    Element(
                        'speed'
                    ),
                    Element(
                        'ipv4'
                    ),
                    Element(
                        'ipv4-subnet-mask'
                    ),
                    Element(
                        'description'
                    ),
                    Element(
                        'mtu'
                    ),
                    Element(
                        'input-security-acl'
                    ),
                    Element(
                        'output-security-acl'
                    )
                ),
                xmlns='http://cisco.com/ns/yang/Cisco-IOS-XE-interfaces-oper'
            )
        ), pretty_print=True
    ).decode()
    interface_xml = netconf.get(filter=interface_filter).xml
    interface_dict = xmltodict.parse(interface_xml)['rpc-reply']['data']['interfaces']['interface']
    interface_json = json.loads(json.dumps(interface_dict))
    pprint(interface_json)

    # Demonstrate pulling interface configuration from the running config with IETF 
    interface_filter = etree.tostring(
        Element(
            'filter',
            Element(
                'interfaces',
                Element(
                    'interface'
                ),
                xmlns='urn:ietf:params:xml:ns:yang:ietf-interfaces'
            )
        ), pretty_print=True
    ).decode()
    interface_xml = netconf.get_config(source='running', filter=interface_filter).xml
    interface_dict = xmltodict.parse(interface_xml)['rpc-reply']['data']['interfaces']['interface']
    interface_json = json.loads(json.dumps(interface_dict))
    pprint(interface_json)

    # Demonstrate pulling line config information from the running config 
    line_filter = etree.tostring(
        Element(
            'filter',
            Element(
                'native',
                Element(
                    'line',
                    Element(
                        'line-list'
                    )
                )
            )
        )
    )