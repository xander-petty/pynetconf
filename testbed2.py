from ncclient import manager 
from lxml import etree
from lxml.builder import E 
import xmltodict
import json 
from getpass import getpass 
from pprint import pprint 

def netconf_xmljson(xml_data, container, leaf):
    try:
        xml_dict = xmltodict.parse(xml_data)['rpc-reply']['data'][container][leaf]
        json_out = json.loads(json.dumps(xml_dict))
        return json_out
    except:
        pass 

# There's a way to dynamically add variables to a function.. just don't remember how.
# Will do this later to have the ability to further filter 
def generate_netconf_xml(namespace, container, leaf):
    netconf_filter = etree.tostring(
        E(
            'filter',
            E(
                container,
                E(
                    leaf
                ),
                xmlns=namespace
            )
        ), pretty_print=True
    ).decode()
    return netconf_filter

def lazy_netconf(nc_manager, namespace, container, leaf):
    xml_filter = generate_netconf_xml(namespace, container, leaf)
    output = nc_manager.get(filter=xml_filter).xml
    json_data = netconf_xmljson(output, container, leaf)
    pprint(json_data)

if __name__ == '__main__':
    # username = input('Username: ')
    # password = getpass()
    # ip = '10.11.255.133'
    # port = 830
    ip =  'ios-xe-mgmt.cisco.com'
    username = 'developer'
    password = 'C1sco12345'
    port = 10000
    params = {
        'host': ip,
        'username': username,
        'password': password,
        'port': port,
        'hostkey_verify': False
    }
    m = manager.connect(**params)

    # Testing Operational CDP
    namespace = 'http://cisco.com/ns/yang/Cisco-IOS-XE-cdp-oper'
    container = 'cdp-neighbor-details'
    leaf = 'cdp-neighbor-detail'
    lazy_netconf(m, namespace, container, leaf)

    # Testing Operational ACL
    namespace = 'http://cisco.com/ns/yang/Cisco-IOS-XE-acl-oper'
    container = 'access-lists'
    leaf = 'access-list'
    lazy_netconf(m, namespace, container, leaf)

    # Testing ACL Config
    namespace = 'http://cisco.com/ns/yang/Cisco-IOS-XE-acl'
    container = 'extended'
    leaf = 'access-list-seq-rule'
    lazy_netconf(m, namespace, container, leaf)

    # Testing Route Map Config
    namespace = 'http://cisco.com/ns/yang/Cisco-IOS-XE-native'
    container ='route-map'
    leaf = 'name'
    lazy_netconf(m, namespace, container, leaf)

    # Testing Routing
    namespace = 'urn:ietf:params:xml:ns:yang:ietf-routing'
    container = 'routing'
    leaf = 'routing-instance'
    lazy_netconf(m, namespace, container, leaf)

    # Testing Routing
    namespace = 'urn:ietf:params:xml:ns:yang:ietf-routing'
    container = 'routing-state'
    leaf = 'routing-instance'
    lazy_netconf(m, namespace, container, leaf)

    # Testing Routing
    namespace = 'http://openconfig.net/yang/local-routing'
    container = 'local-routes'
    leaf = 'config'
    lazy_netconf(m, namespace, container, leaf)

    # ARP Test
    namespace = 'http://cisco.com/ns/yang/Cisco-IOS-XE-arp-oper'
    container = 'arp-data'
    leaf = 'arp-vrf'
    lazy_netconf(m, namespace, container, leaf)

    # Testing Operational Interfaces
    namespace = 'http://cisco.com/ns/yang/Cisco-IOS-XE-interfaces-oper'
    container = 'interfaces'
    leaf = 'interface'
    lazy_netconf(m, namespace, container, leaf)

    # Testing Config of ACL
    namespace = 'http://cisco.com/ns/yang/Cisco-IOS-XE-acl'
    xml_config = etree.tostring(
        E(
            'config',
            E(
                'extended',
                'test_acl',
                E(
                    'access-list-seq-rule',
                    E(
                        'sequence',
                        '10'
                    ), # Seq 
                    E(
                        'ace-rule',
                        E(
                            'action',
                            'permit'
                        ), # Action 
                        E(
                            'protocol',
                            'ip'
                        ), # Protocol match 
                        E(
                            'source-choice',
                            E(
                                'any'
                            ) # Src Match 
                        ), # Source Choice 
                        E(
                            'destination-choice',
                            E(
                                'any'
                            ) # Dest Match
                        ) # Dest Choice 
                    ) # Rule
                ), # Seq Rule
                xmlns=namespace
            ) #ACL Name
        ), pretty_print=True
    ).decode()
    output = m.edit_config(xml_config)

    # Testing Loopback config
    namespace = 'urn:ietf:params:xml:ns:yang:ietf-interfaces'
    xml_config = etree.tostring(
        E(
            'config',
            E(
                'interfaces',
                E(
                    'interface',
                    E(
                        'name',
                        'Loopback 62'
                    ),
                    E(
                        'enabled',
                        'true'
                    ),
                    E(
                        'description',
                        'Netconf configured Loopback'
                    )
                ),
                xmlns=namespace
            )
        ), pretty_print=True
    ).decode()
    output = m.edit_config(xml_config)

    namespace = 'http://cisco.com/ns/yang/Cisco-IOS-XE-native'
    xml_filter = etree.tostring(
        E(
            'filter',
            E(
                'native',
                E(
                    'interface',
                    E(
                        'Ethernet'
                    )
                ),
                xmlns=namespace
            )
        ), pretty_print=True
    ).decode()
    xml_response = m.get(filter=xml_filter).xml
    dict_response = xmltodict.parse(xml_response)['rpc-reply']['data']['native']['interface']['Ethernet']
    json_response = json.loads(json.dumps(dict_response))
    pprint(json_response)

    # Testing ACL Config
    namespace = 'http://cisco.com/ns/yang/Cisco-IOS-XE-acl'
    xml_config = etree.tostring(
        E(
            'config',
            E(
                'standard',
                '''
                <name xmlns:ios-types="http://cisco.com/ns/yang/Cisco-IOS-XE-types">
                    '12'
                </name>
                ''',
                E(
                    'access-list-seq-rule',
                    E(
                        'sequence',
                        '10'
                    ),
                    E(
                        'permit',
                        E(
                            'std-ace',
                            E(
                                'any'
                            )
                        )
                    )
                ),
                xmlns=namespace
            )
        ), pretty_print=True
    ).decode()
    m.edit_config(xml_config).xml


    namespace = 'http://cisco.com/ns/yang/Cisco-IOS-XE-acl'
    xml_config = etree.tostring(
        E(
            'config',
            E(
                'native',
                E(
                    'ip',
                    E(
                        'access-list',
                        E(
                            'standard',
                            E(
                                'name',
                                '12'
                            ),
                            E(
                                'access-list-seq-rule',
                                E(
                                    'sequence',
                                    '00000010'
                                ),
                                E(
                                    'permit',
                                    E(
                                        'std-ace',
                                        E(
                                            'any'
                                        )
                                    )
                                )
                            ),
                            xmlns=namespace
                        )
                    )
                ),
                xmlns='http://cisco.com/ns/yang/Cisco-IOS-XE-native'
            )
        ), pretty_print=True
    ).decode()
    m.edit_config(xml_config)

    native_ns = 'http://cisco.com/ns/yang/Cisco-IOS-XE-native'
    namespace = 'http://cisco.com/ns/yang/Cisco-IOS-XE-acl'
    xml_filter = etree.tostring(
        E(
            'filter',
            E(
                'native',
                E(
                    'ip',
                    E(
                        'access-list',
                        E(
                            'standard',
                            E(
                                'name',
                                '12'
                            ),
                            xmlns=namespace
                        )
                    )
                ),
                xmlns=native_ns
            )
        ), pretty_print=True
    ).decode()
    output = m.get_config(source='candidate', filter=xml_filter).xml

