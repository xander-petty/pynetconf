"""
Netconf testbed
"""

from ncclient import manager 
import lxml.builder
import lxml.etree 
import xmltodict
from lxml.builder import E
import os 

username = 'developer'
password = 'C1sco12345'
ip = 'ios-xe-mgmt.cisco.com'
port = 10000
xml_builder = lxml.builder.ElementMaker()

params = {
    'host': ip,
    'port': port,
    'username': username,
    'password': password,
    'hostkey_verify': False
}
m = manager.connect(**params)

# Verift Connection
m.connected 

# NETCONF Operations
# <get>
# <get-config>
# <edit-config>
# <copy-config>
# <delete-config>
# <commit>
# <lock> / <unlock>
# <close-session>
# <kill-session>

capabilities = list(m.server_capabilities)
# The above code lists all of the models the devices knows. You can view the model by 
# showing the schema as listed below for the IETF IP model
schema = m.get_schema('ietf-ip')
s = m.get_schema('Cisco-IOS-XE-acl')

yang_filter = 'urn:ietf:params:xml:ns:yang'
filter_string = f'{yang_filter}:ietf-interfaces'

# Use XML tools to construct the filter
interface_filter = lxml.etree.tostring(
    xml_builder.filter(
        xml_builder.interfaces(
            xml_builder.interface(
                xml_builder.name(),
                xml_builder.enabled(),
                xml_builder.description()
            ),
            xmlns=filter_string
        )
    ), pretty_print=True
).decode()

# Example of writing the filter 
# yang_filter = 'urn:ietf:params:xml:ns:yang'
# filter_string = f'{yang_filter}:YANG-MODEL-NAME' #Example: ietf-interfaces

# interface_filter = lxml.etree.tostring(
#     xml_builder.filter(
#         xml_builder.CONTAINER( #Example: interfaces
#             xml_builder.LEAF(#Extra filters), #Example: interface
#             xmlns=filter_string
#         )
#     ), pretty_print=True
# ).decode()

netconf_interfaces = m.get_config(source='running', filter=interface_filter).xml
interfaces = xmltodict.parse(netconf_interfaces)['rpc-reply']['data']['interfaces']['interface']

for iface in interfaces:
    print('--------------------------------')
    print('Name: ' + iface['name'])
    print('Enabled: ' + iface['enabled'])
    try:
        print('Description: ' + iface['description'])
    except:
        pass 
    print('--------------------------------')
    print('\n')


yang = 'urn:ietf:params:xml:ns:yang:ietf-routing'
xml = lxml.etree.tostring(
    E(
        'filter',
        E(
            'routing',
            E(
                'routing-instance'
            ),
            xmlns=yang
        )
    ), pretty_print=True
).decode()
test = m.get(filter=xml)
results = xmltodict.parse(test.xml)['rpc-reply']['data']['routing']['routing-instance']
print(results)


# Actual Capabilities for Netconf
netcap = []
cap = m.server_capabilities
for i in cap:
    if str(i).__contains__('urn'):
        if str(i).__contains__('yang:'):
            netcap.append(
                i.split('yang:')[1].split('?')[0]
            )
for yang in netcap:
    print(yang)

# Write models to folder
cwd = os.getcwd()
folder = str(f'{cwd}\\yangmodels')
os.mkdir(folder)
for yang in netcap:
    try:
        schema = str(m.get_schema(yang))
        name = str(f'{yang}.yang')
        write_path = folder + '\\' + name
        file = open(write_path, 'w')
        file.write(schema)
        file.close()
    except:
        pass 


namespace = 'urn:cisco:params:xml:ns:yang:cisco-ethernet'
ip_filter = lxml.etree.tostring(
    E(
        'filter',
        E(
            'ethernet',
            E(
                'duplex'
            ),
            xmlns=namespace
        )
    ), pretty_print=True
).decode()
xml_response = m.get(filter=ip_filter).xml 
dict_response = xmltodict.parse(xml_response)['rpc-reply']['data']
pprint(dict_response)



namespace = 'https://cisco.com/ns/yang/ned/ios'
test_filter = lxml.etree.tostring(
    E(
        'filter',
        E(
            'native',
            E(
                'interface'
            ),
            xmlns=namespace
        ),
        type='subtree'
    ), pretty_print=True
).decode()
xml_response = m.get(filter=test_filter).xml
dict_response = xmltodict.parse(xml_response)['rpc-reply']['data']

# Disconnect
m.close_session()