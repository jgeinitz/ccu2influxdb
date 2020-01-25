#!/bin/sh
#
need_restart=0
#
telegrafpid=/var/run/telegraf/telegraf.pid
if [ ! -f ${telegrafpid} ]
then
	need_restart=1
else
	rc=$(kill -0 $(cat $telegrafpid) 2>/dev/null; echo $?)
	if [ "x${rc}" != "x0" ]
	then
		need_restart=1
	fi
fi
if [ $need_restart -ne 0  ]
then
	/bin/rm $telegrafpid 2>/dev/null
	/usr/lib/telegraf/scripts/init.sh restart 2>&1 >/dev/null
fi
