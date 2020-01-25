#!/usr/bin/python3
#
#

import urllib3
import xml.dom.minidom

#############################################################################
# Flow
# init system (vars,etc, configfile,...)
#############################################################################

#############################################################################
#############################################################################
class storage:
    """ use a persistent store for the data """
    storagename = ""

    def createtables(self):
        """ create all tables needed for this database """
        # CREATE TABLE db_version (major INTEGER NOT NULL,
        #                          minor INTEGER NOT NULL,
        #               UNIQUE KEY version_key (major, minor)
        #                          )
        #
        # CREATE TABLE ise (device_id    INTEGER NOT NULL,
        #                   channel_id   INTEGER NOT NULL,
        #                   datapoint_id INTEGER NOT NULL,
        #        UNIQUE KEY ise_key (device_id, channel_id, datapoint_id)
        #                   )
        #
        # CREATE TABLE device (name           VARCHAR(64) DEFAULT NULL,
        #                      device_id      INTEGER NOT NULL,
        #                      unreach        BOOLEAN DEFAULT NULL,
        #                      sticky_unrach  BOOLEAN DEFAULT NULL,
        #                      config_pending BOOLEAN_DEFAULT NULL,
        #                      rx_rssi        INTEGER DEFAULT NULL,
        #                      tx_rssi        INTEGER DEFAULT NULL,
        #                      address        VARCHAR(32) DEFAULT NULL,
        #                      interface      VARCHAR(16) DEFAULT '',
        #                      device_type    VARCHAR(32) DEFAULT NULL,
        #                      ready_config   BOOLEAN DEFAULT NULL,
        #         PRIMARY KEY (device_id))
        #
        # CREATE TABLE channel (name              VARCHAR(64) DEFAULT NULL,
        #                       channel_id        INTEGER NOT NULL,
        #                       visible           BOOLEAN DEFAULT NULL,
        #                       operate           BOOLEAN DEFAULT NULL,
        #                       type              INTEGER DEFAULT -1,
        #                       address           VARCHAR(32) DEFAULT '',
        #                       direction         VARCHAR(16) DEFAULT '',
        #                       channel_index     INTEGER DEFAULT '-1',
        #                       group_partner     VARCHAR(32) DEFAULT NULL,
        #                       aes_available     BOOLEAN DEFAULT NULL,
        #                       transmission_mode VARCHAR(32) DEFAULT NULL,
        #                       indx              INTEGER DEFAULT NULL,
        #          PRIMARY KEY (channel_id))
        #
        #
        # CREATE TABLE datapoint (name         VARCHAR(64) DEFAULT NULL,
        #                         datapoint_id INTEGER NOT NULL,
        #                         type         VARCHAR(32) DEFAULT NULL,
        #                         value        VARCHAR(64) DEFAULT NULL,
        #                         valuetype    VARCHAR(64) DEFAULT NULL,
        #                         valueunit    VARCHAR(16) DEFAULT NULL,
        #                         timestamp    TIMESTAMP NULL DEFAULT NULL,
        #                         operation    INTEGER DEFAULT NULL,
        #            PRIMARY KEY (datapoint_id))
        #
        ####
        print("create db")


    def __init__(self, store="/tmp/ccu.db"):
        self.storagename = store
        
#############################################################################
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
store=storage()
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
