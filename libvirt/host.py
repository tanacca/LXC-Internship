import os
from menu import menuLayout


class host_submenu_desc:
    title = "Main Menu > Host Menu"
    options = ['Return', 'Show Host Info']
    ask = "Please enter your choice (0-1): "


def show_host_info(conn):  # print some host useful information
    os.system("clear")
    hostname = conn.getHostname()
    vcpus = conn.getMaxVcpus(None)
    nodeinfo = conn.getInfo()
    print(f"""\n KVM Host Info\n{'='*80}
 Main Menu > Host Menu > Host Info\n{'-'*80}
 - Hostname: {hostname}
 - Maximum support virtual CPUs: {str(vcpus)}
 - Model: {str(nodeinfo[0])}
 - Memory size: {str(nodeinfo[1])}MB
 - Number of CPUs: {str(nodeinfo[2])}
 - MHz CPUs: {str(nodeinfo[3])}\n{'='*80}""")
# - Number of NUMA nodes: {str(nodeinfo[4])}
# - Number of CPU sockets: {str(nodeinfo[5])}
# - Number of CPU cores per socket: {str(nodeinfo[6])}
# - Number of CPU threads per core: {str(nodeinfo[7])}
    pass


def host_submenu(conn, uri):
    while(True):
        opt = menuLayout(host_submenu_desc, uri)
        if int(opt) == 0:
            break
        if int(opt) == 1:
            show_host_info(conn)
            input("\n Press <ENTER> to continue...")
