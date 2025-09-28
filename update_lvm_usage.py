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


def run_cmd(cmd):
    try:
        out = subprocess.check_output(
            cmd,
            stderr=subprocess.DEVNULL,
            shell=False,
            timeout=30
        )
        return json.loads(out)
    except Exception as e:
        print(f"ERROR: failed to run {' '.join(cmd)}: {e}", file=sys.stderr)
        sys.exit(1)


def get_lvs():
    data = run_cmd(["/sbin/lvs", "--reportformat", "json", "--units", "m"])
    return data['report'][0]['lv']


def get_vgs():
    data = run_cmd(["/sbin/vgs", "--reportformat", "json", "--units", "m"])
    return data['report'][0]['vg']


def main():
    dirname = os.path.dirname(filename)
    os.makedirs(dirname, exist_ok=True)

    lvs = get_lvs()
    vgs = get_vgs()

    with open(filename, "w") as fh:
        # LV metrics
        print('# HELP lvm_volume_size Size of LVM logical volume in MB', file=fh)
        print('# TYPE lvm_volume_size gauge', file=fh)
        print('# HELP lvm_volume_usage_percent Percent usage of LVM logical volume', file=fh)
        print('# TYPE lvm_volume_usage_percent gauge', file=fh)
        print('# HELP lvm_volume_usage_megabytes Usage of LVM logical volume in MB', file=fh)
        print('# TYPE lvm_volume_usage_megabytes gauge', file=fh)
        print('# HELP lvm_volume_is_thin Whether the LVM volume is thin-provisioned (1=yes, 0=no)', file=fh)
        print('# TYPE lvm_volume_is_thin gauge', file=fh)

        for i in lvs:
            lv_name = i.get("lv_name", "unknown")
            pool_lv = i.get("pool_lv", "")
            vg_name = i.get("vg_name", "")

            try:
                lv_size = float(i["lv_size"].rstrip("m"))
            except (KeyError, ValueError):
                continue

            data_percent = i.get("data_percent")

            if not data_percent:
                usage_mb = lv_size
                data_percent = 100.0
                is_thin = 0
            else:
                try:
                    data_percent = float(data_percent)
                except ValueError:
                    data_percent = 100.0
                usage_mb = lv_size * data_percent / 100
                is_thin = 1

            print(f'lvm_volume_size{{lv_name="{lv_name}",pool_lv="{pool_lv}",vg_name="{vg_name}"}} {lv_size}', file=fh)
            print(f'lvm_volume_usage_percent{{lv_name="{lv_name}",pool_lv="{pool_lv}",vg_name="{vg_name}"}} {data_percent}', file=fh)
            print(f'lvm_volume_usage_megabytes{{lv_name="{lv_name}",pool_lv="{pool_lv}",vg_name="{vg_name}"}} {usage_mb}', file=fh)
            print(f'lvm_volume_is_thin{{lv_name="{lv_name}",pool_lv="{pool_lv}",vg_name="{vg_name}"}} {is_thin}', file=fh)

        # VG metrics
        print('# HELP lvm_vg_size Size of LVM volume group in MB', file=fh)
        print('# TYPE lvm_vg_size gauge', file=fh)
        print('# HELP lvm_vg_free Free space of LVM volume group in MB', file=fh)
        print('# TYPE lvm_vg_free gauge', file=fh)
        print('# HELP lvm_vg_usage_percent Percent used of LVM volume group', file=fh)
        print('# TYPE lvm_vg_usage_percent gauge', file=fh)
        print('# HELP lvm_vg_usage_megabytes Used space of LVM volume group in MB', file=fh)
        print('# TYPE lvm_vg_usage_megabytes gauge', file=fh)

        for vg in vgs:
            vg_name = vg.get("vg_name", "unknown")

            try:
                vg_size = float(vg["vg_size"].rstrip("m"))
                vg_free = float(vg["vg_free"].rstrip("m"))
            except (KeyError, ValueError):
                continue

            vg_used = vg_size - vg_free
            usage_percent = (vg_used / vg_size * 100) if vg_size > 0 else 0.0

            print(f'lvm_vg_size{{vg_name="{vg_name}"}} {vg_size}', file=fh)
            print(f'lvm_vg_free{{vg_name="{vg_name}"}} {vg_free}', file=fh)
            print(f'lvm_vg_usage_megabytes{{vg_name="{vg_name}"}} {vg_used}', file=fh)
            print(f'lvm_vg_usage_percent{{vg_name="{vg_name}"}} {usage_percent}', file=fh)


if __name__ == "__main__":
    main()
    sys.exit(0)
