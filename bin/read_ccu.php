#!/usr/bin/php
<?php
//
//
if ( empty($_SERVER["argv"][1]) ) {
	echo "usage: Program Homematicdevice\n";
	exit(1);
}
date_default_timezone_set( "Europe/Berlin" );
$dbconection = mysqli_connect('localhost','ccu','ccu') or die('Verbindungsfehler: '. mysqli_connect_error() . "\n");
$database = mysqli_select_db($dbconection,'ccu') or die('Kann Datenbank nicht auswählen\n');
//
$query = "SELECT device.name as devname ,
		device.address as address,
		datapoint.name as fullname,
		datapoint.type, 
		datapoint.value, 
		datapoint.timestamp,
		unix_timestamp(convert_tz(datapoint.timestamp,'Europe/Berlin', 'UTC')) as timest, 
		device.tx_rssi as tx_rssi, 
		device.rx_rssi as rx_rssi ".
	 "FROM ise,datapoint,device " .
	 "WHERE device.name LIKE '".$_SERVER["argv"][1]."%' ".
	 "AND device.device_id = ise.device_id ".
	 "AND datapoint.datapoint_id = ise.datapoint_id ".
	 "ORDER BY datapoint.timestamp,type";

$res = mysqli_query($dbconection,$query);
if ( !$res )
{
	die("SELECT ERROR " . mysqli_error($dbconection));
}

$hasdev=0;
$timest=0;
while ( $row = mysqli_fetch_assoc($res) ) {
	$v = $row['value'];
	$t = preg_replace("/(.+):(.+)\.(.+)/","$3_$2_$1",strtolower($row['fullname']));
	if ( $v == 'false' ) { $v = 0; }
	elseif ( $v == 'true' ) { $v = 1; }
	elseif ( $v == '' ) { $v = "NULL"; }
	$timest = $row['timest'];
//	if ( $t == "state" ) {
//		if ( $v == 1 ) { $v = -1; }
//		elseif ( $v == 2 ) { $v = 1; }
//	}
	if ( $hasdev == 0 ) {
		$hasdev = 1;
		echo "devicename:".$row['devname']." ";
		echo "address:".$row['address']." ";
		$rssi=-121;
		if ( $row['tx_rssi'] == -120 ) {
			$rssi = $row['rx_rssi'];
		} else {
			$rssi = $row['tx_rssi'];
		}
		if ( $rssi == "" ) { $rssi = -122; }
		echo "rssi_value:".$rssi;
	}
	echo " $t:$v";
}

echo " timestamp:$timest\n";
?>
