import sys
import os
import time

from pylxd import Client
import libvirt


import lxc_do
import lxc_get
import libvirt_conn


def init_lxcKvm(lxc_client, cont_name):
    BASE_IMAGE = 'fedora-30-virt'
    PROFILE = 'kvm-lxc'

    # Networks to define. Need XML file
    NETWORKS = ['default']
    # Domains to define. Need XML file
    DOMAINS = ['centos7.0', 'fedora30']
    DOMAINS_IPS = ['192.168.1.10', '192.168.1.20']
    SERVICES = ['SSH', 'VNC', 'HTTP', 'HTTPS']

    # check if container name already exists. I it does exist,
    # +try first to stop the container, and the delete it
    if os.path.exists(f'/var/lib/lxd/containers/{cont_name}'):
        print(f"[!] Container '{cont_name}' already exist. Deleting container...")
        container = lxc_client.containers.get(cont_name)
        if lxc_do.stop_container(container):
            lxc_do.delete_container(lxc_client, container)
        else:
            print(f"[-] Error: couldn't stop the existing '{cont_name}' container. Exiting...")
            sys.exit(1)

    # Define and Create Container object in container
    container = lxc_do.init_container(lxc_client, cont_name, BASE_IMAGE, PROFILE)

    # Start the container
    if not lxc_do.start_container(container):
        print(f"[-] Error: couldn't start '{cont_name}' container.")
        sys.exit(1)
    time.sleep(5)

    lxc_do.send_command(container, 'saslpasswd2 -a libvirt -c virt-user -f /etc/libvirt/passwd.db -p <<< virtpassword')


    # connect to the container libvirt daemon and do preliminary operations
    ip, mask = lxc_get.ip_address(container)
    cont_libvirt_uri = f'qemu+tcp://{ip}:16509/system'
    cont_libvirt_conn = libvirt_conn.connect_to_libvirtHost(cont_libvirt_uri)

    # start defining networks
    for network in NETWORKS:
        if not os.path.exists(f'XMLs_NETWORKS/{network}.xml'):
            print(f"[!] XML file descriptor for '{network}' does not exist.")
            print(f"[-] Deleting container '{cont_name}'...")
            lxc_do.stop_container(container)
            lxc_do.delete_container(lxc_client, container)
            sys.exit(1)
        else:
            XML_net = open(f'XMLs_NETWORKS/{network}.xml', 'r')
            # str_XML_net is a string which represent the XML network file
            str_XML_net = XML_net.read()
            try:
                cont_libvirt_conn.networkCreateXML(str_XML_net)
            except Exception as EXC:
                print(f"[!] {EXC}")
                input()
                lxc_do.send_command(container, "virsh net-destroy {network}")
                input()
                cont_libvirt_conn.networkCreateXML(str_XML_net)
                input()
                lxc_do.send_command(container, "virsh net-autostart {network}")
                input()
            else:
                cont_libvirt_conn.networkCreateXML(str_XML_net)
                lxc_do.send_command(container, "virsh net-autostart {network}")
        print(f"[+] Network '{network}' defined in '{container}'")

##### TODOOOOOOOOOOO ########
