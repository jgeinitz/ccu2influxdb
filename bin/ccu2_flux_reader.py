#!/usr/bin/python
#
import time
import mysql.connector
from mysql.connector import errorcode

class worker():
    config = {
            'user' : 'ccu', 'password':'ccu', 'database':'ccu'
    }
    dbh=''

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
    
    def getDatapoint(self,device_id,channel_id):
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
                " AND channel.channel_id = %(c)s"+
                " ORDER BY datapoint.timestamp DESC")
        cursor.execute(q, { 'd': device_id, 'c': channel_id })
        datadict= cursor.fetchall()
        cursor.close()
        tm=int(time.time())
        #tm=0
        for ( dataname, dataval, vt, tim ) in datadict:
            if dataval != "" and dataname != "" and vt != 20 and dataname != 'ip' and dataname != 'info':
                if dataval == "false":
                    dataval=0
                if dataval == "true":
                    dataval=1
                tm = tim
                returnstring = returnstring + ','+ str(dataname) + '=' + str(dataval)
        returnstring = returnstring + ' ' + str(int(tm)) + '000000000'
        #if tm == 0:
        #    return ""
        return returnstring


    def getChannel(self,dname,device,rx_rssi,tx_rssi,address,devicetype,name1,name2):
        cursor = self.dbh.cursor()
        q=("select distinct(lower(replace(replace(channel.name,' ','_'),':','_'))) as name,channel.channel_id as channel_id, channel.indx as cindex from channel,device,ise where ise.device_id= %(d)s AND channel.channel_id=ise.channel_id and device.device_id=ise.device_id")
        cursor.execute(q, { 'd': device})
        channeldict = cursor.fetchall()
        cursor.close()
        for (name,channel_id, cindex) in channeldict:
            if rx_rssi is None:
                rx_rssi=-255
            if tx_rssi is None:
                tx_rssi=-255
            if cindex < 1 or cindex == "":
                cindex=-1
            if address is None:
                address="None"
            dp=self.getDatapoint(device,channel_id)
            if dp != "":
                print(str(dname)+",index="+str(cindex)+",devicetype="+str(devicetype)
                    +',name=' +str(name)
                    +',name1=' +str(name1)
                    +',name2=' +str(name2)
                    +',deviceaddress=' +address
                    +' rx_rssi=' +str(rx_rssi)
                    +',tx_rssi=' +str(tx_rssi) 
                    +str(dp))
            #print(self.getDatapoint(device,channel_id))

    def getDevice(self):
        cursor = self.dbh.cursor()
        #cursor.execute("select lower(replace(name,' ','_')) as name,device_id,rx_rssi,tx_rssi,address,device_type from device")
        cursor.execute("select lower(replace(name,' ','_')) as name,device_id,rx_rssi,tx_rssi,address,device_type from device where address is not null")
        devicedict = cursor.fetchall()
        cursor.close()
        for (name, device_id, rx_rssi, tx_rssi,address,device_type) in devicedict:
            namearray = name.split('_',3)
            name1 = namearray[0]
            name2 = namearray[1]
            self.getChannel(name,device_id,rx_rssi,tx_rssi,address,device_type,name1,name2)

worker()
worker().getDevice()

####
####for deviceaddr in $(mysql -N ccu -u ccu --password=ccu -e 'select address from device where address is not null order by name')
####do
#####	mysql ccu -u ccu --password=ccu -e "select lower(replace(device.name,' ','_')) as devicename,     channel.address as channeladdress, device.address as deviceaddress,     datapoint.type,     replace(replace(replace(datapoint.value,'','0'),'false',0),'true',1) as value,     replace(device.rx_rssi,'NULL',-255),     device.tx_rssi,     datapoint.timestamp, datapoint.valuetype      from device,ise,channel,datapoint where device.device_id=ise.device_id And ise.channel_id=channel.channel_id And ise.datapoint_id=datapoint.datapoint_id and channel.visible<>0 AND device.address='$deviceaddr'"
#####mysql -N ccu -u ccu --password=ccu -e "select replace(channel.address,':','_') as channeladdress,  datapoint.type,     replace(replace(replace(datapoint.value,'','0'),'false',0),'true',1) as value,     replace(device.rx_rssi,'NULL',-255) as rx_rssi,replace(device.tx_rssi,'NULL',-120) as tx_rssi,     datapoint.timestamp, datapoint.valuetype      from device,ise,channel,datapoint where device.device_id=ise.device_id And ise.channel_id=channel.channel_id And ise.datapoint_id=datapoint.datapoint_id and channel.visible<>0 AND device.address='$deviceaddr'"
####	dn=$(mysql -N ccu -u ccu --password=ccu -e "select lower(replace(name,' ','_')) as devicename from device where address='$deviceaddr'")
####	echo "device is $dn $deviceaddr"
####	for channel in $(mysql -N ccu -u ccu --password=ccu -e "select channel.address from device,channel,ise where device.device_id=ise.device_id AND device.address='$deviceaddr'")
####	do
####		echo "got $channel"
####	done
####done
