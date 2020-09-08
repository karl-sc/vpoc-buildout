ssh_host = "1.1.1.1"
username = "root"
password = "password"

#vim-cmd vmsvc/getallvms | grep MASTER-DC2-svr
import paramiko
import traceback

class AllowAllKeys(paramiko.MissingHostKeyPolicy):
    def missing_host_key(self, client, hostname, key):
        return

vpoc_object = {
    'config' : 
        {
            'servers' :
            {
                'br1-desktop' : 
                {
                    'vnc_port' : "5961"
                },
                'br2-desktop' : 
                {
                    'vnc_port' : "5962"
                },
                'br3-desktop' : 
                {
                    'vnc_port' : "5963"
                },
                'dc1-svr' : 
                {
                    'vnc_port' : "5965"
                },
                'dc2-svr' : 
                {
                    'vnc_port' : "5966"
                },
                'dc3-svr' : 
                {
                    'vnc_port' : "5967"
                },
            },
            'ions' :
            {
                'br1-ion' : 
                {
                    'vnc_port' : "5971"
                },
                'br2-ion' : 
                {
                    'vnc_port' : "5972"
                },
                'br3-ion' : 
                {
                    'vnc_port' : "5973"
                },
                'dc1-ion' : 
                {
                    'vnc_port' : "5975"
                },
                'dc2-ion' : 
                {
                    'vnc_port' : "5976"
                },
                'dc3-ion' : 
                {
                    'vnc_port' : "5977"
                },
            },
            "name_prefix" : "POC2"
        }
    
}




debug_flag = True

def debug_print(printed_text):
    global debug_flag
    if debug_flag:
        print("COMMAND:",printed_text)
    return

def run_ssh_command(cmd_to_execute):
    global ssh_host, username, password
    ssh=paramiko.SSHClient()
    ssh.set_missing_host_key_policy(AllowAllKeys())
    retry = True
    while retry:
        try:
            ssh.connect(ssh_host, username=username, password=password)
            retry = False
        except Exception as e:
            print("SSH Error!")
            print(traceback.format_exc())
            user_input = ""
            while user_input != "y" and user_input != "n":
                user_input = input("Try SSH Connection again (y/n) ? " )
            if user_input == "n":
                retry = False
                return [ None, None]
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute)
    ssh.close()
    debug_print(cmd_to_execute)
    return [ ssh_stderr, ssh_stdout ]


def clone_server(name_prefix, server_name, vnc_port): ###NOTE this also clones desktops
    new_server_name = name_prefix + "-" + server_name
    cmd_list = [] 
    cmd_list.append(    "cd /vmfs/volumes/ssd1/"                + ";")
    cmd_list.append(    "./clone.sh IMAGE-lubuntu " + new_server_name        + ";")
    cmd_list.append(    "sed -i 's/vnc.port.*./vnc.port = \"" + vnc_port + "\"/g' " + new_server_name + "/IMAGE-lubuntu.vmx"     + ";")
    cmd_to_execute = "".join(cmd_list)
    #print ("COMMAND:",cmd_to_execute)
    
    return run_ssh_command(cmd_to_execute)

def clone_ions(name_prefix, ion_name, vnc_port):
    new_ion_name = name_prefix + "-" + ion_name
    cmd_list = [] 
    cmd_list.append(    "cd /vmfs/volumes/ssd1/"                + ";")
    cmd_list.append(    "./clone.sh IMAGE-3102v " + new_ion_name        + ";")
    cmd_list.append(    "sed -i 's/vnc.port.*./vnc.port = \"" + vnc_port + "\"/g' " + new_ion_name + "/IMAGE-3102v.vmx"     + ";")
    cmd_to_execute = "".join(cmd_list)
    #print ("COMMAND:",cmd_to_execute)
    
    return run_ssh_command(cmd_to_execute)


def create_vmware_vswitch_networking(name_prefix):
    cmd_list = [] 
    cmd_list.append(    "esxcli network vswitch standard add --vswitch-name=" + name_prefix + "-vswitch-mpls"                + ";")
    cmd_list.append(    "esxcli network vswitch standard add --vswitch-name=" + name_prefix + "-vswitch-lan"                + ";")
    cmd_list.append(    "esxcli network vswitch standard add --vswitch-name=" + name_prefix + "-vswitch-inet"                + ";")
    
    cmd_list.append(    "esxcli network vswitch standard policy security set -m=true -f=true -p=true -v " + name_prefix + "-vswitch-mpls"                + ";")
    cmd_list.append(    "esxcli network vswitch standard policy security set -m=true -f=true -p=true -v " + name_prefix + "-vswitch-lan"                + ";")
    cmd_list.append(    "esxcli network vswitch standard policy security set -m=true -f=true -p=true -v " + name_prefix + "-vswitch-inet"                + ";")
    
    cmd_to_execute = "".join(cmd_list)
    #print ("COMMAND:",cmd_to_execute)
    return run_ssh_command(cmd_to_execute)

def create_vmware_pg_networking(name_prefix):
    cmd_list = [] 
    cmd_list.append(    "esxcli network vswitch standard portgroup add -v " + name_prefix + "-vswitch-mpls -p " + name_prefix + "-pg-mpls-trunk"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup set -p " + name_prefix + "-pg-mpls-trunk --vlan-id 4095"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup add -v " + name_prefix + "-vswitch-mpls -p " + name_prefix + "-dc-mpls-link"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup set -p " + name_prefix + "-dc-mpls-link --vlan-id 57"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup add -v " + name_prefix + "-vswitch-inet -p " + name_prefix + "-pg-inet-trunk"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup set -p " + name_prefix + "-pg-inet-trunk --vlan-id 4095"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup add -v " + name_prefix + "-vswitch-lan -p " + name_prefix + "-lan-trunk"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup set -p " + name_prefix + "-lan-trunk --vlan-id 4095"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup add -v " + name_prefix + "-vswitch-lan -p " + name_prefix + "-mgmt"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup set -p " + name_prefix + "-mgmt --vlan-id 5"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup add -v " + name_prefix + "-vswitch-lan -p " + name_prefix + "-br1-lan1"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup set -p " + name_prefix + "-br1-lan1 --vlan-id 11"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup add -v " + name_prefix + "-vswitch-lan -p " + name_prefix + "-br1-lan2"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup set -p " + name_prefix + "-br1-lan2 --vlan-id 12"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup add -v " + name_prefix + "-vswitch-lan -p " + name_prefix + "-br2-lan1"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup set -p " + name_prefix + "-br2-lan1 --vlan-id 21"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup add -v " + name_prefix + "-vswitch-lan -p " + name_prefix + "-br2-lan2"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup set -p " + name_prefix + "-br2-lan2 --vlan-id 22"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup add -v " + name_prefix + "-vswitch-lan -p " + name_prefix + "-br3-lan1"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup set -p " + name_prefix + "-br3-lan1 --vlan-id 31"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup add -v " + name_prefix + "-vswitch-lan -p " + name_prefix + "-br3-lan2"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup set -p " + name_prefix + "-br3-lan2 --vlan-id 32"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup add -v " + name_prefix + "-vswitch-lan -p " + name_prefix + "-dc1-ion"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup set -p " + name_prefix + "-dc1-ion --vlan-id 51"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup add -v " + name_prefix + "-vswitch-lan -p " + name_prefix + "-dc1-svr"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup set -p " + name_prefix + "-dc1-svr --vlan-id 52"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup add -v " + name_prefix + "-vswitch-lan -p " + name_prefix + "-dc2-ion"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup set -p " + name_prefix + "-dc2-ion --vlan-id 61"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup add -v " + name_prefix + "-vswitch-lan -p " + name_prefix + "-dc2-svr"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup set -p " + name_prefix + "-dc2-svr --vlan-id 62"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup add -v " + name_prefix + "-vswitch-lan -p " + name_prefix + "-dc3-ion"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup set -p " + name_prefix + "-dc3-ion --vlan-id 71"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup add -v " + name_prefix + "-vswitch-lan -p " + name_prefix + "-dc3-svr"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup set -p " + name_prefix + "-dc3-svr --vlan-id 72"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup add -v " + name_prefix + "-vswitch-lan -p " + name_prefix + "-NULL"                + ";")
    cmd_list.append(    "esxcli network vswitch standard portgroup set -p " + name_prefix + "-NULL --vlan-id 999"                + ";")
    cmd_to_execute = "".join(cmd_list)
    #print ("COMMAND:",cmd_to_execute)
    return run_ssh_command(cmd_to_execute)

def change_vm_network_cmd(prefix,vm,interface, portgroup, vmx_filename=None):
    if vmx_filename == None:
        vmx_filename = vm
    return "sed -i \"s/"+ interface +".networkName.*./"+ interface +".networkName = \"" + prefix + "-"+ portgroup +"\"/g\" " + prefix + "-" + vm + "/" + vmx_filename +".vmx"

def config_linux_guest_networking(name_prefix):
    cmd_list = [] 
    cmd_list.append(    "cd /vmfs/volumes/ssd1/"                + ";")
    cmd_list.append(    change_vm_network_cmd(name_prefix, "br1-desktop", "ethernet0", "br1-lan1", vmx_filename="IMAGE-lubuntu")                + ";")
    cmd_list.append(    change_vm_network_cmd(name_prefix, "br2-desktop", "ethernet0", "br2-lan1", vmx_filename="IMAGE-lubuntu")                + ";")
    cmd_list.append(    change_vm_network_cmd(name_prefix, "br3-desktop", "ethernet0", "br3-lan1", vmx_filename="IMAGE-lubuntu")                + ";")
    cmd_list.append(    change_vm_network_cmd(name_prefix, "dc1-svr", "ethernet0", "dc1-svr", vmx_filename="IMAGE-lubuntu")                + ";")
    cmd_list.append(    change_vm_network_cmd(name_prefix, "dc2-svr", "ethernet0", "dc2-svr", vmx_filename="IMAGE-lubuntu")                + ";")
    cmd_list.append(    change_vm_network_cmd(name_prefix, "dc3-svr", "ethernet0", "dc3-svr", vmx_filename="IMAGE-lubuntu")                + ";")

    cmd_to_execute = "".join(cmd_list)
    #print ("COMMAND:",cmd_to_execute)
    return run_ssh_command(cmd_to_execute)


def config_ion_dc(name_prefix, vm_name):
    cmd_list = [] 
    cmd_list.append(    "cd /vmfs/volumes/ssd1/"                + ";")
    cmd_list.append(    change_vm_network_cmd(name_prefix, vm_name, "ethernet0", "mgmt", vmx_filename="IMAGE-3102v")                + ";")
    cmd_list.append(    change_vm_network_cmd(name_prefix, vm_name, "ethernet1", "pg-inet-trunk", vmx_filename="IMAGE-3102v")                + ";")
    cmd_list.append(    change_vm_network_cmd(name_prefix, vm_name, "ethernet2", "pg-mpls-trunk", vmx_filename="IMAGE-3102v")                + ";")
    cmd_list.append(    change_vm_network_cmd(name_prefix, vm_name, "ethernet3", vm_name, vmx_filename="IMAGE-3102v")                + ";")
    cmd_list.append(    change_vm_network_cmd(name_prefix, vm_name, "ethernet4", "NULL", vmx_filename="IMAGE-3102v")                + ";")

    ###WACK MAPPING
    ### ESXI Ethernet3     is      CGX Controller       which is VMWare Network Adapter 4 in GUI        Mapped to PG mgmt
    ### ESXI Ethernet0     is      CGX 1                which is VMWare Network Adapter 1 in GUI        Mapped to PG pg-inet-trunk
    ### ESXI Ethernet4     is      CGX 2                which is VMWare Network Adapter 5 in GUI        Mapped to PG pg-mpls-trunk
    ### ESXI Ethernet1     is      CGX 3                which is VMWare Network Adapter 2 in GUI        Mapped to PG **vm_name**
    ### ESXI Ethernet2     is      CGX 4                which is VMWare Network Adapter 3 in GUI        Mapped to PG NULL


    cmd_to_execute = "".join(cmd_list)
    #print ("COMMAND:",cmd_to_execute)
    return run_ssh_command(cmd_to_execute)

def config_ion_br(name_prefix, vm_name):
    site_without_suffix = vm_name.replace("-desktop","").replace("-svr","").replace("-ion","")
    
    cmd_list = [] 
    cmd_list.append(    "cd /vmfs/volumes/ssd1/"                + ";")
    cmd_list.append(    change_vm_network_cmd(name_prefix, vm_name, "ethernet0", "mgmt", vmx_filename="IMAGE-3102v")                + ";")
    cmd_list.append(    change_vm_network_cmd(name_prefix, vm_name, "ethernet1", "pg-inet-trunk", vmx_filename="IMAGE-3102v")                + ";")
    cmd_list.append(    change_vm_network_cmd(name_prefix, vm_name, "ethernet2", "pg-mpls-trunk", vmx_filename="IMAGE-3102v")                + ";")
    cmd_list.append(    change_vm_network_cmd(name_prefix, vm_name, "ethernet3", site_without_suffix + "-lan1", vmx_filename="IMAGE-3102v")                + ";")
    cmd_list.append(    change_vm_network_cmd(name_prefix, vm_name, "ethernet4", site_without_suffix + "-lan2", vmx_filename="IMAGE-3102v")                + ";")
    
    ###WACK MAPPING
    ### ESXI Ethernet3     is      CGX Controller       which is VMWare Network Adapter 4 in GUI        Mapped to PG mgmt
    ### ESXI Ethernet0     is      CGX 1                which is VMWare Network Adapter 1 in GUI        Mapped to PG pg-inet-trunk
    ### ESXI Ethernet4     is      CGX 2                which is VMWare Network Adapter 5 in GUI        Mapped to PG pg-mpls-trunk
    ### ESXI Ethernet1     is      CGX 3                which is VMWare Network Adapter 2 in GUI        Mapped to PG -lan1
    ### ESXI Ethernet2     is      CGX 4                which is VMWare Network Adapter 3 in GUI        Mapped to PG -lan2


    cmd_to_execute = "".join(cmd_list)
    #print ("COMMAND:",cmd_to_execute)
    return run_ssh_command(cmd_to_execute)

def clone_wanem(name_prefix):
    vm_name = name_prefix + "-WANEM"
    cmd_list = [] 
    cmd_list.append(    "cd /vmfs/volumes/ssd1/"                + ";")
    cmd_list.append(    "./clone.sh IMAGE-WANEM-INET " + vm_name        + ";")
    cmd_to_execute = "".join(cmd_list)
    #print ("COMMAND:",cmd_to_execute)
    return run_ssh_command(cmd_to_execute)

def config_wanem_networking(name_prefix):
    vm_name = "WANEM"
    cmd_list = [] 
    cmd_list = [] 
    cmd_list.append(    "cd /vmfs/volumes/ssd1/"                + ";")
    
    cmd_list.append(    change_vm_network_cmd(name_prefix, vm_name, "ethernet1", "lan-trunk", vmx_filename="IMAGE-WANEM-INET")                + ";")
    cmd_list.append(    change_vm_network_cmd(name_prefix, vm_name, "ethernet2", "pg-inet-trunk", vmx_filename="IMAGE-WANEM-INET")                + ";")
    

    cmd_to_execute = "".join(cmd_list)
    #print ("COMMAND:",cmd_to_execute)
    return run_ssh_command(cmd_to_execute)





def clone_mplsem(name_prefix):
    vm_name = name_prefix + "-MPLSEM"
    cmd_list = [] 
    cmd_list.append(    "cd /vmfs/volumes/ssd1/"                + ";")
    cmd_list.append(    "./clone.sh IMAGE-WANEM-MPLS " + vm_name        + ";")
    cmd_to_execute = "".join(cmd_list)
    #print ("COMMAND:",cmd_to_execute)
    return run_ssh_command(cmd_to_execute)

def config_wanmpls_networking(name_prefix):
    vm_name = "MPLSEM"
    cmd_list = [] 
    cmd_list = [] 
    cmd_list.append(    "cd /vmfs/volumes/ssd1/"                + ";")
    
    cmd_list.append(    change_vm_network_cmd(name_prefix, vm_name, "ethernet1", "pg-mpls-trunk", vmx_filename="IMAGE-WANEM-MPLS")                + ";")
    cmd_list.append(    change_vm_network_cmd(name_prefix, vm_name, "ethernet2", "lan-trunk", vmx_filename="IMAGE-WANEM-MPLS")                + ";")
    

    cmd_to_execute = "".join(cmd_list)
    #print ("COMMAND:",cmd_to_execute)
    return run_ssh_command(cmd_to_execute)



name_prefix = vpoc_object['config']['name_prefix']

####Clone servers but do not power on yet!
print("")
print("############################################")
print("#     Step 1 - Clone Servers               #")
print("############################################")
user_input = ""
while user_input != "y" and user_input != "n":
    user_input = input("Clone desktops/servers count: " + str(len(vpoc_object['config']['servers'])) + " (y/n) ? " )
count = 0
if user_input == "y":
    for server in vpoc_object['config']['servers']:
        count += 1
        server_name = server
        vnc_port = vpoc_object['config']['servers'][server]['vnc_port']
        print("Cloning server",count)
        print("   servername",server)
        print("   vnc_port",vnc_port)
        [ errors, stdout ] = clone_server(name_prefix, server_name, vnc_port)


###Create vSwitches
print("")
print("############################################")
print("#     Step 2 - ESXi Networking Config      #")
print("############################################")
user_input = ""
while user_input != "y" and user_input != "n":
    user_input = input("Configure VMWare vSwitch and PG networking (y/n)? " )
if user_input == "y":
    [ errors, stdout ] = create_vmware_vswitch_networking(name_prefix)
    [ errors, stdout ] = create_vmware_pg_networking(name_prefix)

###Create Linux VM Config
print("")
print("############################################")
print("#     Step 3 - Linux VM Networking         #")
print("############################################")
user_input = ""
while user_input != "y" and user_input != "n":
    user_input = input("Configure Linux Guest (BR and DC) networking (y/n)? " )
if user_input == "y":
    [ errors, stdout ] = config_linux_guest_networking(name_prefix)




####Clone IONs but do not power on yet!
print("")
print("############################################")
print("#     Step 4 - Clone ION's                 #")
print("############################################")
user_input = ""
while user_input != "y" and user_input != "n":
    user_input = input("Clone IONS count: " + str(len(vpoc_object['config']['ions'])) + " (y/n) ? " )
count = 0
if user_input == "y":
    for ions in vpoc_object['config']['ions']:
        count += 1
        ions_name = ions
        vnc_port = vpoc_object['config']['ions'][ions]['vnc_port']
        print("Cloning server",count)
        print("   servername",ions)
        print("   vnc_port",vnc_port)
        [ errors, stdout ] = clone_ions(name_prefix, ions_name, vnc_port)


###Create ION VM Config
print("")
print("############################################")
print("#     Step 5 - ION VM Networking Config    #")
print("############################################")
user_input = ""
while user_input != "y" and user_input != "n":
    user_input = input("Configure ION Guest (BR and DC) networking (y/n)? " )
if user_input == "y":
    for ions in vpoc_object['config']['ions']:
        if "dc" in str(ions).lower():
            [ errors, stdout ] = config_ion_dc(name_prefix, ions)
        else:
            [ errors, stdout ] = config_ion_br(name_prefix, ions)
    
###Clone ION WAN SIMULATOR Config
print("")
print("############################################")
print("#     Step 6 - Clone WAN INET Emulator     #")
print("############################################")
user_input = ""
while user_input != "y" and user_input != "n":
    user_input = input("Clone Wan INET Emulator (y/n)? " )
if user_input == "y":
    clone_wanem(name_prefix)

###Config ION WAN SIMULATOR Networking
print("")
print("############################################")
print("#     Step 7 - INET WAN Emulator Networking#")
print("############################################")
user_input = ""
while user_input != "y" and user_input != "n":
    user_input = input("Config Wan INET Emulator networking (y/n)? " )
if user_input == "y":
    config_wanem_networking(name_prefix)


###Clone ION WAN SIMULATOR Config
print("")
print("############################################")
print("#     Step 8 - Clone WAN MPLS Emulator     #")
print("############################################")
user_input = ""
while user_input != "y" and user_input != "n":
    user_input = input("Clone Wan MPLS Emulator (y/n)? " )
if user_input == "y":
    clone_mplsem(name_prefix)

###Config ION MPLS SIMULATOR Networking
print("")
print("############################################")
print("#     Step 9 - MPLS WAN Emulator Networking#")
print("############################################")
user_input = ""
while user_input != "y" and user_input != "n":
    user_input = input("Config Wan MPLS Emulator networking (y/n)? " )
if user_input == "y":
    config_wanmpls_networking(name_prefix)

print("")
print("")
print("############################################")
print("#     COMPLETE  - Manual Steps remaining   #")
print("############################################")
print("TODO:")
print(" 1) Power on WANEM and MPLS WANEM to generate VM-LAN-GW Mac address on Ethernet0")
print(" 2) Configure STATIC DHCP lease on PFSense for WANEM")
print(" 3) Enable Guacamole HTTP port on PFSENSE to DNAT to WANEM port")
print(" 4) Configure STATIC DHCP lease on PFSense for MPLSEM")
print(" 5) Restart WANEM and MPLS WANEM to retrieve static DHCP lease assignment")
print(" 6) Update GUACAMOLE VNC and SSH IP's (for WanEM/MPLSEm)")
print(" 7) Power on Virtual Machines")
print(" 8) Claim and LAB!")



