<?php
/**
 * Fritz!Box PHP tools CLI script to fetch dsl data
 *
 * Must be called via a command line, shows a help message if called without any or an invalid argument
 *
 * Check the config file fritzbox.conf.php!
 * 
 * @author   juergen
 * @author   Gregor Nathanael Meyer <Gregor [at] der-meyer.de>
 * @license  http://creativecommons.org/licenses/by-sa/3.0/de/ Creative Commons cc-by-sa
 * @version  0.3 2013-01-02
 * @package  Fritz!Box PHP tools
 */

try
{
  // load the fritzbox_api class
  require_once('fritzbox_api.class.php');
  $fritz = new fritzbox_api();
  
  // init the output message
  $message = date('Y-m-d H:i') . ' ';

  // read the current settings
  $formfields = array(
    'getpage' => '/internet/dsl_stats_tab.lua'
  );
  $output = $fritz->doGetRequest($formfields);
echo $output . "lj\n";  
  // read down_time_activ setting
//jhg  preg_match('@name="down_time_activ"[^>]+(checked)[^>]*@', $output, $matches);
  //jhgif ( isset($matches[1]) )
  //jhg{
    //jhg$formfields['down_time_activ'] = 'on';
  //jhg}
  // read down_time_value setting
  //jhgpreg_match('@name="down_time_value".*?<option value="(\d+)"[^>]+?selected.*?</select>@s', $output, $matches);
  //jhg$formfields['down_time_value'] = isset($matches[1]) ? $matches[1] : '15';
  // read disconnect_guest_access setting
  //jhgpreg_match('@name="disconnect_guest_access"[^>]+(checked)[^>]*@', $output, $matches);
  //jhgif ( isset($matches[1]) )
  //jhg{
    //jhg$formfields['disconnect_guest_access'] = 'on';
  //jhg}
  //jhg// read guest_ssid setting
  //jhgpreg_match('@name="guest_ssid"[^>]+value="([^"]*)"[^>]*@', $output, $matches);
  //jhg$formfields['guest_ssid'] = isset($matches[1]) ? $matches[1] : 'defaultguestaccess';
  //jhg// read wlan_security setting
  //jhgpreg_match('@name="wlan_security"[^>]+value="([^"])"[^>]+checked[^>]*@', $output, $matches);
  //jhg$formfields['wlan_security'] = isset($matches[1]) ? $matches[1] : '15';
  //jhg// read wpa_key setting
  //jhgpreg_match('@name="wpa_key"[^>]+value="([^"]*)"[^>]*@', $output, $matches);
  //jhg$formfields['wpa_key'] = isset($matches[1]) ? $matches[1] : 'defaultwpakey';
  //jhg// read wpa_modus setting
  //jhgpreg_match('@name="wpa_modus".*?<option value="(\d+)"[^>]+?selected.*?</select>@s', $output, $matches);
  //jhg$formfields['wpa_modus'] = isset($matches[1]) ? $matches[1] : 'x';
  
  // set new given setting
  //jhgif ( $mode == true )
  //jhg{
    //jhg$formfields['activate_guest_access'] = 'on';
    //jhgif ( $wpa_key !== false )
    //jhg{
      //jhg$formfields['wpa_key'] = $wpa_key;
    //jhg}
  //jhg}
  
  // do the update
  //jhg$formfields['btnSave'] = '';
  //jhg$output = $fritz->doPostForm($formfields);
//jhg
  //jhgpreg_match('@name="activate_guest_access"[^>]+(checked)[^>]*@', $output, $matches);
  //jhgif ( isset($matches[1]) && $mode == true )
  //jhg{
		//jhgpreg_match('@name="wpa_key"[^>]+value="([^"]*)"[^>]*@', $output, $matches);
		//jhgif ( isset($matches[1]) )
		//jhg{
			//jhg$message .= 'WLAN guest access is now active. WPA-Key is "' . $matches[1] . '"';
		//jhg}
  //jhg}
  //jhgelse if ( !isset($matches[1]) && $mode == false )
  //jhg{
    //jhg$message .= 'WLAN guest access is now inactive.';
  //jhg}
  //jhgelse if ( isset($matches[1]) && $mode == false )
  //jhg{
    //jhg$message .= 'ERROR: WLAN guest access status change failed, should be inactive, but is still active.';
  //jhg}
  //jhgelse if ( !isset($matches[1]) && $mode == true )
  //jhg{
    //jhg$message .= 'ERROR: WLAN guest access status change failed, should be active, but is still inactive.';
  //jhg}
}
catch (Exception $e)
{
  $message .= $e->getMessage();
}

// log the result
if ( isset($fritz) && is_object($fritz) && get_class($fritz) == 'fritzbox_api' )
{
  $fritz->logMessage($message);
}
else
{
  echo($message);
}
$fritz = null; // destroy the object to log out
?>
