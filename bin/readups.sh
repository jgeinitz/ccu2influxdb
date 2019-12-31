#!/bin/bash
#
UPSHOST='aeg@oldfield'
#
IFS='
'
#
RESULT="${UPSHOST},index=1 "
for i in $(upsc  $UPSHOST 2>/dev/null | grep -v driver |grep -v '^ups'|grep -v '^device')
do
	a=$(echo $i | awk -F: '{print $1 }' | tr '.' '-')
	b=$(echo $i | awk -F: '{print $2 }' | tr -d ' ')
	RESULT="${RESULT}${a}=${b},"
done

echo $RESULT | sed 's/,$//'
