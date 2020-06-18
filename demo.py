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
    # username = 'admin'
    # password = getpass('Local admin password: ')
    # ip = '10.179.0.37'
    # port = 830
    username = 'developer'
    password = 'C1sco12345'
    port = 10000
    ip = 'ios-xe-mgmt.cisco.com'
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
    interface_xml = netconf.get_config(choice='running', filter=interface_filter).xml
    interface_dict = xmltodict.parse(interface_xml)['rpc-reply']['data']['interfaces']['interface']
    interface_json = json.loads(json.dumps(interface_dict))
    pprint(interface_json)

    # Demonstration of pulling line card information from Operational state
    line_filter = etree.tostring(
        Element(
            'filter',
            Element(
                'linecard-oper-data',
                Element(
                    'linecard'
                ),
                xmlns='http://cisco.com/ns/yang/Cisco-IOS-XE-linecard-oper'
            )
        ), pretty_print=True
    ).decode()
    line_xml = netconf.get(filter=line_filter).xml
    line_dict = xmltodict.parse(line_xml)['rpc-reply']['data']['linecard-oper-data']['linecard']
    line_json = json.loads(json.dumps(line_dict))
    pprint(line_json)

    # Testing of building config differently
    def src_dst_choice(*args):
        choice = []
        for e in args:
            if str(type(e)) == "<class 'dict'>":
                choice.append(
                    Element(
                        list(e.items())[0][0],
                        list(e.items())[0][1]
                    )
                )
            elif str(type(e)) == "<class 'str'>":
                choice.append(
                    Element(
                        e
                    )
                )
            elif str(type(e)) == "<class 'list'>":
                for i in e:
                    if str(type(i)) == "<class 'dict'>":
                        choice.append(
                            Element(
                                list(i.items())[0][0],
                                list(i.items())[0][1]
                            )
                        )
                    elif str(type(i)) == "<class 'str'>":
                        choice.append(
                            Element(
                                i
                            )
                        )
        return choice 

    xml_seq_rules = Element('access-list-seq-rule')
    rule10 = (Element('sequence', '00000010'), Element('ace-rule'))
    temp = src_dst_choice('permit', 'ip', {'source-address': '10.0.0.0'}, {'source-wildcard-bits': '0.0.0.255'}, 'destination-any')
    for rule in temp:
        rule10[1].append(rule)
    xml_seq_rules.append(rule10[0])
    xml_seq_rules.append(rule10[1])

    rule20 = (Element('sequence', '00000020'), Element('ace-rule'))
    temp = src_dst_choice('permit', 'ip', {'source-address': '20.0.0.0'}, {'source-wildcard-bits': '0.0.0.255'}, {'destination-address': '0.0.0.0'}, {'destination-wildcard-bits': '255.255.255.255'})
    for rule in temp:
        rule20[1].append(rule)
    xml_seq_rules.append(rule20[0])
    xml_seq_rules.append(rule20[1])

    rule30 = (Element('sequence', '00000030'), Element('ace-rule'))
    temp = src_dst_choice('deny', 'ip', 'source-any', 'destination-any', 'log')
    for rule in temp:
        rule30[1].append(rule)
    xml_seq_rules.append(rule30[0])
    xml_seq_rules.append(rule30[1])

    acl_name = Element('test_acl')
    acl_extended = Element('extended', acl_name, xml_seq_rules, xmlns='http://www.cisco.com/ns/yang/Cisco-IOS-XE-acl')

    xml_ip = Element('ip', acl_extended)
    xml_native = Element('native', xml_ip, xmlns='http://www.cisco.com/ns/yang/Cisco-IOS-XE-native')
    xml_config = Element('config', xml_native)
    xml_string = etree.tostring(xml_config, pretty_print=True).decode()
    print(xml_string)