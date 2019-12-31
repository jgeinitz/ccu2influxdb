#!/usr/bin/php
<?php
// Juergen Geinitz 2016
//
date_default_timezone_set( "Europe/Berlin" );
// helper to convert true/false to 1/0
function make_tf($val) {
	if ( $val == 'true' ) {
		return 1;
	}
	return $val;
}
$dbconection = mysqli_connect('localhost','ccu','ccu') or die('DB connect error: '. mysql_error() . "\n");
$database = mysqli_select_db($dbconection,'ccu') or die('cannot seelct database ccu\n');
#$statelist = simplexml_load_file('http://ccu2.dg9dw.ham-radio-op.net/config/xmlapi/devicelist.cgi');
echo("fetching xml data\n");
$statelist = simplexml_load_file('http://192.168.21.19/addons/xmlapi/devicelist.cgi');
// scan all homematic devices
echo("scanning devices on ccu\n");
foreach ( $statelist->device as $dev ) :
	echo("Device ".$dev[0]['name']."\n");
	$currentdev = $dev[0]['name'];
	$device_id = $dev[0]['ise_id'];
	$address = $dev[0]['address'];
	$interface = $dev[0]['interface'];
	$device_type = $dev[0]['device_type'];
	$ready_config = make_tf($dev[0]['ready_config']);
	$query = "SELECT count('device_id') AS cnt FROM device WHERE device_id = '". $device_id . "'";
	$result = mysqli_query($dbconection,$query) or die("select cnt error for device " . mysqli_error($database) . "\n");
	$row = mysqli_fetch_assoc($result);
	if ( $row['cnt'] == 0 ) {
		$query= "INSERT INTO device (device_id) VALUES (" . $device_id . ")";
		$result = mysql_query($database,$query) or die("insert primary key for $currentdev ($device_id) " . mysql_error() . "\n");
	}
	$query = "UPDATE LOW_PRIORITY device SET " .
		"name = '"		. $currentdev . "', " .
		"address = '"           . $address    . "', " .
		"interface = '"         . $interface  . "', " .
		"device_type = '"       . $device_type . "', ".
		"ready_config = '"      . $ready_config . "' ".
		"WHERE " .
		"device_id = " . $device_id ;
	$result = mysqli_query($dbconection,$query) or die("update device error " . mysql_error() . "\n");
	// scan all channels on this device
	foreach ( $dev[0]->channel as $chan ) :
		$currentchan = $chan[0]['name'];
		echo("\tchannel ".$currentchan."\n");
		$channel_id = $chan[0]['ise_id'];
		$type  = $chan[0]['type'];
		$address  = $chan[0]['address'];
		$interface  = $chan[0]['interface'];
		$direction  = $chan[0]['direction'];
		$channel_index  = $chan[0]['index'];
		$group_partner  = $chan[0]['group_partner'];
		$aes_available  = make_tf($chan[0]['aes_available']);
		$transmission_mode  = $chan[0]['transmission_mode'];
		$type  = $chan[0]['type'];
		$query = "SELECT count('channel_id') AS cnt FROM channel WHERE channel_id = '". $channel_id . "'";
		$result = mysqli_query($dbconection,$query) or die("select cnt error for channel " . mysql_error() . "\n");
		$row = mysqli_fetch_assoc($result);
		if ( $row['cnt'] == 0 ) {
			$query= "INSERT INTO channel (channel_id) VALUES (" . $channel_id . ")";
			$result = mysqli_query($dbconection,$query) or die("insert primary key for $currentchan ($channel_id) " . mysql_error() . "\n");
		}
		$query = "UPDATE LOW_PRIORITY channel SET " .
			"name = '"		. $currentchan . "', " .
			"type = '"		. $type		. "', ".
			"address = '"		. $address	. "', ".
			"direction = '"		. $direction 	. "', ".
			"channel_index = '"	. $channel_index ."', ".
			"group_partner = '"	. $group_partner ."', ".
			"aes_available = '"	. $aes_available ."', ".
			"transmission_mode = '"	. $transmission_mode . "' ".
			"WHERE " .
			"channel_id = " . $channel_id ;
		$result = mysqli_query($dbconection,$query) or die("update device error " . mysql_error() . "\n");
		//echo "XXX $currentdev $device_id $currentchan $channel_id $visible $operate\n";
	endforeach;
endforeach;

echo("done\n");
