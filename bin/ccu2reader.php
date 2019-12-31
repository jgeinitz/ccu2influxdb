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
$dbc = mysqli_connect('localhost','ccu','ccu') or die('DB connect error: '. mysqli_connect_error() . "\n");
$database = mysqli_select_db($dbc,'ccu') or die('cannot seelct database ccu\n');
#$statelist = simplexml_load_file('http://ccu2.dg9dw.ham-radio-op.net/config/xmlapi/statelist.cgi');
echo("fetching xml data\n");
$statelist = simplexml_load_file('http://192.168.21.19/addons/xmlapi/statelist.cgi');
// scan all homematic devices
echo("scanning devices on ccu\n");
foreach ( $statelist->device as $dev ) :
	echo("Device ".$dev[0]['name']."\n");
	$currentdev = $dev[0]['name'];
	$device_id = $dev[0]['ise_id'];
	$unreach = make_tf($dev[0]['unreach']);
	$sticky_unreach = make_tf($dev[0]['sticky_unreach']);
	$config_pending = make_tf($dev[0]['config_pendig']);
	$query = "SELECT count('device_id') AS cnt FROM device WHERE device_id = '". $device_id . "'";
	$result = mysqli_query($dbc,$query) or die("select cnt error for device " . mysqli_error($dbc) . "\n");
	$row = mysqli_fetch_assoc($result);
	if ( $row['cnt'] == 0 ) {
		$query= "INSERT INTO device (device_id) VALUES (" . $device_id . ")";
		$result = mysqli_query($dbc,$query) or die("insert primary key for $currentdev ($device_id) " . mysqli_error($dbc) . "\n");
	}
	$query = "UPDATE LOW_PRIORITY device SET " .
		"name = '"		. $currentdev . "', " .
		"unreach = '"		. $unreach . "', " .
		"sticky_unreach = '"	. $sticky_unreach . "', " .
		"config_pending = '"	. $config_pending . "' " .
		"WHERE " .
		"device_id = " . $device_id ;
	$result = mysqli_query($dbc,$query) or die("update device error " . mysqli_error($dbc) . "\n");
	// scan all channels on this device
	foreach ( $dev[0]->channel as $chan ) :
		$currentchan = $chan[0]['name'];
		echo("\tchannel ".$currentchan."\n");
		$channel_id = $chan[0]['ise_id'];
		$visible = make_tf($chan[0]['visible']);
		$operate = make_tf($chan[0]['operate']);
		$indx	 = make_tf($chan[0]['index']);
		$query = "SELECT count('channel_id') AS cnt FROM channel WHERE channel_id = '". $channel_id . "'";
		$result = mysqli_query($dbc,$query) or die("select cnt error for channel " . mysqli_error($dbc) . "\n");
		$row = mysqli_fetch_assoc($result);
		if ( $row['cnt'] == 0 ) {
			$query= "INSERT INTO channel (channel_id) VALUES (" . $channel_id . ")";
			$result = mysqli_query($dbc,$query) or die("insert primary key for $currentchan ($channel_id) " . mysqli_error($dbc) . "\n");
		}
		$query = "UPDATE LOW_PRIORITY channel SET " .
			"name = '"		. $currentchan . "', " .
			"indx = '"		. $indx . "', " .
			"visible = '"		. $visible . "', ".
			"operate = '"		. $operate . "' ".
			"WHERE " .
			"channel_id = " . $channel_id ;
		$result = mysqli_query($dbc,$query) or die("update device error " . mysqli_error($dbc) . "\n");
		//echo "XXX $currentdev $device_id $currentchan $channel_id $visible $operate\n";
		// finally loop over every datapoint of the current channel of the current device
		foreach ( $chan[0]->datapoint as $dp ) :
			$dataval = '';
			$valuetype = '';
			$valueunit = '';
			$tims = 0;
			$op = 0;
			$dataname = $dp[0]['name'];
			$datatype = $dp[0]['type'];
			$dataid = $dp[0]['ise_id'];
			$dataval = $dp[0]['value'];
			$valuetype = $dp[0]['valuetype'];
			$valueunit = $dp[0]['valueunit'];
			$tz = new DateTimeZone("Europe/Berlin");
			$x = DateTime::createFromFormat('U', $dp[0]['timestamp'],$tz);
			$y = $tz->getOffset($x);
			$x = DateTime::createFromFormat('U', $dp[0]['timestamp'] + $y,$tz );
			$tims = $x->format('Y-m-d H:i:s');
			$op = $dp[0]['operations'];
			$query = "SELECT count('datapoint_id') AS cnt FROM datapoint WHERE datapoint_id = '". $dataid . "'";
			$result = mysqli_query($dbc,$query) or die("select cnt error for datapoint " . mysqli_error($dbc) . "\n");
			$row = mysqli_fetch_assoc($result);
			if ( $row['cnt'] == 0 ) {
				$query= "INSERT INTO datapoint (datapoint_id) VALUES (" . $dataid . ")";
				$result = mysqli_query($dbc,$query) or die("insert primary key for $dataname ($datais) " . mysqli_error($dbc) . "\n");
			}
			$query = "UPDATE datapoint SET " .
				"name = '"		. $dataname . "', " .
				"type = '"		. $datatype . "', " .
				"value = '"		. $dataval . "', ".
				"valuetype = '"		. $valuetype . "', ".
				"valueunit = '"		. $valueunit . "', ".
				"timestamp = '"		. $tims . "', ".
				"operation = '"		. $op . "' ".
				"WHERE " .
				"datapoint_id = " . $dataid ;
			$result = mysqli_query($dbc,$query) or die("update device error " . mysqli_error($dbc) . "\n");
			$query = "SELECT count('datapoint_id') AS cnt FROM ise WHERE datapoint_id = '". $dataid . "'";
			$result = mysqli_query($dbc,$query) or die("select cnt error for datapoint in ise " . mysqli_error($dbc) . "\n");
			$row = mysqli_fetch_assoc($result);
			if ( $row['cnt'] == 0 ) {
				$query= "INSERT INTO ise (datapoint_id) VALUES (" . $dataid . ")";
				$result = mysqli_query($dbc,$query) or die("insert ise_id record for $dataid '" . mysqli_error($dbc) . "'\n");
			}
			$query = "UPDATE ise SET " .
				"channel_id = '"		. $channel_id . "', " .
				"device_id = '"			. $device_id . "' ".
				"WHERE " .
				"datapoint_id = " . $dataid ;
			$result = mysqli_query($dbc,$query) or die("update device error " . mysqli_error($dbc) . "\n");
			//echo "yyy $device_id $channel_id $dataid $dataname $datatype $dataval $valuetype $valueunit $times $op\n";
			//echo "- $dataid - $query \n";
		endforeach;
	endforeach;
endforeach;
echo("fetching xml data for RSSIs\n");
$rssilist = simplexml_load_file('http://192.168.21.19/addons/xmlapi/rssilist.cgi');
#$rssilist = simplexml_load_file('http://ccu2.dg9dw.ham-radio-op.net/config/xmlapi/rssilist.cgi');
foreach ( $rssilist->rssi as $list ) :
	$device = $list[0]['device'];
	echo("Device ".$device."\n");
	$rx = $list[0]['rx'];
	$tx = $list[0]['tx'];
	if ( $rx == 65536 )
		$rx = -120;
	if ( $tx == 65536 )
		$tx = -120;
	$query = "SELECT count('device_id') AS cnt, device_id FROM device WHERE name like '%". $device . "'";
        $result = mysqli_query($dbc,$query) or die("select cnt error for device " . mysqli_error($dbc) . "\n");
        $row = mysqli_fetch_assoc($result);
        if ( $row['cnt'] != 0 ) {
		$deviceid = $row['device_id'];
        	$query = "UPDATE LOW_PRIORITY device SET " .
                	"rx_rssi = '"              . $rx . "', " .
                	"tx_rssi = '"           . $tx . "' " .
                	"WHERE " .
                	"device_id = " . $deviceid ;
        	$result = mysqli_query($dbc,$query) or die("update device error " . mysqli_error($dbc) . "\n");
	}
endforeach;

echo("done\n");
