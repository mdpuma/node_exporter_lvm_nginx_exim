#!/usr/bin/env python2

# apt install python3 python3-pip
#
# crontab line 
# 30 * * * * /root/update_mailqueue_nginx.py 
#
# --collector.textfile.directory=/tmp/node_exporter


from __future__ import print_function
import json
import subprocess
import sys
import os
import re
import resource

resource.setrlimit(resource.RLIMIT_NOFILE, (10000,10000))

filename = '/tmp/node_exporter/exim_queue.prom'

dirname = os.path.dirname(filename)
if os.path.isdir(dirname) != True:
	os.mkdir(dirname)

out = None
err = None

# timeout=30

out = subprocess.check_output(["/usr/sbin/exiqgrep", "-bzc"], stderr=err, shell=False)

test1 = re.match("^([0-9]+) matches out of ([0-9]+) messages", out)
if test1:
	frozen_messages = test1.group(1)
	total_messages = test1.group(2)

out = subprocess.check_output(["/usr/sbin/exiqgrep", "-bxc"], stderr=err, shell=False)

test1 = re.match("^([0-9]+) matches out of ([0-9]+) messages", out)
if test1:
	nonfrozen_messages = test1.group(1)
	total_messages = test1.group(2)


fh = open(filename, mode='wt')

print('exim_queue{status="frozen"} '+frozen_messages, file=fh)
print('exim_queue{status="nonfrozen"} '+nonfrozen_messages, file=fh)
print('exim_queue{status="total"} '+total_messages, file=fh)

fh.close()



filename = '/tmp/node_exporter/nginx_testconfig.prom'

try:
	out = subprocess.check_output(["/usr/sbin/nginx", "-t"], stderr=subprocess.STDOUT, shell=False)
except subprocess.CalledProcessError as e:
	print(e.output, sep=' ', end='\n', file=sys.stderr)

fh = open(filename, mode='wt')

try:
	print('nginx_exitstatus '+str(e.returncode), file=fh)
except:
	print('nginx_exitstatus 0', file=fh)
	
fh.close()

sys.exit(0)
