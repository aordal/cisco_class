import xmltodict
import json
import re

from device import Device


def checkroutes(sw):

    #load command variable with xml from this command
    command = sw.show('show ip route')
    
    result = xmltodict.parse(command[1])
    
    #define variables
    i = 0
    routeloop = False
    t1 = 0
    t2 = 0
    
    #run through each route looking for route uptime
    while i < len(result['ins_api']['outputs']['output']['body']['TABLE_vrf']['ROW_vrf']['TABLE_addrf']['ROW_addrf']['TABLE_prefix']['ROW_prefix']):
        
        #assign uptime value to variable
        uptime = result['ins_api']['outputs']['output']['body']['TABLE_vrf']['ROW_vrf']['TABLE_addrf']['ROW_addrf']['TABLE_prefix']['ROW_prefix'][0]['TABLE_path']['ROW_path'][0]['uptime']
        i += 1
        
        #using regex assign number of days route has been up to a variable
        day = re.findall(r'\P(.*)D', uptime)
        
        for days in day:
            t1=days
        
        #using regesx assign number of hours route has been up to a variable
        hour = re.findall(r'\T(.*)H', uptime)
        for hours in hour:
            t2=hours
    
        if int(t1) < 1 and int(t2) < 1:
        	routeloop = True
    
    #check if routes have been up less than an hour or not
    if routeloop:
        print "You have routes that are less than 1 hour old. Possible routes flapping(loop)"
    else:
    	print "Routes look good."
    
    return routeloop

def test_ospf(sw):
        """Test_ospf uses various show commands to determine if OSPF is running on the switch.
        """
        cmd = cmd = sw.show('show ip ospf')
        resp = xmltodict.parse(cmd[1])['ins_api']['outputs']['output']

        try:
                if resp["code"] == "400":
                        #most likely feature ospf is not in the configuration.
                        return False
                elif resp["code"] == "501" and resp["clierror"] == "Note:  process currently not running\n":
                        #feature ospf is enabled but not configured.
                        return False
                elif resp["code"] == "200":
                        #ospf appears to be configured
                        contexts = resp["body"]["TABLE_ctx"]["ROW_ctx"]
                        if len(contexts) > 0:
                                return True
        except Exception as oops:
                print type(oops)
                print oops.args
                print oops
        return False

def test_eigrp(sw):
        """Test_eigrp uses various show commands to determine if OSPF is running on the switch.
        """
        cmd = cmd = sw.show('show ip eigrp')
        resp = xmltodict.parse(cmd[1])['ins_api']['outputs']['output']

        try:
                if resp["code"] == "400":
                        #most likely feature eigrp is not in the configuration.
                        return False
                elif resp["code"] == "501" and resp["clierror"] == "Note:  process currently not running\n":
                        #feature eigrp is enabled but not configured.
                        return False
                elif resp["code"] == "200":
                        #eigrp appears to be configured
                        contexts = resp["body"]["TABLE_asn"]["ROW_asn"]
                        if len(contexts) > 0:
                                return True
        except Exception as oops:
                print type(oops)
                print oops.args
                print oops
        return False

def test_bgp(sw):
        """Test_bgp uses various show commands to determine if BGP is running on the switch.
        """
        cmd = cmd = sw.show('show ip bgp')
        resp = xmltodict.parse(cmd[1])['ins_api']['outputs']['output']

        try:
                if resp["code"] == "400":
                        #most likely feature bgp is not in the configuration.
                        return False
                elif resp["code"] == "501" and resp["clierror"] == "Note:  process currently not running\n":
                        #feature bgp is enabled but not configured.
                        return False
                elif resp["code"] == "501" and resp["msg"] == "Structured output unsupported":
                        #bgp appears to be configured
                        return True
        except Exception as oops:
                print type(oops)
                print oops.args
                print oops
        return False

def get_ip_protocols(sw):
        protocols = []
        ospf = test_ospf(sw)
        if ospf:
                protocols.append("ospf")
        eigrp = test_eigrp(sw)
        if eigrp:
                protocols.append("eigrp")
        bgp = test_bgp(sw)
        if bgp:
                protocols.append("bgp")


        return protocols

def stp_detail(switch):
    debug = False
    ifloop = False
    stp_split = []

    getdata = switch.conf('show spanning-tree detail')

    show_stp = xmltodict.parse(getdata[1])

    stp = show_stp ['ins_api']['outputs']['output']['body']
    
    tsn_change = re.findall('(?<=occurred\s).*(?=\:)', stp)
    for time in tsn_change:
        stp_time = time
        stp_split = stp_time.split(':')
        
        if debug:
            print stp_split

        if debug:
            print "Last topology change happened " + stp_time + " hours ago"

    tsn_number = re.findall('(?<=changes\s).*(?=\last)', stp)
    for number in tsn_number:
        stp_number = number

        if debug:
            print "Number of topology changes = " + stp_number

    if int(stp_split[0]) == 0 and int(stp_split[1]) <= 5:
        ifloop = True
    
    if ifloop:
        print "Last topology change happened " + stp_time + " hours ago"
        print "Number of topology changes = " + stp_number
    else:
        print "No STP topology changes."




def main():

        switch = Device(ip='172.23.193.210', username='admin', password='P@ssw0rd')
        switch.open()

        checkroutes(switch)
        get_ip_protocols(switch)
        stp_detail(switch)


if __name__ == "__main__":
    main()
