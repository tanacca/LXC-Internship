#!/bin/python3
# Example-1.py
# consolecallback - provide a persistent console that survives guest reboots
from __future__ import print_function
import sys
import os
import logging
import libvirt
import tty
import termios
import atexit


def reset_term():
    termios.tcsetattr(0, termios.TCSADRAIN, attrs)


def error_handler(unused, error):
    # The console stream errors on VM shutdown; we don't care
    if (error[0] == libvirt.VIR_ERR_RPC and
            error[1] == libvirt.VIR_FROM_STREAMS):
        return
    logging.warn(error)


class Console(object):
    # for SSH connectrion to libvirt daemon
    def __init__(self, uri, dom_name):
        self.uri = uri
        self.dom_name = dom_name
        self.connection = libvirt.open(uri)
        self.domain = self.connection.lookupByName(dom_name)
        self.state = self.domain.state(0)
        self.connection.domainEventRegister(lifecycle_callback, self)
        self.stream = None
        self.run_console = True
        logging.info("%s initial state %d, reason %d",
                     self.dom_name, self.state[0], self.state[1])

'''
class Console(object):
    # for authenticated TCP connection to libvirt daemon
    def __init__(self, uri, dom_name):
        SASL_USER = "virt-user"         # hardcoded. Need to change it and parametarize
        SASL_PASSWD = "virtpassword"    # both

        def request_cred(credentials, user_data):
            for credential in credentials:
                if credential[0] == libvirt.VIR_CRED_AUTHNAME:
                    credential[4] = SASL_USER
                elif credential[0] == libvirt.VIR_CRED_PASSPHRASE:
                    credential[4] = SASL_PASSWD
            return 0

        self.auth = [[libvirt.VIR_CRED_AUTHNAME, libvirt.VIR_CRED_PASSPHRASE], request_cred, None]
        self.dom_name = dom_name
        self.connection = libvirt.openAuth(uri, self.auth, 0)
        self.domain = self.connection.lookupByName(dom_name)
        self.state = self.domain.state(0)
        self.connection.domainEventRegister(lifecycle_callback, self)
        self.stream = None
        self.run_console = True
        logging.info("%s initial state %d, reason %d",
                     self.dom_name, self.state[0], self.state[1])
'''

def check_console(console):
    if (console.state[0] == libvirt.VIR_DOMAIN_RUNNING or
            console.state[0] == libvirt.VIR_DOMAIN_PAUSED):
        if console.stream is None:
            console.stream = console.connection.newStream(libvirt.VIR_STREAM_NONBLOCK)
            console.domain.openConsole(None, console.stream, 0)
            console.stream.eventAddCallback(libvirt.VIR_STREAM_EVENT_READABLE, stream_callback, console)
    else:
        if console.stream:
            console.stream.eventRemoveCallback()
            console.stream = None
    return console.run_console


def stdin_callback(watch, fd, events, console):
    readbuf = os.read(fd, 1024)
    if readbuf.startswith(b"\x1d"):
        console.run_console = False
        return
    if console.stream:
        console.stream.send(readbuf)


def stream_callback(stream, events, console):
    try:
        received_data = console.stream.recv(1024)
    except:
        return
    os.write(0, received_data)


def lifecycle_callback(connection, domain, event, detail, console):
    console.state = console.domain.state(0)
    logging.info("%s transitioned to state %d, reason %d",
                 console.dom_name, console.state[0], console.state[1])


'''
# main
if len(sys.argv) != 3:
    print("Usage:", sys.argv[0], "URI UUID")
    print("for example:", sys.argv[0], "'qemu:///system' 'kali'")
    sys.exit(1)
'''
uri = sys.argv[1]
dom_name = sys.argv[2]
print("Escape character is ^]")
logging.basicConfig(filename='msg.log', level=logging.DEBUG)
logging.info("URI: %s", uri)
logging.info("VM Name: %s", dom_name)

libvirt.virEventRegisterDefaultImpl()
libvirt.registerErrorHandler(error_handler, None)

atexit.register(reset_term)
global attrs
attrs = termios.tcgetattr(0)
tty.setraw(0)

console = Console(uri, dom_name)
console.stdin_watch = libvirt.virEventAddHandle(0, libvirt.VIR_EVENT_HANDLE_READABLE, stdin_callback, console)

while check_console(console):
    libvirt.virEventRunDefaultImpl()
