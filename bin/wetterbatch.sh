#!/bin/sh
(
#curl -s 'http://api.openweathermap.org/data/2.5/weather?q=nauheim,de&appid=36b95a935eea3f315c00a7011581106d&units=metric' >>/dev/null
sleep 4
curl -s 'http://api.openweathermap.org/data/2.5/weather?q=nauheim,de&appid=36b95a935eea3f315c00a7011581106d&units=metric' )  > /disk/tmp/wetterreport
