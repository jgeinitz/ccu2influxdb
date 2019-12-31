#!/bin/bash
mysql ccu -u ccu --password=ccu -e 'select name,address from device order by name'

