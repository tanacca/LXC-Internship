import sys
import time
from menu import menuLayout
import os

from multiprocessing import Process
from subprocess import call


class domains_submenu_desc:
    title = 'Main Menu > Guest VMs Menu'
    options = ['Return', 'List Guest VMs', 'Start/Stop Guest VM', 'Ping Guest VM ', 'Connect To Guest VM']
    ask = "Please enter your choice (0-4): "


class domains_subsubmenu_desc:
    def __init__(self, domChoice):
        self.title = 'Main Menu > Guest VMs Menu > Guest: [' + domChoice + ']'

    options = ['Return', 'Remote Console to Guest VM', 'Remote Screen to Guest VM',
               'Change to anothe Guest VM', 'Subchoice 4']

    ask = "Please enter your choice (0-3): "


def get_domains(conn):
    # main function to get domains list (active/non-active)
    # is ok to use domain name as domain unique ID
    domains = {}
    activeDomains = conn.listAllDomains(1)      # <-- 1 = active domains
    if len(activeDomains) != 0:
        for activeDomain in activeDomains:
            domains[activeDomain.name()] = True

    inactiveDomains = conn.listAllDomains(2)    # <-- 2 = inactive domains
    if len(inactiveDomains) != 0:
        for inactiveDomain in inactiveDomains:
            domains[inactiveDomain.name()] = False
    return domains


def list_domains(conn):
    domains = get_domains(conn)
    domainList = ""
    for key, val in domains.items():
        if val:
            print(f" [+] The Guest VM [{key}] is UP!")
        else:
            print(f" [-] The Guest VM [{key}] is DOWN!")
    return domainList


def startstop_Domain(conn, domain_name):
    domains = get_domains(conn)
    if domain_name not in domains:
        print(f" [!] Error: [{domain_name}] is not a registered Guest VM")
        return
    else:
        dom = conn.lookupByName(domain_name)
        if not domains[domain_name]:  # example: 'kali':True --> switched on
            if dom.create() < 0:
                print(f" [!] Error: cannot boot guest domain {domain_name}. \n {sys.stderr}")
                return
            print(f" [*] Booting {domain_name}...")
            time.sleep(1)
            print(f" [+] Guest VM {domain_name} SWITCHED ON.")
            return
        else:
            dom.shutdown()
            print(f" [*] Powering Off {domain_name}...")
            time.sleep(1)
            print(f" [-] Guest VM {domain_name} SWITCHED OFF.")
            return


def connect_to_domain(conn, domain_name):
    domains = get_domains(conn)
    if domain_name not in domains:
        print(f" [!] Error: [{domain_name}] is not a registered Guest VM")
        return False
    else:
        if not domains[domain_name]:  # check if is off, example: 'kali':True --> switched on
            print(f" [-] Guest VM [{domain_name}] is down. Power it ON before opening the VM's menu.")
            return False
        else:
            return True


def domains_submenu(conn, uri):
    while(True):
        opt = menuLayout(domains_submenu_desc, uri)
        if int(opt) == 0:
            break
        if int(opt) == 1:
            print()
            list_domains(conn)
            input("\n Press <ENTER> to continue...")
            continue
        if int(opt) == 2:
            domain_choice = input("\n [?] Select a Guest VM to start/stop (leave blank to return): ")
            if domain_choice == "":
                continue
            else:
                startstop_Domain(conn, domain_choice)
                input("\n Press <ENTER> to continue...")
                continue
        if int(opt) == 3:
            continue
        if int(opt) == 4:
            domain_choice = input("\n [?] Select a Guest VM to connect to (leave blank to return): ")
            if domain_choice == "":
                continue
            else:
                if not connect_to_domain(conn, domain_choice):
                    input("\n Press <ENTER> to continue...")
                    continue
                else:
                    while(True):
                        opt = menuLayout(domains_subsubmenu_desc(domain_choice), uri)
                        if int(opt) == 0:
                            break
                        if int(opt) == 1:
                            call([f'{sys.path[0]}/console_exe.py', uri, domain_choice])
                            continue
                        if int(opt) == 2:
                            portNumber = {'centos7.0': '5901', 'fedora30': '5902',
                                          'kali': '5903'}
                            p = Process(target=call,
                                        args=(['remote-viewer', f'spice://localhost:{portNumber[domain_choice]}'], ))
                            p.start()
                            #p.join()
                            #call(['remote-viewer', f'spice://localhost:{portNumber[domain_choice]}'])
                            continue
                        if int(opt) == 3:
                            domain_choice_new = input("\n [?] Select a Guest VM to connect to (leave blank to return): ")
                            if domain_choice_new == "":
                                continue
                            else:
                                if not connect_to_domain(conn, domain_choice):
                                    input("\n Press <ENTER> to continue...")
                                    continue
                                else:
                                    domain_choice = domain_choice_new
                                    continue
                        if int(opt) == 4:
                            continue


""" Define what to get
0  = ALL
1  = VIR_CONNECT_LIST_DOMAINS_ACTIVE
2  = VIR_CONNECT_LIST_DOMAINS_INACTIVE
3  = VIR_CONNECT_LIST_DOMAINS_PERSISTENT
4  = VIR_CONNECT_LIST_DOMAINS_TRANSIENT
5  = VIR_CONNECT_LIST_DOMAINS_RUNNING
6  = VIR_CONNECT_LIST_DOMAINS_PAUSED
7  = VIR_CONNECT_LIST_DOMAINS_SHUTOFF
8  = VIR_CONNECT_LIST_DOMAINS_OTHER
9  = VIR_CONNECT_LIST_DOMAINS_MANAGEDSAVE
10 = VIR_CONNECT_LIST_DOMAINS_NO_MANAGEDSAVE
11 = VIR_CONNECT_LIST_DOMAINS_AUTOSTART
12 = VIR_CONNECT_LIST_DOMAINS_NO_AUTOSTART
13 = VIR_CONNECT_LIST_DOMAINS_HAS_SNAPSHOT
14 = VIR_CONNECT_LIST_DOMAINS_NO_SNAPSHOT
"""