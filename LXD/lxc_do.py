from pylxd import Client
import time


def init_container(lxc_client, cont_name, cont_image, cont_profile):
    # Define container configuration, return a container object
    config = {'name': cont_name,
              'source': {'type': 'image', 'alias': cont_image},
              'profiles': [cont_profile]}
    try:
        container = lxc_client.containers.create(config, wait=True)
    except Exception as EXC:
        print(f"[-] {EXC}")
        return None
    else:
        print(f"[+] Container \"{container.name}\" created")
        return container


def delete_container(lxc_client, container):
    if container.exists(lxc_client, container.name):
        try:
            container.delete(wait=True)
        except Exception as EXC:
            print(f"[-] {EXC}")
            return False
        else:
            print(f"[+] Container {container.name} deleted")
            return True
    else:
        print(f"[!] Container {container.name} does not exist")
        return False


def start_container(container):
    # Start existing container
    if container.status == 'Running':
        print(f"[!] Container {container.name} is already running")
        return True
    elif container.status == 'Stopped':
        try:
            print(f"[+] Starting Container '{container.name}'...")
            container.start(wait=True)
        except Exception as EXC:
            print(f"[-] {EXC}")
            return False
        else:
            return True
    else:
        print(f"[-] Conainer Status: {container.status}")
        return False


def stop_container(container):
    if container.status == 'Stopped':
        print(f"[!] Container {container.name} is already stopped")
        return True
    elif container.status == 'Running':
        try:
            print(f"[+] Stopping Container '{container.name}'...")
            container.stop(wait=True)
        except Exception as EXC:
            print(f"[-] {EXC}")
            return False
        else:
            return True
    else:
        print(f"[-] Conainer Status: {container.status}")
        return False


def create_snapshot(container):
    # Create a LXC snapshot
    container_name = container.name
    try:
        snapshot = container.snapshots.create(f'{container_name}_backup_{time.ctime()}', wait=True)
    except Exception as EXC:
        print(f"[-] {EXC}")
        return None
    else:
        return snapshot


# def delete_snapshot(container, del_qty):


def send_command(container, command):
    # execute a command inside a container
    # command_xc -> command exit code
    try:
        command_xc, stdout, stderr = list(container.execute(['sh', '-c', command]), wait=True)
    except Exception as EXC:
        print(f"[-] {EXC}")
        return False
    else:
        if command_xc == 0:
            return True
        else:
            print(f"[-] Command execution failed. exit_code={command_xc}")
            return False


if __name__ == "__main__":
    BASE_IMAGE = 'fedora-30-virt'
    PROFILE = 'kvm-lxc'

    lxc_client = Client('/run/lxd.socket')
    containers = lxc_client.containers.all()

    cont_name = input("Container Name: ")
    container = init_container(lxc_client, cont_name, BASE_IMAGE, PROFILE)
    print(start_container(container))
