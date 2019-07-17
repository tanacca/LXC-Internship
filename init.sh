#!/bin/bash
# Init LXC viirtualization space, version 1.

# Warnings:
# --------
# The following script create an unprivileged Fedora30 LXC preconfigured
#+with Virtualization Software (KVM/QEMU) and required Kernel modules.
# Also, it applies a specific LXC profile called "kvm-lxc" on top of 
#+the container and prepare the environment by applying double port 
#+forwarding to enable direct connection to the single VMs.

# Name of the base image and LXC profile that are used
CONTAINER_IMAGE=fedora-30-virt
CONTAINER_PROFILE=kvm-lxc

# Domains configuration (VMs) to import from host
DOMAINS=( centos7.0 fedora30 )
# Domains IPs (required for port forwarding)
IPS=( 192.168.1.10 192.168.1.20 ) 

# Networks configuration to import from host 
NETWORKS=(default)

# Creates temp dir for misc files
TEMPDIR=$(mktemp -d /tmp/XXXXXX)  

# Services to open for each Domain (inside the container)
SERVICES=("SSH" "VNC" "HTTP" "HTTPS")

######################
# SCRIPT STARTS HERE #
######################

# Test command line argument (1 required)
case "$1" in
""                  ) echo "Usage: `basename $0` container-name";
  exit;;
*[!0-9a-zA-Z'-''_']*) echo "Can use only alphanumeric characters plus '-' and '_'"
  exit;;
*                   ) Container_name=$1;;
esac
# End test command line

# Init the LXC user space. Do some preliminary checking
if [[ -e /var/lib/lxd/containers/$Container_name ]]; then
  echo "[*] Graceful deleting existing \"$Container_name\" container"
  lxc stop $Container_name
  sleep 1
  lxc delete --force $Container_name
  sleep 1 
fi
  lxc launch $CONTAINER_IMAGE $Container_name -p $CONTAINER_PROFILE
  sleep 1
# End LXC space init

# Define LXC internal virtual network(s) by importing from host
for Network in ${NETWORKS[*]}; do
  if [[ $(sudo virsh net-list | grep -wo $Network) == "" ]]; then
    echo "vNetwork $Network not found."
    echo "Check your vNetworks names "
    lxc delete --force $Container_name # Force container deletion if 
    sleep 1                            #+anything goes wrong
    exit
  else
    virsh --connect qemu:///system net-dumpxml --network $Network > $TEMPDIR/$Network.xml
    sleep 0.5
    lxc file push $TEMPDIR/$Network.xml $Container_name/$Network.xml
    sleep 1
    lxc exec $Container_name -- sh -c "chown root.root /$Network.xml"
    sleep 0.5
    lxc exec $Container_name -- sh -c "virsh net-destroy $Network"
    sleep 0.5
    lxc exec $Container_name -- sh -c "virsh net-undefine $Network"
    sleep 0.5
    lxc exec $Container_name -- sh -c "virsh net-define --file /$Network.xml"
    sleep 0.5
    lxc exec $Container_name -- sh -c "virsh net-start $Network"
    sleep 0.5
  fi
done
# End define vNetwork(s)

# Define LXC internal Virtual Domains (VMs) by creating a linked clone
#+from the host base images and importing xml conf
cd /var/lib/libvirt/filesystems/
for Domain in ${DOMAINS[*]}; do
  if [[ ! -e $Domain.qcow2 ]]; then
    echo "vDomain $Domain not found"
    echo "Check you vDomains names (HARDCODED)."
    lxc delete --force $Container_name # Force container deletion if 
    sleep 1                            #+anything goes wrong
    exit       
  else
    lxc exec $Container_name -- sh -c "qemu-img create -f qcow2 -b \
      /var/lib/libvirt/filesystems-original-ro/$Domain.qcow2 \
      /var/lib/libvirt/filesystems/$Domain.qcow2"
  fi
  virsh --connect qemu:///system dumpxml --domain $Domain > $TEMPDIR/$Domain.xml
  sleep 0.5
  lxc file push $TEMPDIR/$Domain.xml $Container_name/$Domain.xml
  sleep 1
  # lxc exec $Container_name -- sh -c "edit $Domain.xml bla bla, commit some changes
  lxc exec $Container_name -- sh -c "chown root.root /$Domain.xml"
  lxc exec $Container_name -- sh -c "virsh define /$Domain.xml"
done
# End define LXC internal Virtual Domains

# Remove xml files from inside LXC
lxc exec $Container_name -- sh -c "rm -f *.xml"

# Retrieve LXC container IPv4
Container_IPv4=$(lxc list -c4 --format csv $Container_name | grep 'eth0' | grep -Po '^[^\s]*')
echo "$Container_name $Container_IPv4" >> ~/port-forwardings.txt
echo "+-------------------------------+" >> ~/port-forwardings.txt

# Create forwarding port for VMs services inside LXCs
i=0 # port number counter
j=0 # Domains List index counter for Domain<->IP lists correlation
for Domain in ${DOMAINS[*]}; do
  # Open FORWARD chain from LXC Container to each kvm guest-domain
  lxc exec $Container_name -- sh -c "iptables -I FORWARD -o virbr0 -d ${IPS[$j]} -j ACCEPT"         
  for Service in ${SERVICES[*]}; do
    case $Service in # Assign DPort depending on selected service
    "SSH"  ) DPort=22;;
    "VNC"  ) DPort=5901;;
    "HTTP" ) DPort=80;;
    "HTTPS") DPort=443;;
    esac
    # Calculate the Forward Port starting from 10000 and incrementing by 1
    FPort=$(( 10000 + $i ))
    echo "$Domain $DPort ($Service) = $FPort " >> ~/port-forwardings.txt
    # PortForwarding Inside Container (IPTABLES)  
    lxc exec $Container_name -- sh -c \
      "iptables -t nat -I PREROUTING -p tcp --dport $FPort -j DNAT --to ${IPS[$j]}:$DPort"
    i=$i+1 # increment port counter
  done
  j=$j+1 # increment Domains List index counter
  lxc exec $Container_name -- sh -c "virsh start $Domain" # start Domain
  sleep 0.5
done
echo " " >> ~/port-forwardings.txt

#lxc exec $Container_name -- sh -c "virsh start centos7.0"
#sleep 0.5
#lxc exec $Container_name -- sh -c "virsh start fedora30"
#sleep 0.5
