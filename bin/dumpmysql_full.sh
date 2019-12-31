#!/bin/bash
DAT=`TZ=UTC date '+%Y%m%d_%X'`
TARGET=/disk/stick/mysqldump
mysqldump   --defaults-file=/etc/mysql/debian.cnf --all-databases -Y --events > ${TARGET}/mysql_dump_$DAT
gzip -9 ${TARGET}/mysql_dump_$DAT
cd ${TARGET}
fil1=`ls -tr | tail -2| head -1`
fil2=`ls -tr | tail -1`
if [ $fil1 != $fil2 ]
then
  x1=`ls -l $fil1 | awk '{ print $5 }'`
  x2=`ls -l $fil2 | awk '{ print $5 }'`
  if [ "$x1" = "$x2" ]
  then
    /bin/rm $fil1
  fi
fi
cnt=`ls -1 mysql_dump* | wc -l`
while [ $cnt -gt 10 ]
do
  x=`ls -1rt mysql_dump* | head -1`
  /bin/rm $x
  cnt=`ls -1 mysql_dump*| wc -l`
done
exit 0
