#!/usr/bin/php
<?php
//
//
$dEbug=0;
if ( empty($_SERVER["argv"][1]) ) {
	echo "usage: Program Homematicdevice Datepoint\n";
	exit(1);
}
if ( empty($_SERVER["argv"][2]) ) {
	$point="";
} else {
	$point = $_SERVER["argv"][2];
}

date_default_timezone_set( "Europe/Berlin" );
$dbconection = mysqli_connect('localhost','ccu','ccu') or die('Verbindungsfehler: '. mysqli_connect_error() . "\n");
$database = mysqli_select_db($dbconection,'ccu') or die('Kann Datenbank nicht auswählen\n');
//
$query = "SELECT device.name as devname ,
		device.device_id as deviceid,
		datapoint.name as fullname,
		datapoint.type, 
		datapoint.value, 
		datapoint.timestamp,
		unix_timestamp(convert_tz(datapoint.timestamp,'Europe/Berlin', 'UTC')) as timest, 
		device.tx_rssi as tx_rssi, 
		device.rx_rssi as rx_rssi ".
	 "FROM ise,datapoint,device " .
	 "WHERE device.name LIKE '%".$_SERVER["argv"][1]."%' ".
	 "AND datapoint.name LIKE '%".$point ."' ".
	 "AND device.device_id = ise.device_id ".
	 "AND datapoint.datapoint_id = ise.datapoint_id ".
	 "ORDER BY datapoint.timestamp,type";
if ( $dEbug != 0 ) {
	echo "DBG:".$query.":\n";
}
$res = mysqli_query($dbconection,$query);
if ( !$res )
{
	die("SELECT ERROR " . mysqli_error($dbconection));
}

$timest=0;
while ( $row = mysqli_fetch_assoc($res) ) {
	$v = $row['value'];
	$t = preg_replace("/(.+):(.+)\.(.+)/","$3_$2",strtolower($row['fullname']));
	if ( $v == 'false' ) { $v = 0; }
	elseif ( $v == 'true' ) { $v = 1; }
	elseif ( $v == '' ) { $v = "NULL"; }
	$timest = $row['timest'];
//	if ( $t == "state" ) {
//		if ( $v == 1 ) { $v = -1; }
//		elseif ( $v == 2 ) { $v = 1; }
//	}
	echo " $t:$v";
}

echo " timestamp:$timest\n";
?>
