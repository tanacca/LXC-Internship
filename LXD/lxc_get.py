import os
from pylxd import Client
import time


def memory_usage(container):
    # Retrieve LXC memory usage in %
    memory_limit = int(container.expanded_config.get('limits.memory'))
    memory_usage = int(container.state().memory['usage'])
    return f"{((memory_usage / memory_limit) * 100):.2f} %"


def ip_address(container):
    # Retrieve LXC ip address
    try:
        ip_address = container.state().network['eth0']['addresses'][0]['address']
        ip_mask = container.state().network['eth0']['addresses'][0]['netmask']
    except TypeError:
        return None, None
    else:
        return ip_address, ip_mask


def disk_usage(container):
    # Retrieve disk usage in %
    try:
        hd_current_usg = int(container.state().disk['root']['usage'])
    except TypeError:
        hd_quota = int(container.expanded_devices['root']['size'])
        return "<UNKNOWN>"
    else:
        hd_quota = int(container.expanded_devices['root']['size'])
        return f"{((hd_current_usg / hd_quota) * 100):.2f} %"


if __name__ == "__main__":
    lxc_client = Client('/run/lxd.socket')
    while(True):
        containers = lxc_client.containers.all()
        os.system('clear')
        for container in containers:
            ip, mask = ip_address(container)
            print(f"""
         [+] Container name: {container.name}
             Status        : {container.status}
             IP address    : {ip}/{mask}
             Base ProcessID: {container.config['volatile.idmap.base']}
             HD Quota Usage: {disk_usage(container)} (Tot: 10GB)
             Memory usage  : {memory_usage(container)} (Tot: 4GB)
             Tot Snapshots : {len(container.snapshots.all())}
                    """)
            # time in seconds
        time.sleep(1)
