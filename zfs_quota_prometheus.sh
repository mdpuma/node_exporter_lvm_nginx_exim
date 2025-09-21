#!/bin/bash

# Output file for Prometheus node_exporter textfile collector
OUTFILE="/tmp/node_exporter/zfs_quota.prom"

# Temp file to avoid partial writes
TMPFILE=$(mktemp)

# Prometheus format requires HELP and TYPE once per metric
echo "# HELP zfs_user_quota_bytes ZFS user quota limit in bytes" >> "$TMPFILE"
echo "# TYPE zfs_user_quota_bytes gauge" >> "$TMPFILE"
echo "# HELP zfs_user_used_bytes ZFS user used space in bytes" >> "$TMPFILE"
echo "# TYPE zfs_user_used_bytes gauge" >> "$TMPFILE"

# Loop through datasets with quotas
for dataset in $(zfs list -H -o name); do
    # Get per-user quota and usage
    /usr/sbin/zfs userspace -H -o name,quota,used "$dataset" 2>/dev/null | while read -r user quota used; do
        # skip "root" and "-" placeholders
        [[ "$user" == "-" ]] && continue

        # Convert values to bytes
        quota_bytes=$(numfmt --from=iec "$quota" 2>/dev/null || echo 0)
        used_bytes=$(numfmt --from=iec "$used" 2>/dev/null || echo 0)

        # Export with labels dataset and user
        echo "zfs_user_quota_bytes{dataset=\"$dataset\",user=\"$user\"} $quota_bytes" >> "$TMPFILE"
        echo "zfs_user_used_bytes{dataset=\"$dataset\",user=\"$user\"} $used_bytes" >> "$TMPFILE"
    done
done

# Atomic move
mv "$TMPFILE" "$OUTFILE"
chmod 644 "$OUTFILE"

