#!/usr/bin/python3
#
#

import urllib3
import xml.dom.minidom
#############################################################################
# Flow
# init system (vars,etc, configfile,...)
#############################################################################

class readccuxml:
    ccuaddr = "http://localhost/"


    def readout(self):
        http = urllib3.PoolManager()
        try:
            remot = http.request('GET',self.ccuaddr + 'addons/xmlapi/statelist.cgi')
        except:
            print("open error ")
            exit(1)
        dom = xml.dom.minidom.parseString(remot.data)
        for statelist in dom.childNodes:
            for device in statelist.childNodes:
                if device.hasAttributes():
                    for deviceattribName in device.attributes.keys():
                        print(str(deviceattribName) + " " + device.getAttribute(deviceattribName))
                #for c in device.childNodes:
                #    print(c)

    def __init__(self, addr):
        self.ccuaddr = addr
        
#############################################################################
#############################################################################
#############################################################################

# +------------------------------------------------------------------+
# | setup syslog and say hello                                       |
# | check for another running instance                               |
# | ---- and exit if found telling syslog about it                   |
# | init database fi needed                                          |
# | setup ccureader and influxdb writer                              |
ccu = readccuxml("http://192.168.21.19/")
# | setup timer system                                               |
# +------------------------------------------------------------------|
# | | while running                                                  |
# | +----------------------------------------------------------------+
# | | daily update needed?                                           |
# | +------yes------------------+------------------------------------+
# | | fetch daily data from ccu |                                    |
# | | store in database         |    %                               |
# | | daily done                |                                    |
# | +---------------------------+------------no----------------------+
# | |                           | note timestamp                     |
# | |       %                   | fetch data from ccu to database    |
ccu.readout()
# | |                           | read databse and send to influxdb  |
# | |                           | wait for a reasonable time         |
# +-+---------------------------+------------------------------------+

#
#
# Flow
# +------------------------------------------------------------------+
# | setup syslog and say hello                                       |
# | check for another running instance                               |
# | ---- and exit if found telling syslog about it                   |
# | init database fi needed                                          |
# | setup timer system                                               |
# +------------------------------------------------------------------|
# | | while running                                                  |
# | +----------------------------------------------------------------+
# | | daily update needed?                                           |
# | +------yes------------------+------------------------------------+
# | | fetch daily data from ccu |                                    |
# | | store in database         |    %                               |
# | | daily done                |                                    |
# | +---------------------------+------------no----------------------+
# | |                           | note timestamp                     |
# | |       %                   | fetch data from ccu to database    |
# | |                           | read databse and send to influxdb  |
# | |                           | wait for a reasonable time         |
# +-+---------------------------+------------------------------------+

#############################################################################
#
#<stateList>
#<device name="Bad_Taster_NEQ0453551" ise_id="10519" unreach="false" sticky_unreach="false" config_pending="false">
#<channel name="Bad_Taster_NEQ0453551:0" ise_id="10520" index="0" visible="" operate="">
#<datapoint name="BidCos-RF.NEQ0453551:0.UNREACH" type="UNREACH" ise_id="10536" value="false" valuetype="2" valueunit="" timestamp="1577012041" operations="5"/>
#<datapoint name="BidCos-RF.NEQ0453551:0.STICKY_UNREACH" type="STICKY_UNREACH" ise_id="10532" value="false" valuetype="2" valueunit="" timestamp="1577012041" operations="7"/>
#<datapoint name="BidCos-RF.NEQ0453551:0.CONFIG_PENDING" type="CONFIG_PENDING" ise_id="10522" value="false" valuetype="2" valueunit="" timestamp="1577012041" operations="5"/>
#<datapoint name="BidCos-RF.NEQ0453551:0.LOWBAT" type="LOWBAT" ise_id="10526" value="false" valuetype="2" valueunit="" timestamp="1577012041" operations="5"/>
#<datapoint name="BidCos-RF.NEQ0453551:0.RSSI_DEVICE" type="RSSI_DEVICE" ise_id="10530" value="1" valuetype="8" valueunit="" timestamp="1577012041" operations="5"/>
#<datapoint name="BidCos-RF.NEQ0453551:0.RSSI_PEER" type="RSSI_PEER" ise_id="10531" value="1" valuetype="8" valueunit="" timestamp="1577012041" operations="5"/>
#</channel>
#<channel name="Bad_Taster_NEQ0453551:1" ise_id="10540" index="1" visible="true" operate="true">
#<datapoint name="BidCos-RF.NEQ0453551:1.PRESS_SHORT" type="PRESS_SHORT" ise_id="10545" value="" valuetype="2" valueunit="" timestamp="0" operations="6"/>
#<datapoint name="BidCos-RF.NEQ0453551:1.PRESS_LONG" type="PRESS_LONG" ise_id="10543" value="" valuetype="2" valueunit="" timestamp="0" operations="6"/>
#</channel>
#<channel name="Bad_Taster_NEQ0453551:2" ise_id="10546" index="2" visible="true" operate="true">
#<datapoint name="BidCos-RF.NEQ0453551:2.PRESS_SHORT" type="PRESS_SHORT" ise_id="10551" value="" valuetype="2" valueunit="" timestamp="0" operations="6"/>
#<datapoint name="BidCos-RF.NEQ0453551:2.PRESS_LONG" type="PRESS_LONG" ise_id="10549" value="" valuetype="2" valueunit="" timestamp="0" operations="6"/>
#</channel>
#</device>
#</statelist>
