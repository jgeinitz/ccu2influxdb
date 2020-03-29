#!/usr/bin/python2
# encoding=utf8
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

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import urllib3
import sqlite3
import time
import xml.dom.minidom
import syslog
import argparse
import pycurl

global dEbug
global store
global log

#############################################################################
# Flow
# init system (vars,etc, configfile,...)
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug',   help='debug output (takes a number)',default=0)
parser.add_argument('-f', '--influxdb',help='base url of the influxdb',     default="http://influxdb.example.com")
parser.add_argument('-R', '--Recreate',help='re-create tables',             default=0)
parser.add_argument('-s', '--database',help='path to database',             default="/tmp/ccu.db")
parser.add_argument('-u', '--ccu',     help='address of ccu',               default='http://ccu.example.com/')
parser.add_argument('-v', '--verbose', help='be noisy (takes a number)',    default=0)

args = parser.parse_args()

dEbug = args.verbose
dEbug = args.debug
store = args.database
#############################################################################

#############################################################################
class send_to_influxdb:
    connection=""
    def __init__(self,dbconnector):
        self.connection = pycurl.Curl()
        self.connection.setopt(self.connection.URL, dbconnector+"/write?db=homematic")

    def insert_record(self,string):
        self.connection.setopt(self.connection.POSTFIELDS, str(string))
        log.dprint("insert record " +str(string))
        self.connection.perform()

#############################################################################
class processdata:
    influx=""
    def __init__(self,db):
        self.influx = send_to_influxdb(db)


    def work(self):
        self.getdevice()

    def getdevice(self):
        cursor = db.cursor()
        for row in cursor.execute("SELECT "
                       +"lower(replace(name,' ','_')) as name,"
                       +"device_id,"
                       +"rx_rssi,"
                       +"tx_rssi,"
                       +"address,"
                       +"device_type "
                       +"FROM device "
                       +"WHERE address is not null"):
            (name,device_id, rx_rssi, tx_rssi, address, device_type) = row
            namearray = name.split('_')
            if rx_rssi == "None":
                rx_rssi=65533
            if tx_rssi == "None":
                tx_rssi=65533
            self.getchannel(name,device_id,
                            rx_rssi, tx_rssi,
                            address, device_type,
                            namearray[0],
                            namearray[1])
                          #  namearray[2])
        db.commit()

    def getchannel(self, dname, device, rx_rssi, tx_rssi, address, device_type,
                   name1, name2):
        global log
        c = db.cursor()
        q=("SELECT "
           +"  distinct(lower(replace(replace(channel.name,' ','_'),':','_'))) AS name,"
           +"  channel.channel_id AS channel_id,"
           +"  channel.indx AS cindex "
           +"FROM channel,device,ise "
           +"WHERE "
           +"  ise.device_id='"+str(device)+"' "
           +"AND "
           +"  channel.channel_id=ise.channel_id "
           +"AND "
           +"  device.device_id=ise.device_id")
        for row in c.execute(q):
            (name, channel_id, cindex) = row
            dp = self.getdatapoint(device, channel_id)
            if dp != "":
                self.influx.insert_record(str(dname)
                      +",index="         +str(cindex)
                      +",devicetype="    +str(device_type)
                      +',name='          +str(name)
                      +',name1='         +str(name1)
                      +',name2='         +str(name2)
                      +',deviceaddress=' +address
                      +' rx_rssi='       +str(rx_rssi)
                      +',tx_rssi='       +str(tx_rssi)
                      +str(dp))

        db.commit()

    def getdatapoint(self,device_id,channel_id):
        returnstring=""
        cursor = db.cursor()
        q=("SELECT "
           +"  lower(datapoint.type) AS dataname, "
           +"  datapoint.value AS dataval, "
           +"  datapoint.valuetype AS vt, "
           +"  datapoint.timestamp AS tim "
           +"FROM "
           +"  datapoint,channel,device,ise "
           +"WHERE "
           +"  datapoint.datapoint_id=ise.datapoint_id "
           +"AND "
           +"  channel.channel_id = ise.channel_id "
           +"AND "
           +"  device.device_id = ise.device_id "
           +"AND "
           +"  device.device_id = '"+str(device_id)+"' "
           +"AND "
           +"  channel.channel_id = "+str(channel_id)+" "
           +"ORDER BY datapoint.timestamp ASC")
        tm=int(time.time())
        datavalues=""
        got_a_datapoint=0
        for row in cursor.execute(q):
            ( dataname, dataval, vt, tim) = row
            if dataval != "" and dataname != "" and vt != 20 and dataname != 'ip' and dataname != 'info':
                if dataval == "false":
                    dataval=0
                if dataval == "true":
                    dataval=1
                if tim >= (tm - 1814400): # got no value in the last 6 weeks
                    got_a_datapoint = 1
#                    tm = tim # so we return the last time we've got
                    returnstring = returnstring + ','+ str(dataname) + '=' + str(dataval)
        returnstring = returnstring + ' ' + str(int(tm)) + '000000000'
        if got_a_datapoint == 0:
            return ""
        return returnstring


#############################################################################
#############################################################################
class logging:
    global dEbug

    def __init__(self,myname):
        syslog.openlog(logoption=syslog.LOG_PID,
                       facility=syslog.LOG_DAEMON)
        self.iprint(myname + " starting")

    def iprint(self,text):
        syslog.syslog(syslog.LOG_INFO, text)
        if dEbug != 0:
            print("LOG: "+ str(text))

    def dprint(self,text):
        if dEbug > 1:
            syslog.syslog(syslog.LOG_DEBUG, text)
            print("DBG: "+ str(text))

    def eprint(self,text):
        syslog.syslog(syslog.LOG_ERR, text)
        print("ERR: "+ str(text))

#############################################################################
#############################################################################
class storage:
    """ use a persistent store for the data """

    databaseconnection = ""
    dbmajor = 0
    dbminor = 1

    def destroytables(self):
        log.iprint("re-creating all tables")
        self.databaseconnection.cursor()
        self.databaseconnection.execute("DROP TABLE IF EXISTS db_version")
        self.databaseconnection.execute("DROP TABLE IF EXISTS ise")
        self.databaseconnection.execute("DROP TABLE IF EXISTS device")


    def chkDBversion(self):
        c = self.databaseconnection.cursor()
        c.execute("SELECT COUNT(*) AS cnt FROM db_version")
        x = c.fetchone()
        self.databaseconnection.commit()
        if x[0] == 0:
            c=self.databaseconnection.cursor()
            c.execute("INSERT INTO db_version VALUES (" +
                      str(self.dbmajor) + "," +
                      str(self.dbminor) + ")")
            self.databaseconnection.commit()
        else:
            c = self.databaseconnection.cursor()
            c.execute("SELECT * FROM db_version")
            (maj, mino) = c.fetchone()
            if maj != self.dbmajor:
                log.eprint("Database major version mismatch: " +
                           str(maj) + " required " + str(self.dbmajor))
                exit(1)
            if mino < self.dbminor:
                log.iprint("Database warning program minor is " +
                          str(self.dbminor) +
                          " database minor is " + str(mino))
            else:
                if mino != self.dbminor:
                    log.iprint("Database warning: database is newer than program "+
                              str(mino) + " <-> " + str(self.dbminor))

    def createtables(self):
        """ create all tables needed for this database """
        self.databaseconnection.cursor()
        try:
            self.databaseconnection.execute('''
              CREATE TABLE IF NOT EXISTS
                           db_version (major INTEGER NOT NULL,
                                       minor INTEGER NOT NULL,
                          PRIMARY KEY (major, minor))'''
                                            )
            self.databaseconnection.execute('''
              CREATE TABLE IF NOT EXISTS ise (
                                device_id    INTEGER NOT NULL,
                                channel_id   INTEGER NOT NULL,
                                datapoint_id INTEGER NOT NULL,
                PRIMARY KEY    (device_id, channel_id, datapoint_id))
                ''')
            self.databaseconnection.execute('''
                CREATE TABLE IF NOT EXISTS device (
                name           VARCHAR(64) DEFAULT NULL,
                device_id      INTEGER NOT NULL,
                unreach        BOOLEAN DEFAULT NULL,
                sticky_unreach BOOLEAN DEFAULT NULL,
                config_pending BOOLEAN_DEFAULT NULL,
                rx_rssi        INTEGER DEFAULT 65530,
                tx_rssi        INTEGER DEFAULT 65530,
                address        VARCHAR(32) DEFAULT NULL,
                interface      VARCHAR(16) DEFAULT '',
                device_type    VARCHAR(32) DEFAULT NULL,
                ready_config   BOOLEAN DEFAULT NULL,
                PRIMARY KEY (device_id))''')
            self.databaseconnection.execute('''
                CREATE TABLE IF NOT EXISTS channel (
                name              VARCHAR(64) DEFAULT NULL,
                channel_id        INTEGER NOT NULL,
                visible           BOOLEAN DEFAULT NULL,
                operate           BOOLEAN DEFAULT NULL,
                type              INTEGER DEFAULT -1,
                address           VARCHAR(32) DEFAULT '',
                direction         VARCHAR(16) DEFAULT '',
                channel_index     INTEGER DEFAULT '-1',
                group_partner     VARCHAR(32) DEFAULT NULL,
                aes_available     BOOLEAN DEFAULT NULL,
                transmission_mode VARCHAR(32) DEFAULT NULL,
                indx              INTEGER DEFAULT NULL,
                PRIMARY KEY (channel_id))''')
            self.databaseconnection.execute('''
                CREATE TABLE IF NOT EXISTS datapoint (
                name         VARCHAR(64) DEFAULT NULL,
                datapoint_id INTEGER NOT NULL,
                type         VARCHAR(32) DEFAULT NULL,
                value        VARCHAR(64) DEFAULT NULL,
                valuetype    VARCHAR(64) DEFAULT NULL,
                valueunit    VARCHAR(16) DEFAULT NULL,
                timestamp    TIMESTAMP NULL DEFAULT NULL,
                operation    INTEGER DEFAULT NULL,
                PRIMARY KEY (datapoint_id))''')
            self.databaseconnection.commit()
        except sqlite3.OperationalError as e:
            log.eprint("cannot create table '"+  str(e) + "'")
            exit(1)

    def statement(self, sql):
        self.databaseconnection.execute(sql)

    def cursor(self):
        return(self.databaseconnection.cursor())

    def commit(self):
        self.databaseconnection.commit()

    def __init__(self, droptable):
        self.databaseconnection = sqlite3.connect(store)
        log.dprint("connected to database "+ str(store))
        if droptable != 0:
            self.destroytables()
        self.createtables()
        self.chkDBversion()

#############################################################################
#############################################################################
class readccuxml:
    """purpose: fetch values from ccu using the xml plugin
       parse the xml and construct sql statements to store the
       data inside a reletional database"""
    ccuaddr = "http://localhost/"

    def booltonumber(self, invar):
        if invar == "true":
            return(1)
        return(0)

    def readdevice(self, device):
        devicetext=""
        device_id=""
        unreach=""
        sticky_unreach=""
        config_pending=""
        if device.hasAttributes():
            for deviceattribName in device.attributes.keys():
                attr=device.getAttribute(deviceattribName)
                if (attr =="true") or (attr =="false"):
                    attr = self.booltonumber(attr)
                if deviceattribName == "name":
                    currentdev=attr
                elif deviceattribName == "ise_id":
                    device_id = attr
                elif deviceattribName == "unreach":
                    unreach = attr
                elif deviceattribName == "sticky_unreach":
                    sticky_unreach = attr
                elif deviceattribName == "config_pending":
                    config_pending = attr
            query = "SELECT COUNT('device_id') FROM device WHERE device_id = '"+str(device_id)+"'"
            c=db.cursor()
            c.execute(query)
            newdevice = c.fetchone()
            db.commit()
            log.dprint("inserting device    record for "+str(currentdev))
            if newdevice[0] == 0:
                db.statement("INSERT INTO device (device_id) VALUES ('"+str(device_id)+"')")
            db.statement("UPDATE device SET "+
                         "name = '" + str(currentdev) + "', " +
                         "unreach = '" + str(unreach) + "', "+
                         "sticky_unreach = '" + str(sticky_unreach) + "', " +
                         "config_pending = '" + str(config_pending) + "' " +
                         " WHERE " +
                         "device_id = '" + device_id + "'")
            db.commit()

        for c in device.childNodes:
            self.readchannel(c,device_id)


    def readchannel(self, channel, device_id):
        channel_id = ""
        visible = ""
        name=""
        operate=""
        index=""

        if channel.hasAttributes():
            for channelattribName in channel.attributes.keys():
                attr=channel.getAttribute(channelattribName)
                if (attr =="true") or (attr =="false"):
                    attr = self.booltonumber(attr)
                if channelattribName == "name":
                    name = attr
                elif channelattribName == "ise_id":
                    channel_id = attr
                elif channelattribName == "visible":
                    visible = attr
                elif channelattribName == "operate":
                    operate = attr
                elif channelattribName == "index":
                    index = attr
            query = "SELECT COUNT('channel_id') FROM channel WHERE channel_id = '"+str(channel_id)+"'"
            c=db.cursor()
            c.execute(query)
            newdevice = c.fetchone()
            db.commit()
            log.dprint("inserting channel   "+str(name))
            if newdevice[0] == 0:
                db.statement("INSERT INTO channel (channel_id) VALUES ('"+str(channel_id)+"')")
            db.statement("UPDATE channel SET "+
                         "name = '" + str(name) + "', " +
                         "indx = '" + str(index) + "', "+
                         "visible = '" + str(visible) + "', " +
                         "operate = '" + str(operate) + "' " +
                         " WHERE " +
                         "channel_id = '" + channel_id + "'")
            db.commit()
        for d in channel.childNodes:
            self.readdatapoint(d, device_id, channel_id)

    def readdatapoint(self, dp, device_id, channel_id):
        if dp.hasAttributes():
            for attribName in dp.attributes.keys():
                attr=dp.getAttribute(attribName)
                if (attr =="true") or (attr =="false"):
                    attr = self.booltonumber(attr)
                if attribName == "name":
                    dataname = attr
                elif attribName == "type":
                    datatype = attr
                elif attribName == "ise_id":
                    dataid = attr
                elif attribName == "value":
                    dataval = attr
                elif attribName == "valuetype":
                    valuetype = attr
                elif attribName == "valueunit":
                    valueunit = attr
                elif attribName == "timestamp":
                    time = attr
                elif attribName == "operations":
                    op = attr
            query = "SELECT COUNT('datapoint_id') FROM datapoint WHERE datapoint_id = '"+str(dataid)+"'"
            c=db.cursor()
            c.execute(query)
            newdevice = c.fetchone()
            db.commit()
            log.dprint("inserting datapoint "+str(dataname))
            if newdevice[0] == 0:
                db.statement("INSERT INTO datapoint (datapoint_id) VALUES ('"+str(dataid)+"')")
            q = ("UPDATE datapoint SET " +
                 "name = '" + str(dataname) + "', " +
                 "type = '" + str(datatype) + "', " +
                 "value = '" + str(dataval) + "', " +
                 "valuetype = '" + str(valuetype) + "', " +
                 "valueunit = '" + str(valueunit) + "', " +
                 "timestamp = '" + str(time) + "', " +
                 "operation = '" + str(op) + "' " +
                 " WHERE " +
                 "datapoint_id = '" + str(dataid) + "'")
            db.statement(q)
            db.commit()
            self.fill_ise(dataid,channel_id,device_id)

    def fill_ise(self, dat,chan,dev):
        query = "SELECT COUNT('datapoint_id') FROM ise WHERE datapoint_id = '"+str(dat)+"'"
        c=db.cursor()
        c.execute(query)
        newdevice = c.fetchone()
        db.commit()
        if newdevice[0] == 0:
            db.statement("INSERT INTO ise (datapoint_id,channel_id,device_id) VALUES ('"+str(dat)+"','"+str(chan)+"','"+str(dev)+"')")
        else:
            q = ("UPDATE ise SET " +
                 "channel_id = '" + str(chan) + "', " +
                 "device_id = '" + str(dev) + "' " +
                 " WHERE " +
                 "datapoint_id = '" + dat + "'")
            db.statement(q)
        db.commit()

    def readrssidevice(self,dev):
        rx=65536
        tx=65536
        if dev.hasAttributes():
            for attribName in dev.attributes.keys():
                attr=dev.getAttribute(attribName)
                if attribName == "device":
                    device = attr
                elif attribName == "rx":
                    if attr == "None":
                        attr=65536
                    rx = attr
                elif attribName == "tx":
                    if attr == "None":
                        attr=65536
                    tx = attr
                q=("UPDATE device SET rx_rssi='"+str(rx)+"', tx_rssi='"+str(tx)+"' WHERE address ='"+str(device)+"'")
                db.statement(q)
                db.commit()

    def readdeviceinfo(self,liste):
        if liste.hasAttributes():
            for attribName in liste.attributes.keys():
                attr=liste.getAttribute(attribName)
                if attribName == "address":
                    addr = attr
                elif attribName == "interface":
                    interface = attr
                elif attribName == "device_type":
                    devtype = attr
                elif attribName == "ise_id":
                    ise = attr
                elif attribName == "ready_config":
                    rc = attr
            q = ("UPDATE device SET address = '"+addr + "', "+
                 "interface = '"+ interface + "', "+
                 "device_type = '" + devtype + "', "+
                 "ready_config = '" + rc + "' "+
                 "WHERE device_id = '" + ise + "'")
            db.statement(q)
            db.commit()

    def readout(self):
        """ workhorse alss the work is done here"""
        http = urllib3.PoolManager()
        try:
            remot = http.request('GET',self.ccuaddr + 'addons/xmlapi/statelist.cgi')
        except:
            print("open error ")
            exit(1)
        dom = xml.dom.minidom.parseString(remot.data)
        log.dprint("updating internal database")
        for statelist in dom.childNodes:
            for device in statelist.childNodes:
                self.readdevice(device)

        try:
            remot = http.request('GET',self.ccuaddr + 'addons/xmlapi/devicelist.cgi')
        except:
            print("open error for devicelist.xml")
            exit(1)
        dom = xml.dom.minidom.parseString(remot.data)
        for devicelist in dom.childNodes:
            for l in devicelist.childNodes:
                self.readdeviceinfo(l)

        try:
            remot = http.request('GET',self.ccuaddr + 'addons/xmlapi/rssilist.cgi')
        except:
            print("open error for rssilist.xml")
            exit(1)
        dom = xml.dom.minidom.parseString(remot.data)
        for rssilist in dom.childNodes:
            for list in rssilist.childNodes:
                self.readrssidevice(list)

        log.dprint("got all xml data")
##
    def __init__(self, addr):
        """ define the ccu to connect to"""
        self.ccuaddr = addr
        log.dprint("xml parser: connecting to ccu at " + addr)

#############################################################################
#############################################################################
#############################################################################

# +------------------------------------------------------------------+
# | setup syslog and say hello                                       |
log = logging("ccu to influxdb")
# | check for another running instance                               |
# | ---- and exit if found telling syslog about it                   |
# | init database if needed                                          |
db=storage(args.Recreate)
# | setup ccureader and influxdb writer                              |
ccu = readccuxml(args.ccu)
influx = processdata(args.influxdb)
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
influx.work()
# | |                           | wait for a reasonable time         |
# +-+---------------------------+------------------------------------+

