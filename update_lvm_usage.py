#!/usr/bin/env python3

# apt install python3 python3-pip
#
# crontab line 
# 30 * * * * /root/update_lvm_usage.py 
#
# --collector.textfile.directory=/tmp/node_exporter

import json
import subprocess
import sys
import os

filename = '/tmp/node_exporter/lvm_usage.prom'

out = None
err = None
out = subprocess.check_output(["lvs", "--reportformat", "json", "--units", "m"], stderr=err, shell=False, timeout=30)

json_arr = json.loads(out)
json_arr = json_arr['report'][0]['lv']


dirname = os.path.dirname(filename)
if os.path.isdir(dirname) != True:
	os.mkdir(dirname)
	
fh = open(filename, mode='wt')
for i in json_arr:
	## HELP node_zfs_zil_zil_commit_count kstat.zfs.misc.zil.zil_commit_count
	## TYPE node_zfs_zil_zil_commit_count untyped
	#node_zfs_zil_zil_commit_count 0
	lv_name = i.get('lv_name')
	pool_lv = i.get('pool_lv')
	data_percent = i.get('data_percent')
	
	# convert to mbytes
	lv_size = float(i.get('lv_size').replace('m', ''))
	is_thin_lvm=0
	
	if data_percent == None or not data_percent:
		usage_mb = lv_size
		data_percent = '100'
	else:
		usage_mb = float(lv_size) * float(data_percent) / 100
		is_thin_lvm=1
	
	lv_size = str(lv_size)
	usage_mb = str(usage_mb)
	is_thin_lvm = str(is_thin_lvm)
	
	
	print('lvm_volume_size{lv_name="'+lv_name+'",pool_lv="'+pool_lv+'"} '+lv_size, file=fh)
	print('lvm_volume_usage_percent{lv_name="'+lv_name+'",pool_lv="'+pool_lv+'",is_thin="'+is_thin_lvm+'",lv_size="'+lv_size+'"} '+data_percent, file=fh)
	print('lvm_volume_usage_megabytes{lv_name="'+lv_name+'",pool_lv="'+pool_lv+'", lv_size="'+lv_size+'"} '+usage_mb, file=fh)
	
fh.close()
sys.exit(0)
