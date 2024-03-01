#!/usr/bin/env python3

# apt install python3
#
# crontab line 
# */1 * * * * /root/update_pmacct.py
#
# --collector.textfile.directory=/tmp/node_exporter

import re
import subprocess
import json
import os
import sys


filename = '/tmp/node_exporter/pmacctd.prom'

dirname = os.path.dirname(filename)
if os.path.isdir(dirname) != True:
	os.mkdir(dirname)

fh = open(filename, mode='wt')

# process incoming
p = subprocess.Popen('/usr/local/bin/pmacct -p /tmp/pmacct_in.pipe -s -O json', stdout=subprocess.PIPE, shell=True)
out, err = p.communicate()

out=out.decode('utf-8').split("\n")
for i in out:
	if len(i)>0:
		j = json.loads(str(i))
		print('pmacct_packets{source="pve-antiddos-md", mac_src="'+j['mac_src']+'", net_dst="'+j['net_dst']+'", direction="in"} '+str(j['packets']), file=fh)
		print('pmacct_bytes{source="pve-antiddos-md", mac_src="'+j['mac_src']+'", net_dst="'+j['net_dst']+'", direction="in"} '+str(j['bytes']), file=fh)

# process outgoing
p = subprocess.Popen('/usr/local/bin/pmacct -p /tmp/pmacct_out.pipe -s -O json', stdout=subprocess.PIPE, shell=True)
out, err = p.communicate()

out=out.decode('utf-8').split("\n")
for i in out:
	if len(i)>0:
		j = json.loads(str(i))
		print('pmacct_packets{source="pve-antiddos-md", mac_dst="'+j['mac_dst']+'", net_src="'+j['net_src']+'", direction="out"} '+str(j['packets']), file=fh)
		print('pmacct_bytes{source="pve-antiddos-md", mac_dst="'+j['mac_dst']+'", net_src="'+j['net_src']+'", direction="out"} '+str(j['bytes']), file=fh)

fh.close()
sys.exit(0)
