from xml.dom import minidom
import xml.etree.ElementTree as ET
from domains import *
from menu import menuLayout


class networks_submenu_desc:
    title = "Main Menu > vNetworks Menu"
    options = ['Return', 'List Virtual Networks', 'Assign Network to Guest VM',
               'SubChoice 3', 'SubChoice 4']
    ask = "Please enter your choice (0-3): "


def get_network_details(conn, network_choice):
    networks = conn.listNetworks()
    if network_choice not in networks:
        print(f" [!] Error: network '{network_choice}' doesn't exist")
        return
    network = conn.networkLookupByName(network_choice)
    root = ET.fromstring(network.XMLDesc(0))
    net_dict = {}
    for child in root:
        net_dict[child.tag] = child.attrib
    net_desc = (f"""
  Name            : {network_choice}
  Gateway IP add  : {net_dict['ip']['address']}
  Netmask         : {net_dict['ip']['netmask']}
  Gateway MAC add : {net_dict['mac']['address']}""")
    if 'forward' not in net_dict.keys():
        net_desc += (f"""\n  Forward         : False
  """)
    else:
        net_desc += (f"""\n  Forward         : True
  Forward Mode    : {net_dict['forward']['mode']}
  """)
    print(net_desc)
    return


def get_dom_current_network(conn, dom_name):
    dom = conn.lookupByName(dom_name)
#   dom_xml is an XML object which represent the domain
    dom_xml = minidom.parseString(dom.XMLDesc())
    interfaces = dom_xml.getElementsByTagName('interface')
    for interface in interfaces:
        if interface.getAttribute('type') == 'network':
            int_nodes = interface.childNodes
            for int_node in int_nodes:
                if int_node.nodeName == 'source':
                    return int_node.getAttribute('network')


def change_host_network(conn, dom_name, new_network):
    networks = conn.listNetworks()
    current_network = get_dom_current_network(conn, dom_name)
    if new_network not in networks:
        print(f" [!] Error: network '{new_network}' doesn't exist")
        return
    elif new_network == current_network:
        print(f" [!] Error: network '{new_network}' is the attached network")
        return

    dom = conn.lookupByName(dom_name)
    dom_raw_xml = dom.XMLDesc()
    net_raw_xml = dom_raw_xml[dom_raw_xml.find("<interface type='network'>") - 4: dom_raw_xml.find("</interface>") + 12]
    new_net_raw_xml = net_raw_xml.replace(
        f"<source network='{current_network}'",
        f"<source network='{new_network}'")
    dom.updateDeviceFlags(new_net_raw_xml)
    print(f" [+] Host [{dom_name}] succesfully attached to '{new_network}' network")
    return


def network_submenu(conn, uri):
    while(True):
        opt = menuLayout(networks_submenu_desc, uri)
        if int(opt) == 0:
            break
        if int(opt) == 1:
            networks_list = conn.listNetworks()
            print("\n Virtual Networks:")
            for network in networks_list:
                print(f" - {network}")
            network_choice = input("\n [?] Select which network to get details (leave blank to return): ")
            if network_choice == "":
                continue
            else:
                get_network_details(conn, network_choice)
                input("\n Press <ENTER> to continue...")
        if int(opt) == 2:
            print()
            list_domains(conn)  # <-- print/list domains
            domain_choice = input("\n [?] Select which host to change network (leave blank to return): ")
            if domain_choice == "":
                continue
            else:
                if domain_choice not in get_domains(conn):  # check if domain exist
                    print(f" [!] Error: [{domain_choice}] is not a registered Guest VM")
                    input(f"\n Press <ENTER> to continue...")
                    continue
                else:

                    print(f" [+] The Guest [{domain_choice}] is currently connected to \
                        '{get_dom_current_network(conn, domain_choice)}' network")
                    networks_list = conn.listNetworks()
                    print("\n Virtual Networks:")
                    for network in networks_list:
                        print(f" - {network}")
                    network_choice = input("\n [?] Select the new network (leave blank to return): ")
                    if network_choice == "":
                        continue
                    else:
                        change_host_network(conn, domain_choice, network_choice)
                        input(f"\n Press <ENTER> to continue...")
                        continue
            continue
        if int(opt) == 3:
            continue
        if int(opt) == 4:
            continue


if __name__ == '__main__':
    network_submenu(connect_to_libvirtHost(uri))
