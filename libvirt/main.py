import sys
import libvirt
from host import host_submenu
from domains import domains_submenu
from networks import network_submenu
from menu import menuLayout

# uri = "qemu:///system"
# uri = "qemu+ssh://root@10.0.0.210/system?socket=/var/run/libvirt/libvirt-sock"


class main_menu_desc:
    title = "Main Menu"
    options = ['Exit', 'Host Menu', 'Guest VMs Menu', 'vNetworks Menu']
    ask = "Please enter your choice (0-3): "


def connect_to_libvirtHost(uri="qemu:///system"):
    # for SSH connectrion to libvirt daemon
    conn = libvirt.open(uri)
    if conn is None:
        print(f"Failed to open connection to {uri}", file=sys.stderr)
        exit(1)
    return conn

'''
def connect_to_libvirtHost(uri):
    # for authenticated TCP connection to libvirt daemon
    SASL_USER = "virt-user"
    SASL_PASSWD = "virtpassword"

    def request_cred(credentials, user_data):
        for credential in credentials:
            if credential[0] == libvirt.VIR_CRED_AUTHNAME:
                credential[4] = SASL_USER
            elif credential[0] == libvirt.VIR_CRED_PASSPHRASE:
                credential[4] = SASL_PASSWD
        return 0

    auth = [[libvirt.VIR_CRED_AUTHNAME, libvirt.VIR_CRED_PASSPHRASE], request_cred, None]

#    conn = libvirt.open(uri)
    conn = libvirt.openAuth(uri, auth, 0)
    if conn is None:
        print(f"Failed to open connection to {uri}", file=sys.stderr)
        exit(1)
    return conn
'''


def main(uri):
    opt = -1
    newConn = connect_to_libvirtHost(uri)
    while(True):  # main menu loop
        opt = menuLayout(main_menu_desc, uri)
        if int(opt) == 0:
            print("\n Thanks for using the console. Goodbye\n")
            newConn.close()
            sys.exit(0)
        if int(opt) == 1:
            host_submenu(newConn, uri)
            continue
        if int(opt) == 2:
            domains_submenu(newConn, uri)
            continue
        if int(opt) == 3:
            network_submenu(newConn, uri)
            continue


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(" [!] ERROR: wrong usage.\n [+] Try 'main.py <rempote-ip> <port-number>'")
        sys.exit(1)

    remoteIp = sys.argv[1]
    portNumber = sys.argv[2]
    # URI = f"qemu+tcp://{remoteIp}:{portNumber}/system"
    URI = f"qemu+ssh://root@{remoteIp}:{portNumber}/system?socket=/var/run/libvirt/libvirt-sock"
    main(URI)
