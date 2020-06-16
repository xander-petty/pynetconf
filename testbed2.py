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

if __name__ == '__main__':
    username = input('Username: ')
    password = getpass()
    ip = '10.11.255.133'
    port = 830
    params = {
        'host': ip,
        'username': username,
        'password': password,
        'port': port
    }
    m = manager(**params)

    # Testing shorthand netconf 
    namespace = 'http://cisco.com/ns/yang/Cisco-IOS-XE-cdp-oper'
    container = 'cdp-neighbor-details'
    leaf = 'cdp-neighbor-detail'