#!/usr/bin/python
#
# insert homematic values into influxdb avoiding telegraf
import time
import mysql.connector
import pycurl
from mysql.connector import errorcode

debugging = 0
debugtext = ""
debugtime = ''

class send_to_influxdb:
    global debugtext
    global debugtime
    connection=""
    def __init__(self):
        self.connection = pycurl.Curl()
        self.connection.setopt(self.connection.URL, "http://127.1:9999/write?db=homematic")

    def insert_record(self,string):
        if debugging == 0:
            self.connection.setopt(self.connection.POSTFIELDS, str(string))
            self.connection.perform()
        else:
            print(string + "\n>>" +
                  debugtext + "- " + debugtime)



class worker():
    config = {
            'user' : 'ccu',
            'password':'ccu',
            'database':'ccu'
    }
    dbh=''
    c=""

    device_name = ''
    device_id = 0
    device_address = ''
    device_rx_rssi = 0
    device_tx_rssi = 0

    def __init__(self):
        try:
            self.dbh = mysql.connector.connect(**self.config)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("wrong user/password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("database not found")
            else:
                print(err)
        self.c = send_to_influxdb()
    
    def getDatapoint(self,device_id,channel_id):
        global debugtime
        dtim=0
        returnstring=""
        cursor = self.dbh.cursor()
        q=("SELECT lower(datapoint.type) as dataname,"+
                "datapoint.value AS dataval, "+
                "datapoint.valuetype AS vt, "+
                "UNIX_TIMESTAMP(datapoint.timestamp) AS tim "+
                "FROM datapoint,channel,device,ise "+
                "WHERE datapoint.datapoint_id=ise.datapoint_id"+
                " AND channel.channel_id = ise.channel_id"+
                " AND device.device_id = ise.device_id"+
                " AND device.device_id = %(d)s"+
                " AND channel.channel_id = %(c)s "+
                "ORDER BY datapoint.timestamp ASC")
        cursor.execute(q, { 'd': device_id, 'c': channel_id })
        datadict= cursor.fetchall()
        cursor.close()
        tz=time.timezone
        tm=int(time.time() - tz)
        #tm=0
        for ( dataname, dataval, vt, tim ) in datadict:
            if dataval != "" and dataname != "" and vt != 20 and dataname != 'ip' and dataname != 'info':
                if dataval == "false":
                    dataval=0
                if dataval == "true":
                    dataval=1
                if tim < (tm - 604800): # got no value in the last 2 weeks
                    dtim=2
                    tm = tim # so we return the last time we've got
                returnstring = returnstring + ','+ str(dataname) + '=' + str(dataval)
        returnstring = returnstring + ' ' + str(int(tm + tz)) + '000000000'
        #if tm == 0:
        #    return ""
        if debugging != 0:
            debugtime = "Time: "+ time.asctime(time.gmtime(tm+tz)) + " " + str(dtim)
        return returnstring


    def getChannel(self,dname,device,rx_rssi,tx_rssi,address,devicetype,name1,name2):
        cursor = self.dbh.cursor()
        q=("select "
           +"distinct(lower(replace(replace(channel.name,' ','_'),':','_'))) as name"
           +",channel.channel_id as channel_id"
           +",channel.indx as cindex"
           +"  from channel,device,ise"
           +"  where "
           +"ise.device_id= %(d)s"
           +" AND "
           +"channel.channel_id=ise.channel_id"
           +" and "
           +"device.device_id=ise.device_id"
           )
        cursor.execute(q, { 'd': device})
        channeldict = cursor.fetchall()
        cursor.close()
        for (name,channel_id, cindex) in channeldict:
            if rx_rssi is None:
                rx_rssi=-512
            if tx_rssi is None:
                tx_rssi=-512
            if cindex < 1 or cindex == "":
                cindex=-1
            if address is None:
                address="None"
            dp=self.getDatapoint(device,channel_id)
            if dp != "":
                self.c.insert_record(str(dname)
                                     +",index="+str(cindex)
                                     +",devicetype="+str(devicetype)
                                     +',name=' +str(name)
                                     +',name1=' +str(name1)
                                     +',name2=' +str(name2)
                                     +',deviceaddress=' +address
                                     +' rx_rssi=' +str(rx_rssi)
                                     +',tx_rssi=' +str(tx_rssi) 
                                     +str(dp))
            #print(self.getDatapoint(device,channel_id))

    def getDevice(self):
        global debugtext
        cursor = self.dbh.cursor()
        cursor.execute("SELECT "
                       +"lower(replace(name,' ','_')) as name,"
                       +"device_id,"
                       +"rx_rssi,"
                       +"tx_rssi,"
                       +"address,"
                       +"device_type "
                       +"FROM device "
                       +"WHERE address is not null")
        devicedict = cursor.fetchall()
        cursor.close()
        for (name, device_id, rx_rssi, tx_rssi,address,device_type) in devicedict:
            namearray = name.split('_',3)
            name1 = namearray[0]
            name2 = namearray[1]
            if debugging != 0:
                debugtext=name
            self.getChannel(name,device_id,rx_rssi,tx_rssi,address,device_type,name1,name2)

##################################################################
worker()
worker().getDevice()
